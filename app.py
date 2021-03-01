import streamlit as st
import requests
import datetime
from Tools.utils import geocoder_here
from PIL import Image
import pandas as pd


st.set_page_config(
    page_title="NYC TaxiFare", # => NYC TaxiFare Prediction - Streamlit
    page_icon="🚕️",
    layout="wide", # wide
    initial_sidebar_state="auto") # collapsed

_, title1, title2 = st.beta_columns([1.75,0.5,5])
image = Image.open('images/lewagon.png')
with title1:
    st.image(image, caption="Le Wagon", width=64, use_column_width=None)
with title2:
    st.title("NYC TaxiFare - Batch #469 Lisbon")

st.markdown("")


map_df = pd.DataFrame({
    "lat": [40.71782, 40.73451],
    "lon": [-74.00547, -73.99853]
    })



st.sidebar.markdown("_Fill the information form below to get a New York City Taxi Fare Prediction_")
st.sidebar.markdown("### Datetime")

### Request Date of the course ###
date_col1, date_col2  = st.sidebar.beta_columns([1.75,1])
with date_col1:
    d = st.date_input("Date :", datetime.datetime.now())

### Request Time of the course ###
with date_col2:
    t = st.time_input('Time :', datetime.datetime.now())

### Format the datetime for our API ###
pickup_datetime = f"{d} {t} UTC"

### Display the Pickup Datetime ###
#st.sidebar.success(f'Pickup datetime : {pickup_datetime}')

### Request the Pickup location ###
st.sidebar.markdown("### Pickup Location")
pickup_adress = st.sidebar.text_input("Please enter the pickup address", "Central Park, NewYork")

### Getting Coordinates from Address locations ###
error1 = ""

try:
    pickup_coords = geocoder_here(pickup_adress)
except IndexError:
    error1 = "Pickup Address invalide, default coordinates : "
    pickup_coords = {
        "latitude": 40.78392,
        "longitude": -73.96584
    }


pickup_latitude = pickup_coords['latitude']
pickup_longitude = pickup_coords['longitude']
map_df.loc[0, "lat"] = float(pickup_latitude)
map_df.loc[0, "lon"] = float(pickup_longitude)

### Displaying the Pickup Coordinates ###
if error1 == "":
    st.sidebar.success(f'Lat: {pickup_latitude}, Lon : {pickup_longitude}')
else:
    st.sidebar.error(f'"{pickup_adress}" {error1} \n Lat : {pickup_latitude}, Lon : {pickup_longitude}')


### Request the Dropoff location ###
st.sidebar.markdown("### Dropoff Location")
dropoff_address = st.sidebar.text_input("Please enter the dropoff address", "JFK, NewYork")

### Getting Coordinates from Address locations ###
error2 = ""
try:
    dropoff_coords = geocoder_here(dropoff_address)
except IndexError:
    error2 = "Dropoff Address invalide, default coordinates : "
    dropoff_coords = {
        "latitude": 40.65467,
        "longitude": -73.78911
    }

dropoff_latitude = dropoff_coords['latitude']    
dropoff_longitude = dropoff_coords['longitude']

map_df.loc[1, "lat"] = float(dropoff_latitude)
map_df.loc[1, "lon"] = float(dropoff_longitude)

### Displaying the Pickup Coordinates ###
if error2 == "":
    st.sidebar.success(f'Lat : {dropoff_latitude}, Lon : {dropoff_longitude}')
else:
    st.sidebar.error(f'"{dropoff_address}" {error2} Lat: {dropoff_latitude}, Lon: {dropoff_longitude}')

### Request the Passenger Count ###
st.sidebar.markdown("### Passengers")
passenger_count = st.sidebar.slider('Please enter number of passengers', 1, 9, 1)

### Launch Fare Prediction ###
st.sidebar.markdown("### Prediction")
if st.sidebar.button('Get Fare Prediction'):

    params = {
        "key" : str(pickup_datetime),
        "pickup_datetime" : str(pickup_datetime),
        "pickup_longitude": float(pickup_longitude),
        "pickup_latitude": float(pickup_latitude),
        "dropoff_longitude" : float(dropoff_longitude),
        "dropoff_latitude": float(dropoff_latitude),
        "passenger_count": int(passenger_count)
    }   
    local_api_url = f"http://127.0.0.1:8000/predict_fare"
    cloud_url = "https://predict-api-vwdzl6iuoa-ew.a.run.app/predict_fare"
    response = requests.get(
    url=cloud_url, params=params
    ).json()

    st.info(f"Taxi Fare Predication from {pickup_adress} to {dropoff_address} : {round(response['prediction'], 2)}$ 🎉")

st.map(data=map_df, use_container_width=False)
