import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import AntPath
from scripts.gpx_parser import GPXParser
from scripts.elevation_profile import ElevationProfile


# coords z GPX
parser = GPXParser("data/track/orbita25.gpx")
df = parser.parse_to_dataframe()
coords = df[['latitude', 'longitude']].values.tolist()

# Bufet 
bufet_latlon = [50.716720597663816, 19.01338864353129]

#### Mapa z trasą ####
st.title("Trasa Orbity'25 - Maratonu Kolarskiego")

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
folium.Marker(
    location=coords[0],
    popup="Start / Meta",
    tooltip="Start i Meta",
    icon=folium.Icon(color="green", icon="bicycle", prefix="fa")
).add_to(m)

# Bufet z ikonką jedzenia
folium.Marker(
    location=bufet_latlon,
    popup="Bufet",
    tooltip="Słodki bufet",
    icon=folium.Icon(color="orange", icon="cutlery", prefix="fa")
).add_to(m)

ElevationProfile = ElevationProfile(df, seg_unit_km=0.5)
lengths = ElevationProfile.compute_slope_lengths(smooth_window=5, slope_thresholds=(2, 4, 5, 8))
lengths.rename(columns={'length_km': 'ilość km', 'slope_range': 'nachylenie'}, inplace=True)


col1, col2 = st.columns([1, 3])

with col1:
    st.metric("Długość trasy", f"{round(df['km'].max(), 2)} km")
    st.metric('Suma podjazdów', f"{round(parser.get_total_ascent(), 2)} m")
    st.metric("Najwyższy punkt", f"{round(df['elevation'].max(), 2)} m")
    st.metric("Najniższy punkt", f"{round(df['elevation'].min(), 2)} m")
    st.write("### Długości segmentów według nachylenia")
    st.dataframe(lengths, hide_index=True)

with col2:
    # mapa z trasą
    #st_data = st_folium(m, width='100%', height='500px')
    with open("static/mapa_orbity.html", "r", encoding="utf-8") as f:
        mapa_html = f.read()

    # Wyświetlenie mapy w Streamlit za pomocą komponentu html
    st.components.v1.html(mapa_html, height=400, width=2000)
    # profif wysokości - obraz
    st.image("static/elevation_profile.png", caption="Profil wysokościowy trasy")