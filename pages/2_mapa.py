import streamlit as st
import gpxpy
import pandas as pd
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
from haversine import haversine
from scripts.elevation_profile import ElevationProfile

# --- Ścieżka do pliku GPX ---
GPX_FILE_PATH = "data/track/orbita25.gpx"

# --- Parsowanie GPX ---
def parse_gpx(file_path):
    with open(file_path, 'r', encoding='utf-8') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    data = []
    total_distance = 0
    prev_point = None

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                if prev_point:
                    dist = haversine(
                        (prev_point.latitude, prev_point.longitude),
                        (point.latitude, point.longitude)
                    )
                    total_distance += dist
                else:
                    dist = 0
                data.append({
                    "lat": point.latitude,
                    "lon": point.longitude,
                    "elevation": point.elevation,
                    "distance_km": total_distance
                })
                prev_point = point

    return pd.DataFrame(data)

# --- Wczytaj dane ---
df = parse_gpx(GPX_FILE_PATH)

# --- Mapa z trasą ---
st.title("📍 Mapa Trasy i Profil Wysokości")

st.subheader("🗺️ Trasa na mapie (Folium)")

center = [df["lat"].mean(), df["lon"].mean()]
m = folium.Map(location=center, zoom_start=13)

# Dodaj linię trasy
folium.PolyLine(df[["lat", "lon"]].values, color="blue", weight=5, opacity=0.8).add_to(m)

# Początek i koniec trasy
folium.Marker(
    location=[df.iloc[0]["lat"], df.iloc[0]["lon"]],
    popup="Start",
    icon=folium.Icon(color="green")
).add_to(m)

folium.Marker(
    location=[df.iloc[-1]["lat"], df.iloc[-1]["lon"]],
    popup="Meta",
    icon=folium.Icon(color="red")
).add_to(m)

# Wyświetl mapę w Streamlit
st_folium(m, width=700, height=500)

# --- mapa trasy 2 ---

gpx_path = "data/track/orbita25.gpx"

profile = ElevationProfile(gpx_path, 
                            seg_unit_km=0.5
                            ).parse_gpx()

coords = list(zip(profile.track_df['latitude'], profile.track_df['longitude']))

# Utwórz mapę na środku pierwszego punktu
m2 = folium.Map(location=coords[0], zoom_start=13)

# Dodaj trasę jako polilinię
folium.PolyLine(coords, color='blue', weight=5, opacity=0.7).add_to(m2)

st_folium(m2, width=700, height=500)