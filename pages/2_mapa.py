import streamlit as st
import gpxpy
import pandas as pd
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
from haversine import haversine

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

# --- Profil wysokości ---
# Stylizowany wykres
fig, ax = plt.subplots(figsize=(10, 4))

# Wypełnienie pod profilem
ax.fill_between(df["distance_km"], df["elevation"], color="orangered", alpha=0.7)

# Linia profilu
ax.plot(df["distance_km"], df["elevation"], color="darkred", linewidth=2)

# Stylizacja osi
ax.set_xlabel("Dystans (km)", fontsize=12)
ax.set_ylabel("Wysokość (m)", fontsize=12)
ax.grid(True, linestyle="--", alpha=0.3)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Tytuł
ax.set_title("Profil wysokości trasy", fontsize=16, fontweight='bold')

# Wyświetl w Streamlit
st.pyplot(fig)
