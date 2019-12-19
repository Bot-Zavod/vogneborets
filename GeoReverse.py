from json import loads
from urllib.parse import quote_plus
from init import MapInitialize
from requests import get
# This module will help you while working
# with adresses and coordinates using google maps api

types ={1:['primary_school', 'school', 'secondary_school', 'university'],
        2:['bar', 'cafe', 'meal_delivery', 'meal_takeaway', 'restaurant'],
        3:['accounting', 'atm', 'bakery', 'bank', 'beauty_salon', 'bicycle_store', 'book_store', 'bus_station', 'car_dealer', 'car_rental', 'car_repair', 'car_wash', 'clothing_store', 'convenience_store', 'dentist', 'department_store', 'doctor', 'drugstore', 'electrician', 'electronics_store', 'florist', 'gas_station', 'grocery_or_supermarket', 'hair_care', 'hardware_store', 'hindu_temple', 'home_goods_store', 'insurance_agency', 'jewelry_store', 'laundry', 'lawyer', 'liquor_store', 'locksmith', 'pet_store', 'pharmacy', 'physiotherapist', 'plumber', 'post_office', 'real_estate_agency', 'roofing_contractor', 'shoe_store', 'spa', 'storage', 'store', 'tourist_attraction', 'travel_agency', 'veterinary_care'],
        4:['airport', 'amusement_park', 'aquarium', 'art_gallery','bowling_alley', 'casino', 'church', 'city_hall', 'embassy', 'fire_station', 'funeral_home', 'furniture_store', 'gym', 'hospital', 'library', 'light_rail_station', 'local_government_office', 'mosque', 'movie_rental', 'movie_theater', 'moving_company', 'museum', 'night_club', 'painter', 'park', 'parking', 'police', 'shopping_mall', 'stadium', 'subway_station', 'supermarket', 'synagogue', 'taxi_stand', 'train_station', 'transit_station', 'zoo'],
        5:['campground', 'cemetery', 'courthouse', 'lodging', 'rv_park']}
          
def find_type(typ):
    for key in types.keys():
        if typ in types[key]:
            return key

def CoordinatesToAdress(coordinates):
    # This function accept coordinates like "30.714546,46.380251" and returs list of possible adresses
    # getting the key from init module
    key = MapInitialize()
    
    link0 ="https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="+coordinates+"&language=ru&radius=30&key="+key
    # print(link0)
    adress=[]
    output0 = loads(get(link0).text)   
    if len(output0['results'])!=0:
        for ad in range(len(output0['results'])):
            if output0['results'][ad]['types'][0] in (types[1]+types[2]+types[3]+types[4]+types[5]):
                name = output0['results'][ad]['name']
                adr = output0['results'][ad]['vicinity']
                lat = output0['results'][0]['geometry']['location']['lat']
                lng = output0['results'][0]['geometry']['location']['lng']
                typ = output0['results'][ad]['types'][0]
                typ = find_type(typ)
                adress.append({'name':name, 'adr':adr, 'typ': typ, 'loc':(lat,lng)})
    else:
        raise Exception('No company')

    link = "https://maps.googleapis.com/maps/api/geocode/json?latlng="+coordinates+"&language=ru&result_type=street_address&key="+key
    # print(link)
    # we open the google page downloading their JSON as str and turning it into python file
    output = loads(get(link).text)
    if len(output0['results'])!=0:
        for ad in range(len(output['results'])):
            # itarate and format all available adresses
            adr = output['results'][ad]['formatted_address']
            adr = adr.split(" ")
            adr = adr[:-5]
            adr = " ".join(adr)
            adr = adr[:-1]
            lat = output0['results'][0]['geometry']['location']['lat']
            lng = output0['results'][0]['geometry']['location']['lng']
            adress.append({'name': adr, 'adr':adr, 'typ': 6, 'loc':(lat,lng)})
    else:
        raise Exception('No such adress')
   
   
    # for i in adress:
    #     print(i)
    return adress

def AdressToCoordinates(adress):
    # This function accept possible adress like "Дерибасовская Макдональдс"
    # and returs list with the right adress and its coordinates
    key = MapInitialize()
    #adress should be splitted with + and url encoded
    adress = adress.replace(" ","+")
    adress = quote_plus(adress)
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
    a = CoordinatesToAdress("46.4853906,30.7250282")
    for x in a:
        print(x['typ'],"\t",x['name'])
    # CoordinatesToAdress("46.48402859999999,30.737146")
    # print(AdressToCoordinates("Нежинская 39"))