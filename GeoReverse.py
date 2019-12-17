from json import loads
import urllib.request
from init import MapInitialize
from requests import get
# This module will help you while working
# with adresses and coordinates using google maps api

types = ['accounting', 'airport', 'amusement_park', 'aquarium', 'art_gallery', 'atm', 'bakery', 'bank', 'bar', 'beauty_salon', 'bicycle_store', 'book_store', 'bowling_alley', 'bus_station', 'cafe', 'campground', 'car_dealer', 'car_rental', 'car_repair', 'car_wash', 'casino', 'cemetery', 'church', 'city_hall', 'clothing_store', 'convenience_store', 'courthouse', 'dentist', 'department_store', 'doctor', 'drugstore', 'electrician', 'electronics_store', 'embassy', 'fire_station', 'florist', 'funeral_home', 'furniture_store', 'gas_station', 'grocery_or_supermarket', 'gym', 'hair_care', 'hardware_store', 'hindu_temple', 'home_goods_store', 'hospital', 'insurance_agency', 'jewelry_store', 'laundry', 'lawyer', 'library', 'light_rail_station', 'liquor_store', 'local_government_office', 'locksmith', 'lodging', 'meal_delivery', 'meal_takeaway', 'mosque', 'movie_rental', 'movie_theater', 'moving_company', 'museum', 'night_club', 'painter', 'park', 'parking', 'pet_store', 'pharmacy', 'physiotherapist', 'plumber', 'police', 'post_office', 'primary_school', 'real_estate_agency', 'restaurant', 'roofing_contractor', 'rv_park', 'school', 'secondary_school', 'shoe_store', 'shopping_mall', 'spa', 'stadium', 'storage', 'store', 'subway_station', 'supermarket', 'synagogue', 'taxi_stand', 'tourist_attraction', 'train_station', 'transit_station', 'travel_agency', 'university', 'veterinary_care', 'zoo']


def CoordinatesToAdress(coordinates):
    # This function accept coordinates like "30.714546,46.380251" and returs list of possible adresses
    # getting the key from init module
    key = MapInitialize()

    link0 ="https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="+coordinates+"&type=establishment&language=ru&radius=30&key="+key
    adress=[]
    output0 = loads(get(link0).text)
    for ad in range(len(output0['results'])):
        if output0['results'][ad]['types'][0] in types:
            name = output0['results'][ad]['name']
            adr = output0['results'][ad]['vicinity']
            lat = output0['results'][0]['geometry']['location']['lat']
            lng = output0['results'][0]['geometry']['location']['lng']
            typ = output0['results'][ad]['types'][0]
            adress.append({'name':name, 'adr':adr, 'typ': typ, 'loc':(lat,lng)})

    link = "https://maps.googleapis.com/maps/api/geocode/json?latlng="+coordinates+"&language=ru&location_type=ROOFTOP&key="+key
    # we open the google page downloading their JSON as str and turning it into python file
    output = loads(get(link).text)
    for ad in range(len(output['results'])):
        # itarate and format all available adresses
        adr = output['results'][ad]['formatted_address']
        adr = adr.split(" ")
        adr = adr[:-5]
        adr = " ".join(adr)
        adr = adr[:-1]
        # adress.append({'name': '', 'adr':adr, 'typ': '', 'loc':(lat,lng)})
    return adress

def AdressToCoordinates(adress):
    # This function accept possible adress like "Дерибасовская Макдональдс"
    # and returs list with the right adress and its coordinates
    key = MapInitialize()
    #adress should be splitted with + and url encoded
    adress = adress.replace(" ","+")
    adress = urllib.parse.quote_plus(adress)
    link = "https://maps.googleapis.com/maps/api/geocode/json?address="+adress+"&key="+key
    output = loads(get(link).text)
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
    a = CoordinatesToAdress("46.48402859999999,30.737146")
    for x in a:
        print(x['name'])
