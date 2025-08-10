import streamlit as st
from scripts.preprocess import load_data

st.set_page_config(
    page_title="Orbita'25 - Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🚴‍♂️ Dashboard Maratonu Kolarskiego")

st.markdown("""
Witaj w interaktywnym dashboardzie podsumowującym lokalny maraton kolarski.

W menu po lewej stronie możesz nawigować między:
- Opisem wydarzenia
- Statystykami z wyników
- Rankingiem top 10 zawodników
- Listą wszystkich uczestników

Dane pochodzą z rzeczywistego wydarzenia i zostały przetworzone na potrzeby tej aplikacji.
""")
