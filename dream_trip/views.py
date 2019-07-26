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
        url = "https://thor.goibibo.com/v1/thor/rest/flight/search/max"
        params = {
            "multi": "n",
            "transaction_required": False,
            "cache": False,
            "userid": 156,
            "actionData": [{"query": "air-BLR-DEL-20190903--1-0-0-E-0--"}],
            "application": "b2b",
            "actionId": "AirFareSearchRequest",
            "flavour": "api",
            "qtype": "fbs"}
        params["actionData"] = json.dumps(params["actionData"])
        response = requests.get(url, params=params)

        return Response(response.json())


