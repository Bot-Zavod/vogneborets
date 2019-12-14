# import googlemaps
# from datetime import datetime
import json,urllib.request
from init import MapInitialize
# gmaps = googlemaps.Client(key='AIzaSyD-bmZD2Va33uA-4r9cCVfLqOorSRtDB2I')
# Look up an address with reverse geocoding
# reverse_geocode_result = gmaps.reverse_geocode((46.380256, 30.714669), language=ru)
# print(reverse_geocode_result)


def CoordinatesToAdress(coordinates):
    key = MapInitialize()
    link = "https://maps.googleapis.com/maps/api/geocode/json?latlng="+coordinates+"&location_type=ROOFTOP&key=" + key
    data = urllib.request.urlopen(link).read()
    output = json.loads(data)
    adress = output['results'][0]['formatted_address']
    print(output['results'][0]['formatted_address'],"\n")
    return adress
# test whole json
# print(json.dumps(output, indent=4, sort_keys=True))