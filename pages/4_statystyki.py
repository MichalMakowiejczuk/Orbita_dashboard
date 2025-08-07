import streamlit as st
from scripts.preprocess import load_data

df = load_data()


st.title("📊 Statystyki z zawodów")

# Filtry
# plec = st.sidebar.multiselect("Płeć", options=df["plec"].unique(), default=df["plec"].unique())
# pora = st.sidebar.multiselect("Pora startu", options=df["pora_startu"].unique(), default=df["pora_startu"].unique())
# typ = st.sidebar.multiselect("Typ uczestnika", options=df["typ_uczestnika"].unique(), default=df["typ_uczestnika"].unique())

plec = st.sidebar.pills("Płeć", options=df["plec"].unique(), default=df["plec"].unique(), selection_mode="multi")
pora = st.sidebar.pills("Pora startu", options=df["pora_startu"].unique(), default=df["pora_startu"].unique(), selection_mode="multi")
typ = st.sidebar.pills("Typ uczestnika", options=df["typ_uczestnika"].unique(), default=df["typ_uczestnika"].unique(), selection_mode="multi")

# Zastosuj filtry
filtered_df_without_dns = df[
    (df["plec"].isin(plec)) &
    (df["pora_startu"].isin(pora)) &
    (df["typ_uczestnika"].isin(typ)) &
    (df["DNS"] == False)  # Wyklucz DNS
]

filtered_df_with_dns = df[
    (df["plec"].isin(plec)) &
    (df["pora_startu"].isin(pora)) &
    (df["typ_uczestnika"].isin(typ))
]

st.metric("Liczba zapisanych", len(filtered_df_with_dns))
st.metric("Liczba DNS", filtered_df_with_dns["DNS"].sum())

st.metric("Liczba deklarowanych okrążeń", filtered_df_without_dns["deklarowane"].sum())
st.metric("Liczba wykręconych okrążeń", filtered_df_without_dns["zrobione_pelne"].sum())

st.metric("Średnia liczba deklarowanych okrążeń", round(filtered_df_without_dns["deklarowane"].mean(), 1))
st.metric("Średnia liczba zrobionych okrążeń", round(filtered_df_without_dns["zrobione"].mean(), 1))

st.metric("Całkowity dystans [km]", round(filtered_df_without_dns["dystans_km"].sum(), 1))
st.metric("Średni dystans [km]", round(filtered_df_without_dns["dystans_km"].mean(), 1))

st.metric("Liczba osób które zrobiły mniej niż 1 okrążenie", filtered_df_without_dns["mniej_niz_1_orbita"].sum())
st.metric("Liczba osób które zrobiły 1 okrążenie", filtered_df_without_dns["zrobione_pelne"].eq(1).sum())

st.metric("Liczba osób które zrobiły 2 okrążenia", filtered_df_without_dns["zrobione_pelne"].eq(2).sum())
st.metric("Liczba osób które zrobiły 3 okrążenia", filtered_df_without_dns["zrobione_pelne"].eq(3).sum())

st.metric("Liczba osób które zrobiły 4 okrążenia", filtered_df_without_dns["zrobione_pelne"].eq(4).sum())
st.metric("Liczba osób które zrobiły 5 okrążeń", filtered_df_without_dns["zrobione_pelne"].eq(5).sum())
#st.metric("Średni % wykonania", round(filtered_df["% wykonania"].mean(), 1))
