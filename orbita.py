import streamlit as st

st.set_page_config(
    page_title="Orbita'25 - Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PAGE SETUP ---
about_page = st.Page(
    "views/0_Info.py",
    title="Info",
    #icon=":material/account_circle:",
    default=True,
)
project_1_page = st.Page(
    "views/1_Trasa.py",
    title="Trasa i Profil",
    #icon=":material/bar_chart:",
)
project_2_page = st.Page(
    "views/2_Wykresy.py",
    title="Wykresy",
    #icon=":material/smart_toy:",
)
project_3_page = st.Page(
    "views/3_Statystyki.py",
    title="Statystyki",
    #icon=":material/analytics:",
)

pg = st.navigation(
    {
        "About Me": [about_page],
        "Strony": [project_1_page, project_2_page, project_3_page],
    }
)

# --- SIDEBAR ---
st.html("""
  <style>
    [alt=Logo] {
      height: 4rem;
    }
  </style>
        """)
st.logo("static/orbita_logo.png", size="large", icon_image="static/orbita_icon.png")


# --- RUN NAVIGATION ---
pg.run()
