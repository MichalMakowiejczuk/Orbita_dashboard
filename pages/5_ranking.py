import streamlit as st
import numpy as np
from scripts.preprocess import load_data


df = load_data()
df = df.sort_values(["dystans_km", "nr_startowy"], ascending=[False, True])

st.title("Ranking")

# 🎛️ Filtry boczne
plec = st.sidebar.pills("Płeć", options=df["plec"].unique(), default=df["plec"].unique(), selection_mode="multi")
pora = st.sidebar.pills("Pora startu", options=df["pora_startu"].unique(), default=df["pora_startu"].unique(), selection_mode="multi")
typ = st.sidebar.pills("Typ uczestnika", options=df["typ_uczestnika"].unique(), default=df["typ_uczestnika"].unique(), selection_mode="multi")

# 🔎 Filtrowanie wstępne
df_filtered = df.query(
    "plec in @plec and pora_startu in @pora and typ_uczestnika in @typ"
)
df_filtered.index = np.arange(1, len(df_filtered) + 1)
df_filtered = df_filtered.rename_axis('Pozycja')


st.table(df_filtered)