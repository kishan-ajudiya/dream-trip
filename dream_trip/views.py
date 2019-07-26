import json

import requests

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class Flights(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Return a list of all users.
        """
        url = 'https://thor.goibibo.com/v1/thor/rest/flight/search/max'
        params = {
            'multi': 'n',
            'transaction_required': False,
            'cache': False,
            'userid': 156,
            'actionData': [{'query': 'air-BLR-DEL-20190903--1-0-0-E-0--'}],
            'application': 'b2b',
            'actionId': 'AirFareSearchRequest',
            'flavour': 'api',
            'qtype': 'fbs'}
        params['actionData'] = json.dumps(params['actionData'])
        response = requests.get(url, params=params)

        return Response(response.json())


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
        payloads = {
            'lat': 12.9716,
            'long': 77.5946,
            'vcid': '2311763083662248959',
            'sd': 1564248611,
            'ed': 1569432611,
            'flavour': 'android',
            'pn': 1,
            'ps': 50,
            'pc': 1
        }
        response = requests.post(url, data=json.dumps(payloads), headers=headers)
        return Response(response.json())
