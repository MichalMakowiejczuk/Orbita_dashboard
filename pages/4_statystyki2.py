import streamlit as st
import altair as alt
from scripts.preprocess import load_data

# --- Funkcje pomocnicze ---
def format_value(value, total, mode):
    if mode == "Procenty" and total > 0:
        return f"{(value / total * 100):.1f}%"
    return value

# --- Wczytanie danych ---
df = load_data()

st.title("📊 Statystyki z zawodów")

st.sidebar.header("Filtry")

plec = st.sidebar.multiselect("Płeć", options=df["plec"].unique(),
                              default=df["plec"].unique())
pora = st.sidebar.multiselect("Pora startu", options=df["pora_startu"].unique(),
                              default=df["pora_startu"].unique())
typ = st.sidebar.multiselect("Typ uczestnika", options=df["typ_uczestnika"].unique(),
                             default=df["typ_uczestnika"].unique())

df_filtered = df.query("plec in @plec and pora_startu in @pora and typ_uczestnika in @typ")

include_dns = st.sidebar.checkbox("Uwzględnij DNS w analizie", value=False)
show_percent = st.sidebar.checkbox("Widok procentowy", value=False)

view_mode = "Procenty" if show_percent else "Liczby"
total_ucz = len(df_filtered)

st.header("Podstawowe statystyki")

col1, col2, col3 = st.columns([1,1,1])
with col1:
    st.metric("Liczba zapisanych", format_value(len(df_filtered), total_ucz, view_mode))
with col2:
    st.metric("DNS (nie wystartowali)", format_value(df_filtered["DNS"].sum(), total_ucz, view_mode))
with col3:
    st.metric("Wystartowali", format_value((~df_filtered["DNS"]).sum(), total_ucz, view_mode))

if not include_dns:
    df_filtered = df_filtered[df_filtered["DNS"] == False]

st.write("---")
st.header("Dane o okrążeniach")

total_deklarowane = df_filtered["deklarowane"].sum()
okr_left = [2, 4]
okr_right = [1, 3, 5]

metrics_left = [
    ("Deklarowane okrążenia", format_value(total_deklarowane, total_deklarowane, view_mode)),
    ("Średnia liczba deklarowanych okrążeń na uczestnika", round(df_filtered["deklarowane"].mean(), 1)),
    ("Całkowity dystans [km] wszystkich uczestników", round(df_filtered["dystans_km"].sum(), 1)),
    ("Mniej niż 1 okrążenie", format_value(df_filtered["mniej_niz_1_orbita"].sum() + df_filtered["DNS"].sum(), total_ucz, view_mode))
] + [
    (f"{o} okrążenia", format_value(df_filtered["zrobione_pelne"].eq(o).sum(), total_ucz, view_mode))
    for o in okr_left
]

metrics_right = [
    ("Wykręcone okrążenia", format_value(df_filtered["zrobione_pelne"].sum(), total_deklarowane, view_mode)),
    ("Średnia liczba zrobionych okrążeń na uczestnika", round(df_filtered["zrobione"].mean(), 1)),
    ("Średni dystans [km] na uczestnika", round(df_filtered["dystans_km"].mean(), 1))
] + [
    (f"{o} okrążenia", format_value(df_filtered["zrobione_pelne"].eq(o).sum(), total_ucz, view_mode))
    for o in okr_right
]

col1, col2 = st.columns(2)
with col1:
    for label, val in metrics_left:
        st.metric(label, val, border=True)
with col2:
    for label, val in metrics_right:
        st.metric(label, val, border=True)

# Dodaj wykres
okr_data = df_filtered["zrobione_pelne"].value_counts().reset_index()
okr_data.columns = ["Okrążenia", "Liczba"]

chart = alt.Chart(okr_data).mark_bar(color="#4e79a7").encode(
    x=alt.X("Okrążenia:N", title="Liczba okrążeń"),
    y=alt.Y("Liczba:Q", title="Ilość uczestników"),
    tooltip=["Okrążenia", "Liczba"]
).properties(width=600, height=300)

st.altair_chart(chart)




# realizacja = df_filtered["zrobione"].sum() / df_filtered["deklarowane"].sum() * 100
# st.metric("Realizacja planu [%]", f"{realizacja:.1f}%")
