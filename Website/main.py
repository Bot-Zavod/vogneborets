# coding: utf-8

from flask import Flask, render_template, request, redirect
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map, icons

from TwinklyDb import *

import requests



app = Flask(__name__, template_folder="templates", static_folder="static")

# you can set key as config
app.config['GOOGLEMAPS_KEY'] = "AIzaSyBTfQk2e0_GziHCnrhHYcVituFAWEgBIuQ"

# you can also pass key here
GoogleMaps(
    app,
    #key="AIzaSyDP0GX-Wsui9TSDxtFNj2XuKrh7JBTPCnU"
)

# NOTE: this example is using a form to get the apikey

def makePin(mrk):
    cmt = '<br>'.join(mrk.comments)
    return  {
                'icon': icons.dots.red if mrk.mark < 30 else icons.dots.yellow if mrk.mark < 70 else icons.dots.green,
                'lat': mrk.lat,
                'lng': mrk.lng,
                'infobox': f"<p><b>Місце:</b>{mrk.name}<br><b>Рейтинг:</b> {mrk.mark}<br><b>Коментарі:</b><br>{cmt}</p>"
            }

def updateReviews():
    reviews = Review.getMarkers().values()
    return tuple(makePin(m) for m in reviews)

@app.route("/", methods=["GET", "POST"])
def mapview():
    try:
        host = request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0]
        response = requests.get("http://ip-api.com/json/{}".format(host))
        print(host)
        js = response.json()
        if js['status'] != "success":
            raise Exception('COULD NOT DEFINE LOCATION')
        print(js['countryCode'])
        user_lat = js['lat']
        user_lng = js['lon']
        zoom = 12
    except Exception as e:
        print(e)
        user_lat = 49.114646
        user_lng = 31.131265
        zoom = 6.5
        print("Unknown Location")
    markers = updateReviews()
    twmap = Map(
        identifier="twmap",
        varname="twmap",
        cls='',
        style=(
             "width: 100%;"
             "height: 100vh;" 
        ),
        lat=user_lat,
        lng=user_lng,
        zoom = zoom,
        markers=markers,
    )

    return render_template(
        'index.html',
        twmap=twmap,
    )

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True, host= '0.0.0.0')
