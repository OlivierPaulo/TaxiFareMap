import streamlit as st
import requests
import datetime
from Tools.utils import geocoder_here, haversine2
from PIL import Image
import pandas as pd
from streamlit_folium import folium_static
import folium
import math
import time

st.set_page_config(
    page_title="NYC TaxiFare", # => NYC TaxiFare Prediction - Streamlit
    page_icon="🚕️",
    layout="wide", # wide
    initial_sidebar_state="auto") # collapsed

_, title1, title2 = st.columns([1.75,0.5,5])
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

st.sidebar.markdown("### Datetime")

### Request Date of the course ###
date_col1, date_col2  = st.sidebar.columns([1.6,1.2])
with date_col1:
    d = st.date_input("When?", datetime.datetime.now())

### Request Time of the course ###
with date_col2:
    t = st.time_input("What time?", datetime.datetime.now())

### Format the datetime for our API ###
pickup_datetime = f"{d} {t} UTC"

### Display the Pickup Datetime ###
#st.sidebar.success(f'Pickup datetime : {pickup_datetime}')

### Request the Pickup location ###
st.sidebar.markdown("### Pickup Location")
pickup_adress = st.sidebar.text_input("Where are you?", "Central Park, NewYork")

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
dropoff_address = st.sidebar.text_input("Where are you going?", "JFK, NewYork")

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
# st.sidebar.markdown("### Passengers")
# passenger_count = st.sidebar.slider('Please enter number of passengers', 1, 9, 1)
passenger_count = 1
st.sidebar.markdown("_Not alone? Don't worries, we will drive you and your buddies for the same price!_ 😎️")

hav_df = {
    "pickup_latitude":pickup_latitude,
    "pickup_longitude":pickup_longitude,
    "dropoff_latitude":dropoff_latitude,
    "dropoff_longitude":dropoff_longitude
}

drive_distance = haversine2(hav_df)
zoom_distance = math.log2(drive_distance)

### Launch Fare Prediction ###
if st.sidebar.button("Let's Go! 🚕️💨️"):
    

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
    my_bar = st.sidebar.progress(0)
    for percent_complete in range(100):
        time.sleep(0.01)
        my_bar.progress(percent_complete + 1)
    with st.spinner(f"Driving Distance : {round(drive_distance, 2)}kms"):
        time.sleep(2)
    
    st.info(f"This drive from {pickup_adress} to {dropoff_address} will cost {round(response['prediction'], 2)}$ 💸️")


#### FOLIUM MAP ####
init_lat = (map_df.loc[1, 'lat']+map_df.loc[0, 'lat'])/2
init_lon = (map_df.loc[1, 'lon']+map_df.loc[0, 'lon'])/2


m = folium.Map(location=[init_lat, init_lon], max_bounds=True, zoom_start=15-zoom_distance, min_zoom = 2, max_zoom=20)

folium.TileLayer('OpenStreetMap').add_to(m)
folium.TileLayer('Stamenterrain').add_to(m)
folium.TileLayer('StamenToner').add_to(m)
folium.TileLayer('Cartodbpositron').add_to(m)
folium.TileLayer('Cartodbdark_matter').add_to(m)

folium.LayerControl().add_to(m)

folium.Marker(
    location=[map_df.loc[0, 'lat'], map_df.loc[0, 'lon']], 
    popup=f"Where you are 😉️",
    icon=folium.Icon(icon="flag", color="green", prefix='fa'),
    tooltip=pickup_adress
).add_to(m)

folium.Marker(
    location=[map_df.loc[1, 'lat'], map_df.loc[1, 'lon']], 
    popup=f"Where you go 🙂️",
    icon=folium.Icon(icon="flag-checkered", color="black", prefix='fa'),
    tooltip=dropoff_address
).add_to(m)

folium.PolyLine([(map_df.loc[0, 'lat'],map_df.loc[0, 'lon']),(map_df.loc[1, 'lat'], map_df.loc[1, 'lon'])], color="blue", weight=3, opacity=0.35).add_to(m)

folium_static(m, width=1209, height=500)

