# coding: utf-8

from flask import Flask, render_template, request, redirect
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map, icons

from TwinklyDb import *

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
        response = requests.get("http://ip-api.com/json/{}".format(request.remote_addr))
        js = response.json()
        print(js['countryCode'])
        user_lat = js['lat']
        user_lng = js['lon']
    except Exception:
        user_lat = 46.44
        user_lng = 30.75
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
        zoom = 16,
        markers=markers,
    )

    return render_template(
        'index.html',
        twmap=twmap,
    )

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True, host= '0.0.0.0', port=8080)
