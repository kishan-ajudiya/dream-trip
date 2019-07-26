import json

import requests

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from city_recommendations import sample_recommendation_user_1


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
        response_data = []
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
        if response.status_code:
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

        return Response(resp)


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


class Hotels(APIView):
    def get(self, request):
        """
        Return a list of all hotels.
        """

        url = "https://hermes.goibibo.com/hotels/v9/search/data/v3/6624397033787067229/20190726/20190727/3-3-0"

        params = {
            "s": "popularity",
            "cur": "INR",
            "f": "{}",
            "sb": "0",
            "ud": "Coorg",
            "ai": "1",
            "asi": "0",
            "st": "voy",
            "vt": "city",
            "eid": "6624397033787067229",
            "pid": "0",
            "im": "true"
        }
        response = requests.get(url, params=params)

        return Response(response.json())


class Recommendation(APIView):

    def get(self, request):
        city_id = request.GET.get('city_id', 103)

        import pdb
        pdb.set_trace()
        result = sample_recommendation_user_1(city_id)
        return Response(result)
