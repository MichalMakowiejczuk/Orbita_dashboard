import streamlit as st
from scripts.gpx_parser import GPXParser
from scripts.elevation_profile import ElevationProfile

# --- Footer ---
st.sidebar.markdown("Made with ❤️ by Michał Makowiejczuk")

# GPX coords 
parser = GPXParser("data/track/orbita25.gpx")
df = parser.parse_to_dataframe()
coords = df[['latitude', 'longitude']].values.tolist()

# bufet coords
bufet_latlon = [50.716720597663816, 19.01338864353129]

st.title("Trasa Orbity'25 (jedna pętla)")

# slopes dataframe
ElevationProfile = ElevationProfile(df, seg_unit_km=0.5)
lengths = ElevationProfile.compute_slope_lengths(smooth_window=5, slope_thresholds=(2, 4, 5, 8))
lengths.rename(columns={'length_km': 'Długość [km]', 'slope_range': 'Nachylenie'}, inplace=True)
lengths["Długość [km]"] = lengths["Długość [km]"].round(1)
color_map = {
    "< 2%": "lightgreen",
    "2 ~ 4%": "yellow",
    "4 ~ 5%": "orange",
    "5 ~ 8%": "orangered",
    ">= 8%": "maroon"
}
def color_cells(val):
    return f"background-color: {color_map.get(val, 'white')}; color: black;"
styled_df = (
    lengths.style
    .applymap(color_cells, subset=["Nachylenie"])
    .format("{:.1f}", subset=["Długość [km]"])
)

col1, col2 = st.columns([1, 3])

with col1:
    st.metric("Długość trasy", f"{round(df['km'].max(), 2)} km")
    st.metric('Suma podjazdów', f"{round(parser.get_total_ascent(), 2)} m")
    st.metric("Najwyższy punkt na trasie", f"{round(df['elevation'].max(), 2)} m n.p.m.")
    st.metric("Najniższy punkt na trasie", f"{round(df['elevation'].min(), 2)} m n.p.m.")
    st.write("## Długości segmentów według nachylenia")
    st.dataframe(styled_df, hide_index=True)

    file_path = "./data/track/orbita25.gpx"
    with open(file_path, "rb") as f:
        gpx_data = f.read()

    # download button for GPX file
    st.download_button(
        label="Pobierz trasę GPX",
        data=gpx_data,
        file_name="orbita25.gpx",
        mime="application/gpx+xml"  # typ MIME - GPX
    )

with col2:
    # map
    with open("static/mapa_orbity.html", "r", encoding="utf-8") as f:
        mapa_html = f.read()

    st.components.v1.html(mapa_html, height=400, width=2000)

    # elevation profile img
    st.image("static/elevation_profile.png", caption="Profil wysokościowy trasy")

