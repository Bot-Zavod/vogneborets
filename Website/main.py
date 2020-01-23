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
    print('called')
    markers = updateReviews()
    print(len(markers))
    twmap = Map(
        identifier="twmap",
        varname="twmap",
        cls='',
        style=(
            "height:100%;"
            "width:100%;"
            # "top:100%;"
            # "left:0;"
            # "position:absolute;"
            # "z-index:200;"
        ),
        lat=46.44,
        lng=30.75,
        zoom = 15,
        markers=markers,
        fit_markers_to_bounds=True
    )

    return render_template(
        'index.html',
        twmap=twmap,
    )

@app.route("/map")
def map():
    markers = updateReviews()
    print(len(markers))
    twmap = Map(
        identifier="twmap",
        varname="twmap",
        cls='',
        style=(
            "height:100%;"
            "width:100%;"
            "position:absolute;"
            "z-index:200;"
            "top:0;"
            "left:0;"
        ),
        lat=46.44,
        lng=30.75,
        zoom = 15,
        markers=markers,
        fit_markers_to_bounds=True
    )

    return render_template(
        'map.html',
        twmap=twmap,
    )


if __name__ == "__main__":
    app.run(debug=True, use_reloader=True, host= '0.0.0.0', port=5001)
