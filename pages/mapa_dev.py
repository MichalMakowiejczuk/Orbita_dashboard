import streamlit as st
import gpxpy
import pandas as pd
import folium
import math
import numpy as np
from streamlit_folium import st_folium
from folium.plugins import AntPath
from scripts.gpx_parser import GPXParser
from scripts.elevation_profile import ElevationProfile

def compute_slopes(df):
    slopes_df = (
        df.groupby("segment")
        .agg(start_km=("km", "first"),
            end_km=("km", "last"),
            start_elev=("elevation", "first"),
            end_elev=("elevation", "last"))
        .assign(slope=lambda df: np.where(
            df["end_km"] == df["start_km"], 0,
            (df["end_elev"] - df["start_elev"]) / ((df["end_km"] - df["start_km"]) * 1000) * 100
        ))
        .reset_index()[["segment", "slope"]]
    )
    df = df.merge(slopes_df, on="segment", how="left")
    return df

# coords z GPX
parser = GPXParser("data/track/orbita25.gpx")
track_df = parser.parse_to_dataframe()
track_df["segment"] = (track_df["km"] // 0.5).astype(int)
track_df = compute_slopes(track_df)

# Bufet 
bufet_latlon = [50.716720597663816, 19.01338864353129]

#### Mapa z trasą ####
st.title("Mapa Trasy Maratonu Kolarskiego")

def slope_to_color(slope):
    if slope < 2:
        return "green"
    elif slope < 4:
        return "yellow"
    elif slope < 5:
        return "orange"
    elif slope < 8:
        return "orangered"
    else:
        return "maroon"

start_coords = (track_df.iloc[0]['latitude'], track_df.iloc[0]['longitude'])
m = folium.Map(location=start_coords, zoom_start=12)

# Warstwa klasyczna linia
classic_line = folium.FeatureGroup(name="Klasyczna linia")
folium.PolyLine(
    list(zip(track_df["latitude"], track_df["longitude"])),
    color="grey",
    weight=9,
    opacity=0.7
).add_to(classic_line)
classic_line.add_to(m)

# Warstwa kolorowana wg nachylenia
colored_line = folium.FeatureGroup(name="Linia kolorowana nachyleniem")

lines = []
current_color = None
current_coords = []

for segment, seg_df in track_df.groupby("segment"):
    slope = seg_df["slope"].iloc[0]
    color = slope_to_color(slope)
    coords = list(zip(seg_df["latitude"], seg_df["longitude"]))
    
    if color == current_color:
        # dodajemy do obecnej linii
        current_coords.extend(coords[1:])  # unikamy powtarzania punktu łączenia
    else:
        # zapisz poprzednią linię
        if current_coords:
            lines.append((current_color, current_coords))
        # rozpocznij nową linię
        current_color = color
        current_coords = coords

# dodaj ostatnią linię
if current_coords:
    lines.append((current_color, current_coords))

# rysowanie połączonych linii
for color, coords in lines:
    folium.PolyLine(coords, color=color, weight=6, opacity=0.9).add_to(colored_line)

colored_line.add_to(m)

# Dodaj kontrolkę warstw
folium.LayerControl(collapsed=False).add_to(m)

# Dodaj JS wymuszający radio buttons (tylko jedna warstwa włączona)
m.get_root().html.add_child(folium.Element("""
<script>
document.addEventListener('DOMContentLoaded', function() {
    let inputs = document.querySelectorAll('.leaflet-control-layers-selector');
    inputs.forEach(function(input) {
        input.type = 'radio';
        input.name = 'base_layers';  // nadaj im tę samą nazwę
    });
});
</script>
"""))

# Wyświetl mapę
st_folium(m, width=700, height=500)

