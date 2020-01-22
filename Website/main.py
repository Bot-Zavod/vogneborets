# coding: utf-8

from flask import Flask, render_template, request, redirect
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map, icons
import stripe
from TwinklyDb import *

app = Flask(__name__, template_folder="templates")

pub_key = 'pk_test_3LtOdozoRiUg6rH7Jtn5k8tR008gczBxTM'
secret_key = 'sk_test_6pYkFEXMF33C1y8ldLrS1wi50006quKVd3'

stripe.api_key = secret_key

# you can set key as config
app.config['GOOGLEMAPS_KEY'] = "AIzaSyBTfQk2e0_GziHCnrhHYcVituFAWEgBIuQ"

# you can also pass key here
GoogleMaps(
    app
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
        style=(
            "height:100%;"
            "width:100%;"
            "left:0;"
            "position:absolute;"
            # "z-index:200;"            
        ),
        lat=46.44,
        lng=30.75,
        zoom = 15,
        markers=markers
    )

    return render_template(
        'main.html',
        twmap=twmap,
        GOOGLEMAPS_KEY=request.args.get('apikey')
    )

@app.route("/team", methods=["GET", "POST"])
def about_us():
    return render_template('about_us.html')

@app.route("/donate")
def donate():
    return render_template('donate.html')

@app.route("/donate/<amount>")
def donate_post_amount(amount):
    amount = int(amount)
    return render_template('donate_amount.html', amount = amount)

@app.route('/pay', methods=['POST'])
def pay():
    print('Token:' + request.form['stripeToken'])
    customer = stripe.Customer.create(source=request.form['stripeToken'])

    charge = stripe.Charge.create(
        customer=customer.id,
        amount=int(request.form['amount']),
        currency='uah',
        description='The Product'
    )

    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True, host= '0.0.0.0')
