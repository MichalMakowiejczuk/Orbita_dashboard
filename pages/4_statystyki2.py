import streamlit as st
from scripts.preprocess import load_data
from scripts.utils import metric_box

df = load_data()

st.title("📊 Statystyki z zawodów")

# 🎛️ Filtry boczne
plec = st.sidebar.pills("Płeć", options=df["plec"].unique(), default=df["plec"].unique(), selection_mode="multi")
pora = st.sidebar.pills("Pora startu", options=df["pora_startu"].unique(), default=df["pora_startu"].unique(), selection_mode="multi")
typ = st.sidebar.pills("Typ uczestnika", options=df["typ_uczestnika"].unique(), default=df["typ_uczestnika"].unique(), selection_mode="multi")

# 🔎 Filtrowanie wstępne
df_filtered = df.query(
    "plec in @plec and pora_startu in @pora and typ_uczestnika in @typ"
)

# 📊 Liczby organizacyjne
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Liczba zapisanych", len(df_filtered))
with col2:
    st.metric("DNS (nie wystartowali)", df_filtered["DNS"].sum())
with col3:
    st.metric("Wystartowali", (df_filtered["DNS"] == False).sum())

# ✅ Opcja: uwzględniać DNS?
on = st.toggle("Uwzględnij DNS w analizie")
#uwzglednij_dns = st.checkbox("Uwzględnij DNS w analizie", value=False)

# 👥 Filtrowanie końcowe do analizy
if not on:
    df_filtered = df_filtered[df_filtered["DNS"] == False]

# 🧮 Metryki
col1, col2 = st.columns(2)
with col1:
    st.metric("Liczba deklarowanych okrążeń", df_filtered["deklarowane"].sum())
    st.metric("Średnia liczba deklarowanych okrążeń", round(df_filtered["deklarowane"].mean(), 1))
    st.metric("Całkowity dystans [km]", round(df_filtered["dystans_km"].sum(), 1))
    st.metric("Liczba osób które zrobiły mniej niż 1 okrążenie", df_filtered["mniej_niz_1_orbita"].sum())
    st.metric("Liczba osób które zrobiły 2 okrążenia", df_filtered["zrobione_pelne"].eq(2).sum())
    st.metric("Liczba osób które zrobiły 4 okrążenia", df_filtered["zrobione_pelne"].eq(4).sum())

with col2:
    st.metric("Liczba wykręconych okrążeń", df_filtered["zrobione_pelne"].sum())
    st.metric("Średnia liczba zrobionych okrążeń", round(df_filtered["zrobione"].mean(), 1))
    st.metric("Średni dystans [km]", round(df_filtered["dystans_km"].mean(), 1))
    st.metric("Liczba osób które zrobiły 1 okrążenie", df_filtered["zrobione_pelne"].eq(1).sum())
    st.metric("Liczba osób które zrobiły 3 okrążenia", df_filtered["zrobione_pelne"].eq(3).sum())
    st.metric("Liczba osób które zrobiły 5 okrążeń", df_filtered["zrobione_pelne"].eq(5).sum())




# realizacja = df_filtered["zrobione"].sum() / df_filtered["deklarowane"].sum() * 100
# st.metric("Realizacja planu [%]", f"{realizacja:.1f}%")
