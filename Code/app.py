"""Web app."""
import flask
from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo
import pickle
import base64
from training import prediction
import requests
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = flask.Flask(__name__)

# MongoDB Configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/your_database_name"  # Update with your MongoDB URI
mongo = PyMongo(app)

# Get the current month
current_month = datetime.now().strftime("%B")

data = [{'name':'Delhi', "sel": "selected"}, {'name':'Mumbai', "sel": ""}, {'name':'Kolkata', "sel": ""}, {'name':'Bangalore', "sel": ""}, {'name':'Chennai', "sel": ""}]
months = [{"name":"May", "sel": ""}, {"name":"June", "sel": ""}, {"name":"July", "sel": ""}, {"name": current_month, "sel": "selected"}]
cities = [{'name':'Delhi', "sel": "selected"}, {'name':'Mumbai', "sel": ""}, {'name':'Kolkata', "sel": ""}, {'name':'Bangalore', "sel": ""}, {'name':'Chennai', "sel": ""}, {'name':'New York', "sel": ""}, {'name':'Los Angeles', "sel": ""}, {'name':'London', "sel": ""}, {'name':'Paris', "sel": ""}, {'name':'Sydney', "sel": ""}, {'name':'Beijing', "sel": ""}]

model = pickle.load(open("model.pickle", 'rb'))

@app.route("/")
def index() -> str:
    """Redirect to login page."""
    return redirect(url_for('login'))

@app.route('/loginpage.html', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Process login form data
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validate credentials against MongoDB
        user = mongo.db.users.find_one({"email": email, "password": password})
        if user:
            logging.info(f"User logged in with email: {email}")
            return redirect(url_for('home'))
        else:
            return "Invalid credentials", 401  # Return an error for invalid credentials

    return render_template('loginpage.html')

@app.route('/signup.html', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Process signup form data
        full_name = request.form.get('fullName')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Store user data in MongoDB
        mongo.db.users.insert_one({"full_name": full_name, "email": email, "password": password})
        logging.info(f"New user signed up: {full_name} with email: {email}")
        return redirect(url_for('home'))

    return render_template('signup.html')

@app.route('/home.html')
def home():
    return render_template('home.html')

@app.route('/plots.html')
def plots():
    return render_template('plots.html')

@app.route('/heatmaps.html')
def heatmaps():
    return render_template('heatmaps.html')

@app.route('/chart.html')
def chart():
    return render_template('chart.html')

@app.route('/satellite.html')
def satellite():
    direc = "satellite_images/Delhi_July.png"
    with open(direc, "rb") as image_file:
        image = base64.b64encode(image_file.read())
    image = image.decode('utf-8')
    return render_template('satellite.html', data=data, image_file=image, months=months, text="Delhi in January 2024")

@app.route('/satellite.html', methods=['GET', 'POST'])
def satelliteimages():
    place = request.form.get('place')
    date = request.form.get('date')
    data = [{'name':'Delhi', "sel": ""}, {'name':'Mumbai', "sel": ""}, {'name':'Kolkata', "sel": ""}, {'name':'Bangalore', "sel": ""}, {'name':'Chennai', "sel": ""}]
    months = [{"name":"May", "sel": ""}, {"name":"June", "sel": ""}, {"name":"July", "sel": ""}, {"name": current_month, "sel": "selected"}]
    for item in data:
        if item["name"] == place:
            item["sel"] = "selected"
    
    for item in months:
        if item["name"] == date:
            item["sel"] = "selected"

    text = place + " in " + date + " 2024"

    direc = "satellite_images/{}_{}.png".format(place, date)
    with open(direc, "rb") as image_file:
        image = base64.b64encode(image_file.read())
    image = image.decode('utf-8')
    return render_template('satellite.html', data=data, image_file=image, months=months, text=text)

@app.route('/current_status.html')
def current_status():
    # Logic to fetch and display current satellite images for multiple locations
    images = {}
    for city in data:
        city_name = city['name']
        # Assuming images are stored in a specific format
        direc = f"satellite_images/{city_name}_current.png"
        try:
            with open(direc, "rb") as image_file:
                image = base64.b64encode(image_file.read())
                images[city_name] = image.decode('utf-8')
        except FileNotFoundError:
            images[city_name] = None  # Handle missing images

    return render_template('current_status.html', images=images)

@app.route('/predicts.html')
def predicts():
    return render_template('predicts.html', cities=cities, cityname="Information about the city")

@app.route('/predicts.html', methods=["GET", "POST"])
def get_predicts():
    try:
        cityname = request.form["city"]
        cities = [{'name':'Delhi', "sel": ""}, {'name':'Mumbai', "sel": ""}, {'name':'Kolkata', "sel": ""}, {'name':'Bangalore', "sel": ""}, {'name':'Chennai', "sel": ""}, {'name':'New York', "sel": ""}, {'name':'Los Angeles', "sel": ""}, {'name':'London', "sel": ""}, {'name':'Paris', "sel": ""}, {'name':'Sydney', "sel": ""}, {'name':'Beijing', "sel": ""}]
        for item in cities:
            if item['name'] == cityname:
                item['sel'] = 'selected'
        print(cityname)
        URL = "https://geocode.search.hereapi.com/v1/geocode"
        location = cityname
        api_key = 'pPFSt0miNxLZJY6_Zs-h-nB9W1XxxJG6s3wat1L37r8' # Acquire from developer.here.com

        PARAMS = {'apikey':api_key,'q':location} 
        r = requests.get(url = URL, params = PARAMS) 
        print(r)
        data = r.json()
        latitude = data['items'][0]['position']['lat']
        longitude = data['items'][0]['position']['lng']
        print(f"Latitude: {latitude}, Longitude: {longitude}")
        final = prediction.get_data(latitude, longitude)
        
        final[4] *= 15
        if str(model.predict([final])[0]) == "0":
            pred = "Safe"
        else:
            pred = "Unsafe"
        
        return render_template('predicts.html', cityname="Information about " + cityname, cities=cities, temp=round(final[0], 2), maxt=round(final[1], 2), wspd=round(final[2], 2), cloudcover=round(final[3], 2), percip=round(final[4], 2), humidity=round(final[5], 2), pred = pred)
    except:
        return render_template('predicts.html', cities=cities, cityname="Oops, we weren't able to retrieve data for that city.")

if __name__ == "__main__":
    app.run(debug=True)
