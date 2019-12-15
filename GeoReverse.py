import json,urllib.request
from init import MapInitialize
# This module will help you while working
# with adresses and coordinates
# using google maps api


def CoordinatesToAdress(coordinates):
    # This function accept coordinates like "30.714546,46.380251"
    # and returs list of possible adresses
    key = MapInitialize() #getting the key from init module
    link = "https://maps.googleapis.com/maps/api/geocode/json?latlng="+coordinates+"&language=ru&location_type=ROOFTOP&key=" + key
    data = urllib.request.urlopen(link).read()
    output = json.loads(data)
    # we open the google page downloading their JSON data file
    adress=[]
    for ad in range(len(output['results'])):
        # itarate and format all available adresses
        adr = output['results'][ad]['formatted_address']
        adr = adr.split(" ")
        adr = adr[:-5]
        adr = " ".join(adr)
        adr = adr[:-1]
        adress.append(adr)
    # test whole json file
    # print(json.dumps(output, indent=4, sort_keys=True))
    return adress

def AdressToCoordinates(adress):
    # This function accept possible adress like "Дерибасовская Макдональдс"
    # and returs list with the right adress and its coordinates
    key = MapInitialize()
    #adress should be splitted with + and url encoded
    adress = adress.split(" ")
    adress = "+".join(adress)
    adress = urllib.parse.quote_plus(adress)
    link = "https://maps.googleapis.com/maps/api/geocode/json?address="+adress+"&key=" + key
    print(link)
    data = urllib.request.urlopen(str(link)).read()
    output = json.loads(data)
    # test whole json file
    # print(json.dumps(output, indent=4, sort_keys=True))
    # getting adress and format it
    adress = output['results'][0]['formatted_address']
    adress = adress.split(" ")
    adress = adress[:-5]
    adress = " ".join(adress)
    adress = adress[:-1]
    # getting coordinates
    lat = output['results'][0]['geometry']['location']['lat']
    lng = output['results'][0]['geometry']['location']['lng']
    coordinates = [adress,[lat,lng]]
    return coordinates

if __name__ == "__main__":
    # test data
    coordinates = "46.380251,30.714546"
    adress = 'Дерибасовская Макдональдс'
    CoordinatesToAdress(coordinates)
    AdressToCoordinates(adress)