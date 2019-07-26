import json
import requests


def get_cab_place_id(place):
    url = 'https://gocars.goibibo.com/v1/google/places/text_search?input=%s&limit=10&' \
          'flavour=cars_dweb&vertical=GoCars&media=source&sl_loc_type=city&' \
          'sl_place_id=ChIJ_396YnUApTsRpsFRRupmiq8&rf=ow' % place
    headers = {
        'Authorization': 'Basic Z2R6dnY5NzExMXp6dHYxanEybHR0M2h4M3Jqb2U0MHJiaHQ2OW1kYjh6aWxqamFtMW00bHl1dzk4Z25wNDNy'
                         'YzpnMTJveWZ4YmpldDN4dnN3amNhdjRqNnRoMDVobnB2djhka213azF4ZDNudHNnajcwczFqeHBoNTRsYWJ4bnEw'
    }
    response = requests.get(url, headers=headers).json()
    return response['predictions'][0]['description'], response['predictions'][0]['place_id']


def get_cars_data(source, destination, date_of_travel):
    url = 'https://gocars.goibibo.com/api/apps/v4/home?flavour=cars_dweb&platform=gocars'
    headers = {
        'Authorization': 'Basic Z2R6dnY5NzExMXp6dHYxanEybHR0M2h4M3Jqb2U0MHJiaHQ2OW1kYjh6aWxqamFtMW00bHl1dzk4Z25wNDNyY'
                         'zpnMTJveWZ4YmpldDN4dnN3amNhdjRqNnRoMDVobnB2djhka213azF4ZDNudHNnajcwczFqeHBoNTRsYWJ4bnEw',
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json;',
        'DEVICE-GOIBIBO': '1'
    }
    source_name, source_id = get_cab_place_id(source)
    destination_name, destination_id = get_cab_place_id(destination)
    payload = {
        "source_name": source_name,
        "source_id": source_id,
        "search_id": "",
        "package_id": "",
        "start_time": date_of_travel,
        "end_time": "",
        "trip_type": "ONE_WAY",
        "flavour": "cars_dweb",
        "rf": "ow",
        "destination_name": destination_name,
        "destination_id": destination_id
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers).json()
    if response['response'].get('no_result_message') or response['error']:
        return None
    return response


def get_train_station_code(place):
    url = 'https://voyager.goibibo.com/api/v2/trains_search/find_node_by_name/?' \
          'search_query=%s&limit=10&flavour=ios&vertical=GoRail' % place
    response = requests.get(url).json()
    return response['data']['r'][0]['dn'], response['data']['r'][0]['irctc_code']


def get_trains_data(source, destination, date_of_travel):
    source_name, source_code = get_train_station_code(source)
    destination_name, destination_code = get_train_station_code(destination)
    date = date_of_travel.replace('-', '')
    url = 'https://gotrains.goibibo.com/v1/booking/train_listing/%s/%s/%s?' \
          'sort_by=DEP&sort_order=ASC&offset=0&limit=10&flavour=dweb' % (source_code, destination_code, date)
    headers = {
        'Authorization': 'Basic V2dUM2U2R3E4WTprUDdOeFZKak45bTh1TUxGM0djRHRwVFB1YUxqUDZ3Vg==',
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json;'
    }
    payload = {
        "class": "All",
        "source_station": {
            "code": source_code,
            "name": source_name,
        },
        "destination_station": {
            "code": destination_code,
            "name": destination_name,
        }
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers).json()
    if response['error']:
        return None
    return response


def get_bus_data(source, destination, date_of_travel):
    date = date_of_travel.replace('-', '')
    url = 'https://www.goibibo.com/bus/getsearch/v1/?flavour=v2&versioncode=mfore&application=bus&' \
          'actionId=BusFareSearchRequest&transaction_required=123&cache=true&qtype=bus&' \
          'rand=0.35409928687715997&vc=latest&query=bus-%s-%s-%s--1-0-0' % (source, destination, date)
    try:
        response = requests.get(url).json()
    except:
        return None
    return response

