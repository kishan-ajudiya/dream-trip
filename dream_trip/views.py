import json
import requests
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from destination_recommendations import sample_recommendation_user_1, get_all_users


class Flights(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Return a list of all flights.
        """
        source = request.GET.get("source", "BLR")
        destination = request.GET.get("destination", "DEL")
        dateofdeparture = request.GET.get("date_of_departure", "20191027")
        resp = get_flights(source, destination, dateofdeparture)
        return Response(resp)


def get_flights(source, destination, dateofdeparture):
    url = "http://developer.goibibo.com/api/search/"
    params = {"app_id": "ab0d48e9",
              "app_key": "7bfa0cad77827f2bb0ea03bd0ad74ecf",
              "format": "json",
              "source": source,
              "destination": destination,
              "dateofdeparture": dateofdeparture,
              "seatingclass": "E",
              "adults": "1",
              "children": "0",
              "infants": "0",
              "counter": "2"
              }
    response = requests.get(url, params=params)
    resp = []
    if response.status_code == 200:
        response_data = response.json().get("data", {}).get("onwardflights", [])
        response_data = [d for d in response_data if d['stops'] in ["0", ""]]
        for obj in response_data:
            new_obj = {
                "fare": obj.get('fare', {}),
                "origin": obj.get("origin", ""),
                "destination": obj.get("destination", ""),
                "carrierid": obj.get("carrierid", ""),
                "flightno": obj.get("flightno", ""),
                "duration": obj.get("duration", ""),
                "airline": obj.get("airline", ""),
                "depdate": obj.get("depdate", ""),
                "deptime": obj.get("deptime", ""),
                "arrtime": obj.get("arrtime", ""),
                "arrdate": obj.get("arrdate", ""),
            }
            resp.append(new_obj)
    sorted_resp = sorted(resp, key=lambda i: i['fare'])
    return sorted_resp[:2]


class Experiences(APIView):

    def post(self, request):
        """
        :param request:
        :return: Return a list of experience near by 50 KM ranges
        """
        url = 'https://hippie.goibibo.com/activity_srp_v2/city_data/'

        headers = {
            'content-type': 'application/json',
            'OAUTH-GOIBIBO': 'de94afd9abcf610773419329603a776325727968',
            'Authorization': 'Basic bW9iaWxlOnc5V2cmPDtoLWQ+WCQyag=='
        }
        data = request.data.copy()
        # payloads = {
        #     'lat': 12.9716,
        #     'long': 77.5946,
        #     'vcid': '2311763083662248959',
        #     'sd': 1564248611,
        #     'ed': 1569432611,
        #     'flavour': 'android',
        #     'pn': 1,
        #     'ps': 50,
        #     'pc': 1
        # }
        
        data["sd"] = 1564248611
        data["ed"] = 1569432611

        response = requests.post(url, data=json.dumps(data), headers=headers)
        response = response.json()
        result_list = {'experiences': []}
        experiences_data = response.get('data', {}).get('items', [])
        for experience in experiences_data:
            result_list['experiences'].append(
                {'name': experience['n'], 'image_url': experience['img'], 'price': experience['sp'],
                 'star_rating': experience['star_rating'], 'location': experience['ct']})
        result_list['experiences'] = sorted(result_list['experiences'], key=lambda i: i['star_rating'], reverse=True)
        return Response(result_list)


class Hotels(APIView):
    def get(self, request):
        """
        Return a list of all hotels.
        """
        city_code = request.GET.get("city_code", "6624397033787067229")
        checkin_date = request.GET.get("checkin_date", "20191026")
        checkout_date = request.GET.get("checkout_date", "20191027")
        url = "https://hermes.goibibo.com/hotels/v9/search/data/v3/" + city_code + "/" + checkin_date + "/" \
              + checkout_date + "/1-1-0"

        params = {
            "s": "popularity",
            "cur": "INR",
            "f": "{}",
            "sb": "0",
            "ud": "",
            "ai": "1",
            "asi": "0",
            "st": "voy",
            "vt": "city",
            "eid": city_code,
            "pid": "0",
            "im": "true"
        }
        response = requests.get(url, params=params)
        resp = []
        if response.status_code == 200:
            response_data = response.json().get("data", [])
            for obj in response_data:
                data_dict = {
                    "hotel_name": obj.get("hn", ""),
                    "star_rating": obj.get("gr", ""),
                    "image_url": obj.get("t", ""),
                    "price": obj.get("opr", ""),
                    "rating_count": obj.get("grc", ""),
                    "badge": obj.get("bt", ""),
                    "location": obj.get("l", ""),
                    "info": obj.get("ut", "")
                }
                resp.append(data_dict)
        return Response(resp)


class Recommendation(APIView):
    def get(self, request):
        user_id = request.GET.get('user_id', '5')
        all_users = get_all_users()
        user_id = user_id if all_users.get(int(user_id)) else '5'
        user_past_records, recommendations = sample_recommendation_user_1(user_id)
        results = {'past_records': user_past_records, 'recommendations': recommendations}
        return Response(results)


class Route(APIView):
    def get(self, request):
        response_data = []
        origin_city = request.GET.get('origin_city')
        destination_city = request.GET.get('destination_city')
        dateofdeparture = request.GET.get("date_of_departure", "20191027")
        url = 'http://free.rome2rio.com/api/1.4/json/Search?key=TaJdGrwg&oName=%s&dName=%s&currency=INR' % \
              (origin_city, destination_city)
        response = requests.get(url).json()
        if response.get('routes'):
            sorted_routes = sorted(response['routes'], key=lambda i: i['totalDuration'])
            for segment in sorted_routes[0]['segments']:
                stop = {
                    'travel_mode': segment['segmentKind'],
                    'from_city': response['places'][segment['depPlace']],
                    'to_city': response['places'][segment['arrPlace']],
                    'pricing': segment['indicativePrices'],
                }
                response_data.append(stop)
        for obj in response_data:
            if obj["travel_mode"] == "air":
                import pdb
                pdb.set_trace()
                source = obj["from_city"]["code"]
                destination = obj["to_city"]["code"]
                resp = get_flights(source, destination, dateofdeparture)
                obj["flights"] = resp
        return Response({'data': response_data})


class Users(APIView):
    def get(self, request):
        all_users = get_all_users()
        return Response(all_users)
