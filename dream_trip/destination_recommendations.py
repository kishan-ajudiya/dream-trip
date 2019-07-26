#!/usr/bin/env python
# coding: utf-8

# In[3]:


# !/usr/bin/env python
# coding: utf-8

# In[1]:


# !pip install lightfm
# !pip install recsys


# In[125]:


import numpy as np
import pandas as pd
from array import array
from lightfm import *
from lightfm.data import Dataset
from django.conf import settings
# Importing Libraries and cookbooks
from recsys import *  ## recommender system cookbook
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity


# from IPython.display import HTML ## Setting display options for Ipython Notebook


def create_interaction_matrix(df, user_col, item_col, rating_col, norm=False, threshold=None):
    """
    Function to create an interaction matrix dataframe from transactional type interactions
    Required Input -
        - df = Pandas DataFrame containing user-item interactions
        - user_col = column name containing user's identifier
        - item_col = column name containing item's identifier
        - rating col = column name containing user feedback on interaction with a given item
        - norm (optional) = True if a normalization of ratings is needed
        - threshold (required if norm = True) = value above which the rating is favorable
    Expected output -
        - Pandas dataframe with user-item interactions ready to be fed in a recommendation algorithm
    """
    interactions = df.groupby([user_col, item_col])[rating_col].sum().unstack().reset_index().fillna(0).set_index(
        user_col)
    if norm:
        interactions = interactions.applymap(lambda x: 1 if x > threshold else 0)
    return interactions


def create_user_dict(interactions):
    """
    Function to create a user dictionary based on their index and number in interaction dataset
    Required Input -
        interactions - dataset create by create_interaction_matrix
    Expected Output -
        user_dict - Dictionary type output containing interaction_index as key and user_id as value
    """
    user_id = list(interactions.index)
    user_dict = {}
    counter = 0
    for i in user_id:
        user_dict[i] = counter
        counter += 1
    return user_dict


def create_item_dict(df, id_col, name_col, average_stay, lat, long, category, image_url, voyager_id):
    """
    Function to create an item dictionary based on their item_id and item name
    Required Input -
        - df = Pandas dataframe with Item information
        - id_col = Column name containing unique identifier for an item
        - name_col = Column name containing name of the item
    Expected Output -
        item_dict = Dictionary type output containing item_id as key and item_name as value
    """
    item_dict = {}
    all_records = {}
    df = df.fillna('')
    for i in range(df.shape[0]):
        item_dict[(df.loc[i, id_col])] = df.loc[i, name_col]
        all_records[(df.loc[i, id_col])] = {'destination_name': df.loc[i, name_col],
                                            'average_stay': df.loc[i, average_stay],
                                            'lat': df.loc[i, lat], 'long': df.loc[i, long],
                                            'category': df.loc[i, category],
                                            'image_url': df.loc[i, image_url], 'voyager_id': df.loc[i, voyager_id]}
    return item_dict, all_records


def runMF(interactions, item_features, user_features=None, n_components=30, loss='warp', k=15, epoch=30, n_jobs=4):
    """
    Function to run matrix-factorization algorithm
    Required Input -
        - interactions = dataset create by create_interaction_matrix
        - n_components = number of embeddings you want to create to define Item and user
        - loss = loss function other options are logistic, brp
        - epoch = number of epochs to run
        - n_jobs = number of cores used for execution
    Expected Output  -
        Model - Trained model
    """
    x = sparse.csr_matrix(interactions.values)
    model = LightFM(no_components=n_components, loss=loss, k=k)
    model.fit(x, item_features=item_features, user_features=user_features, epochs=epoch, num_threads=n_jobs)
    return model


def sample_recommendation_user(model, interactions, user_id, user_dict,
                               item_dict, threshold=0, nrec_items=10, show=False):
    """
    Function to produce user recommendations
    Required Input -
        - model = Trained matrix factorization model
        - interactions = dataset used for training the model
        - user_id = user ID for which we need to generate recommendation
        - user_dict = Dictionary type input containing interaction_index as key and user_id as value
        - item_dict = Dictionary type input containing item_id as key and item_name as value
        - threshold = value above which the rating is favorable in new interaction matrix
        - nrec_items = Number of output recommendation needed
    Expected Output -
        - Prints list of items the given user has already bought
        - Prints list of N recommended items  which user hopefully will be interested in
    """
    n_users, n_items = interactions.shape
    user_x = user_dict[user_id]
    scores = pd.Series(model.predict(user_x, np.arange(n_items)))
    scores.index = interactions.columns
    scores = list(pd.Series(scores.sort_values(ascending=False).index))

    known_items = list(
        pd.Series(interactions.loc[user_id, :][interactions.loc[user_id, :] > threshold].index).sort_values(
            ascending=False))

    scores = [x for x in scores if x not in known_items]
    return_score_list = scores[0:nrec_items]
    known_items = list(pd.Series(known_items).apply(lambda x: item_dict[x]))
    scores = list(pd.Series(return_score_list).apply(lambda x: item_dict[x]))
    if show == True:
        print("Known Likes:")
        counter = 1
        for i in known_items:
            print(str(counter) + '- ' + i)
            counter += 1

        print("\n Recommended Items:")
        counter = 1
        for i in scores:
            print(str(counter) + '- ' + i)
            counter += 1
    return return_score_list


def sample_recommendation_item(model, interactions, item_id, user_dict, item_dict, number_of_user):
    """
    Funnction to produce a list of top N interested users for a given item
    Required Input -
        - model = Trained matrix factorization model
        - interactions = dataset used for training the model
        - item_id = item ID for which we need to generate recommended users
        - user_dict =  Dictionary type input containing interaction_index as key and user_id as value
        - item_dict = Dictionary type input containing item_id as key and item_name as value
        - number_of_user = Number of users needed as an output
    Expected Output -
        - user_list = List of recommended users
    """
    n_users, n_items = interactions.shape
    x = np.array(interactions.columns)
    scores = pd.Series(model.predict(np.arange(n_users), np.repeat(x.searchsorted(item_id), n_users)))
    user_list = list(interactions.index[scores.sort_values(ascending=False).head(number_of_user).index])
    return user_list


def create_item_emdedding_distance_matrix(model, interactions):
    """
    Function to create item-item distance embedding matrix
    Required Input -
        - model = Trained matrix factorization model
        - interactions = dataset used for training the model
    Expected Output -
        - item_emdedding_distance_matrix = Pandas dataframe containing cosine distance matrix b/w items
    """
    df_item_norm_sparse = sparse.csr_matrix(model.item_embeddings)
    similarities = cosine_similarity(df_item_norm_sparse)
    item_emdedding_distance_matrix = pd.DataFrame(similarities)
    item_emdedding_distance_matrix.columns = interactions.columns
    item_emdedding_distance_matrix.index = interactions.columns
    return item_emdedding_distance_matrix


def item_item_recommendation(item_emdedding_distance_matrix, item_id,
                             item_dict, n_items=10, show=True):
    '''
    Function to create item-item recommendation
    Required Input -
        - item_emdedding_distance_matrix = Pandas dataframe containing cosine distance matrix b/w items
        - item_id  = item ID for which we need to generate recommended items
        - item_dict = Dictionary type input containing item_id as key and item_name as value
        - n_items = Number of items needed as an output
    Expected Output -
        - recommended_items = List of recommended items
    '''
    recommended_items = list(pd.Series(
        item_emdedding_distance_matrix.loc[item_id, :].sort_values(ascending=Fase).head(n_items + 1).index[
        1:n_items + 1]))
    if show == True:
        print("Item of interest :{0}".format(item_dict[item_id]))
        print("Item similar to the above item:")
        counter = 1
        for i in recommended_items:
            print(str(counter) + '- ' + im_dict[i])
            counter += 1
    return recommended_items


# In[144]:

destinations = pd.read_csv(settings.BASE_DIR + '/dream_trip/static/destinationdetail.csv')
users = pd.read_csv(settings.BASE_DIR + '/dream_trip/static/userdetail.csv')

# Creating interaction matrix using rating data
interactions = create_interaction_matrix(df=users,
                                         user_col='userid',
                                         item_col='destinationid',
                                         rating_col='rating')

# Create User Dict
user_dict = create_user_dict(interactions=interactions)
# Create Item dict
destinations_dict, destinations_data = create_item_dict(df=destinations,
                                                        id_col='destinationid',
                                                        name_col='destinationname',
                                                        average_stay='average_stay',
                                                        lat='lat',
                                                        long='long',
                                                        image_url='image_url',
                                                        category='Category',
                                                        voyager_id='voyager_id')

from lightfm.data import Dataset

dataset = Dataset()
dataset.fit((x[0] for i, x in users.iterrows()),
            (x[1] for i, x in users.iterrows()))
# (interactions, weights) = dataset.build_interactions((x[0],x[1]) for i,x in users.iterrows())
dataset.fit_partial(items=(x['destinationid'] for i, x in destinations.iterrows()),
                    item_features=(x['Destination-tf-idf'] for i, x in destinations.iterrows()))
dataset.fit_partial(items=(x['userid'] for i, x in users.iterrows()),
                    user_features=(x['age'] for i, x in users.iterrows()))

item_features = dataset.build_item_features(
    ((x['destinationid'], [x['Destination-tf-idf']]) for i, x in destinations.iterrows()))
user_features = dataset.build_user_features(((x['userid'], [x['age']]) for i, x in users.iterrows()))

mf_model = runMF(interactions=interactions, item_features=item_features, user_features=user_features,
                 n_components=30,
                 loss='warp',
                 epoch=30,
                 n_jobs=4)


def sample_recommendation_user_1(user_id):
    rec_list = sample_recommendation_user(model=mf_model,
                                          interactions=interactions,
                                          user_id=int(user_id),
                                          user_dict=user_dict,
                                          item_dict=destinations_dict,
                                          threshold=5,
                                          nrec_items=len(destinations_dict),
                                          show=False)
    rec_name_list = []
    record_list = []
    for destination_id in rec_list:
        rec_name_list.append(destinations_dict[destination_id])
        temp_data = destinations_data[destination_id]
        temp_data['destination_id'] = destination_id
        record_list.append(temp_data)
    return rec_list, record_list


# [103, 117, 104, 110, 112, 111, 113, 102, 101, 107]


# In[80]:


# In[120]:


# def sample_recommendation_item(model,interactions,item_id,user_dict,item_dict,number_of_user):
rec_list = sample_recommendation_item(model=mf_model, interactions=interactions, item_id=1, user_dict=user_dict,
                                      item_dict=destinations_dict, number_of_user=len(user_dict))
rec_list

# In[62]:


# In[56]:


# In[58]:


# print(repr(item_features))

# (interactions, weights) = dataset.build_interactions((x[0], x[1]) for i, x in users.iterrows())

# In[61]:


# print(item_features)
