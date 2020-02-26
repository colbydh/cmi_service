import time

import requests
import urllib.parse
from background_services.config import *


def get_coords(location, elapsed_time):

    # try locationiq
    lat, lon = get_coords_using_locationiq(location, elapsed_time)

    return lat, lon


def get_coords_using_here(location):
    text = urllib.parse.quote_plus(location)
    url = 'https://geocoder.ls.hereapi.com/6.2/geocode.json?apiKey=' + HERE_API_KEY + '&searchtext=' + text
    # sending get request and saving the response as response object
    r = requests.get(url=url)

    # extracting data in json format
    data = r.json()
    if 'Response' not in data.keys():
        return None, None

    view = data['Response']['View']

    if len(view) <= 0:
        return None, None
    else:
        result = view[0]['Result'][0]['Location']['DisplayPosition']
        return result['Latitude'], result['Longitude']


def get_coords_using_opencage(location):
    url = 'https://api.opencagedata.com/geocode/v1/json?q=' + location + '&key=' + OPEN_CAGE_API_KEY

    # sending get request and saving the response as response object
    try:
        r = requests.get(url=url)

        # extracting data in json format
        data = r.json()
        if len(data['results']) > 0:
            results = data['results']
            # Get the first one
            results[0]['geometry']
            return results[0]['geometry']['lat'], results[0]['geometry']['lng']
        else:
            print(data)
            return None, None
    except Exception as e:
        print(e)
        return None, None


def get_coords_using_locationiq(location, elapsed_time):
    try:
        if location == '' or location == ' ' or location == '  ' or location == '            ':
            return 'No Geocode', 'No Geocode'

        text = urllib.parse.quote_plus(location)
        url = 'https://us1.locationiq.com/v1/search.php?key=' + LOCATIONIQ_KEY + '&q=' + text + '&format=json'

        # if elapsed time not reached wait
        if elapsed_time < 1:
            time.sleep(2)

        # sending get request and saving the response as response object
        r = requests.get(url=url)

        # extracting data in json format
        data = r.json()

        if type(data) == dict:
            if 'error' in data.keys():
                if data['error'] == 'Unable to geocode':
                    return 'No Geocode', 'No Geocode'
                if data['error'] == 'Rate Limited Second':
                    time.sleep(2)
                    # sending get request and saving the response as response object
                    r = requests.get(url=url)

                    # extracting data in json format
                    data = r.json()
                    if type(data) == dict:
                        if 'error' in data.keys():
                            if data['error'] == 'Unable to geocode':
                                return 'No Geocode', 'No Geocode'

        if len(data) <= 0:
            return None, None
        else:
            return float(data[0]['lat']), float(data[0]['lon'])
    except Exception as e:
        #print('Error in get coords from location iq: ', data)
        return None, None



