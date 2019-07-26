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
        url = "http://developer.goibibo.com/api/search/"
        params = {"app_id": "ab0d48e9",
                  "app_key": "7bfa0cad77827f2bb0ea03bd0ad74ecf",
                  "format": "json",
                  "source": "BLR",
                  "destination": "STV",
                  "dateofdeparture": "20191027",
                  "seatingclass": "E",
                  "adults": "1",
                  "children": "0",
                  "infants": "0",
                  "counter": "100"}
        response = requests.get(url, params=params)

        return Response(response.json())
