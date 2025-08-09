import streamlit as st
from scripts.preprocess import load_data

# --- Funkcje pomocnicze ---
def format_value(value, total, mode):
    """Formatuje wartość jako liczba lub procent."""
    if mode == "Procenty" and total > 0:
        return f"{(value / total * 100):.1f}%"
    return value

def responsive_metrics(metrics, cols_per_row=3):
    """Wyświetla metryki w układzie responsywnym."""
    for i in range(0, len(metrics), cols_per_row):
        row = st.columns(cols_per_row)
        for col, (label, value) in zip(row, metrics[i:i+cols_per_row]):
            col.metric(label, value)

# --- Wczytanie danych ---
df = load_data()

st.title("📊 Statystyki z zawodów")

# --- Filtry boczne ---
plec = st.sidebar.pills(
    "Płeć", options=df["plec"].unique(),
    default=df["plec"].unique(), selection_mode="multi"
)
pora = st.sidebar.pills(
    "Pora startu", options=df["pora_startu"].unique(),
    default=df["pora_startu"].unique(), selection_mode="multi"
)
typ = st.sidebar.pills(
    "Typ uczestnika", options=df["typ_uczestnika"].unique(),
    default=df["typ_uczestnika"].unique(), selection_mode="multi"
)

# --- Filtrowanie wstępne ---
df_filtered = df.query(
    "plec in @plec and pora_startu in @pora and typ_uczestnika in @typ"
)

# --- Tryb wyświetlania ---
view_mode = st.radio("Tryb wyświetlania", ["Liczby", "Procenty"], horizontal=True)

# --- Liczby organizacyjne ---
total_ucz = len(df_filtered)
org_metrics = [
    ("Liczba zapisanych", format_value(len(df_filtered), total_ucz, view_mode)),
    ("DNS (nie wystartowali)", format_value(df_filtered["DNS"].sum(), total_ucz, view_mode)),
    ("Wystartowali", format_value((~df_filtered["DNS"]).sum(), total_ucz, view_mode))
]
responsive_metrics(org_metrics, cols_per_row=3)

# --- Uwzględnianie DNS ---
if not st.toggle("Uwzględnij DNS w analizie", value=True):
    df_filtered = df_filtered[df_filtered["DNS"] == False]

total_ucz = len(df_filtered)  # aktualizacja po filtrze DNS

# --- Metryki analityczne ---
okr_left = [2, 4]
okr_right = [1, 3, 5]

metrics_left = [
    ("Liczba deklarowanych okrążeń", format_value(df_filtered["deklarowane"].sum(), total_ucz, view_mode)),
    ("Średnia deklarowanych okrążeń", round(df_filtered["deklarowane"].mean(), 1)),
    ("Całkowity dystans [km]", round(df_filtered["dystans_km"].sum(), 1)),
    ("Mniej niż 1 okrążenie", format_value(df_filtered["mniej_niz_1_orbita"].sum(), total_ucz, view_mode))
] + [
    (f"{o} okrążenia", format_value(df_filtered["zrobione_pelne"].eq(o).sum(), total_ucz, view_mode))
    for o in okr_left
]

metrics_right = [
    ("Liczba wykręconych okrążeń", format_value(df_filtered["zrobione_pelne"].sum(), total_ucz, view_mode)),
    ("Średnia zrobionych okrążeń", round(df_filtered["zrobione"].mean(), 1)),
    ("Średni dystans [km]", round(df_filtered["dystans_km"].mean(), 1))
] + [
    (f"{o} okrążenia", format_value(df_filtered["zrobione_pelne"].eq(o).sum(), total_ucz, view_mode))
    for o in okr_right
]

# Wyświetlenie w dwóch kolumnach
col1, col2 = st.columns(2)
with col1:
    for label, val in metrics_left:
        col1.metric(label, val)
with col2:
    for label, val in metrics_right:
        col2.metric(label, val)
