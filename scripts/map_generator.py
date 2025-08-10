import streamlit as st
import pandas as pd
import folium
import base64
from streamlit_folium import st_folium
from folium.plugins import AntPath
from gpx_parser import GPXParser
from elevation_profile import ElevationProfile


# coords z GPX
parser = GPXParser("data/track/orbita25.gpx")
df = parser.parse_to_dataframe()
coords = df[['latitude', 'longitude']].values.tolist()

# Bufet 
BUFET_LATLON = [50.716720597663816, 19.01338864353129]

#### Mapa z trasą ####
st.title("Mapa Trasy Maratonu Kolarskiego")

# Tworzymy mapę w centrum trasy
m = folium.Map(location=coords[0], zoom_start=10, tiles="OpenStreetMap")

# Animowana linia trasy
AntPath(
    coords,
    color="blue",
    weight=5,
    delay=2000,
    dash_array=[10, 100],
    pulse_color="red"
).add_to(m)

# Start/meta z ikonką roweru
with open("static/start_meta.jpg", "rb") as img_file:
    b64_img = base64.b64encode(img_file.read()).decode()

start_meta_img = f'<img src="data:image/jpg;base64,{b64_img}" width="200" />'

folium.Marker(
    location=coords[0],
    popup=folium.Popup(start_meta_img, max_width=300),
    tooltip="Start i Meta",
    icon=folium.Icon(color="green", icon="bicycle", prefix="fa")
).add_to(m)

# Bufet z ikonką jedzenia
with open("static/bufet.jpg", "rb") as img_file:
    b64_img = base64.b64encode(img_file.read()).decode()

bufet_img = f'<img src="data:image/jpg;base64,{b64_img}" width="200" />'

folium.Marker(
    location=BUFET_LATLON,
    popup=folium.Popup(bufet_img, max_width=300),
    tooltip="Słodki bufet",
    icon=folium.Icon(color="orange", icon="cutlery", prefix="fa")
).add_to(m)



m.save("static/mapa_orbity.html")