import streamlit as st
import numpy as np
from scripts.preprocess import load_data

def format_value(value, total, mode):
    if mode == "Procenty" and total > 0:
        return f"{(value / total * 100):.1f}%"
    return value

df = load_data()

st.title("Podstawowe Statystyki")

# --- Filtry boczne ---
st.sidebar.header("Filtry")
plec = st.sidebar.pills("Płeć", options=df["plec"].unique(),
                        default=df["plec"].unique(), selection_mode="multi")
pora = st.sidebar.pills("Pora startu", options=df["pora_startu"].unique(),
                        default=df["pora_startu"].unique(), selection_mode="multi")
typ = st.sidebar.pills("Typ uczestnika", options=df["typ_uczestnika"].unique(),
                       default=df["typ_uczestnika"].unique(), selection_mode="multi")

df_filtered = df.query("plec in @plec and pora_startu in @pora and typ_uczestnika in @typ")

# --- Footer ---
st.sidebar.markdown("---")
st.sidebar.markdown("Made with ❤️ by Michał Makowiejczuk")

# --- Toggle obok siebie ---
col_toggle1, col_toggle2 = st.columns(2)

with col_toggle1:
    include_dns = st.toggle("Uwzględnij DNS w analizie", value=False)

with col_toggle2:
    show_percent = st.toggle("Widok procentowy", value=False)

# Ustawienie trybu wyświetlania na podstawie toggle
view_mode = "Procenty" if show_percent else "Liczby"

total_ucz = len(df_filtered)


col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Liczba zapisanych", format_value(len(df_filtered), total_ucz, view_mode))
with col2:
    st.metric("DNS (nie wystartowali)", format_value(df_filtered["DNS"].sum(), total_ucz, view_mode))
with col3:
    st.metric("Wystartowali", format_value((~df_filtered["DNS"]).sum(), total_ucz, view_mode))

if not include_dns:
    df_filtered = df_filtered[df_filtered["DNS"] == False]

total_deklarowane = df_filtered["deklarowane"].sum()

okr_left = [2, 4]
okr_right = [1, 3, 5]

metrics_left = [
    ("Deklarowane okrążenia", format_value(total_deklarowane, total_deklarowane, view_mode)),
    ("Średnia liczba deklarowanych okrążeń na uczestnika", round(df_filtered["deklarowane"].mean(), 1)),
    ("Mniej niż 1 okrążenie", format_value(df_filtered["mniej_niz_1_orbita"].sum() + df_filtered["DNS"].sum(), total_ucz, view_mode))
] + [
    (f"{o} okrążenia", format_value(df_filtered["zrobione_pelne"].eq(o).sum(), total_ucz, view_mode))
    for o in okr_left
]

metrics_right = [
    ("Wykręcone okrążenia", format_value(df_filtered["zrobione_pelne"].sum(), total_deklarowane, view_mode)),
    ("Średnia liczba zrobionych okrążeń na uczestnika", round(df_filtered["zrobione"].mean(), 1)),
] + [
    (f"{o} okrążenia", format_value(df_filtered["zrobione_pelne"].eq(o).sum(), total_ucz, view_mode))
    for o in okr_right
]

tab1, tab2, tab3 = st.tabs(["Statystyki okrążeń", "Statystyki dystansu", "Ranking"])
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        for label, val in metrics_left:
            st.metric(label, val)
    with col2:
        for label, val in metrics_right:
            st.metric(label, val)


with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Średni dystans na uczestnika", f"{round(df_filtered["dystans_km"].mean(), 2)} km")
    with col2:
        st.metric("Suma dystansu wszystkich uczestników", f"{round(df_filtered["dystans_km"].sum(), 2)} km")

with tab3:
    df_rank = df_filtered.sort_values(["dystans_km", "nr_startowy"], ascending=[False, True])
    df_rank.index = np.arange(1, len(df_rank) + 1) 
    df_rank.index.name = "Pozycja (z filtrem)"       

    st.dataframe(df_rank[['Pozycja globalna' ,'nr_startowy', 'nick', 'dystans_km', 'zrobione_pelne']])

