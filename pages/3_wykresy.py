import streamlit as st
from scripts.preprocess import load_data
import plotly.express as px
import plotly.graph_objects as go

# Load data
df = load_data()

st.title("Dashboard Maratonu Kolarskiego")

plec = st.sidebar.pills("Płeć", options=df["plec"].unique(),
                        default=df["plec"].unique(), selection_mode="multi")
pora = st.sidebar.pills("Pora startu", options=df["pora_startu"].unique(),
                        default=df["pora_startu"].unique(), selection_mode="multi")
typ = st.sidebar.pills("Typ uczestnika", options=df["typ_uczestnika"].unique(),
                       default=df["typ_uczestnika"].unique(), selection_mode="multi")

df_filtered = df.query("plec in @plec and pora_startu in @pora and typ_uczestnika in @typ")

if df_filtered.empty:
    st.warning("Brak danych dla wybranych filtrów")
else:
    def plotly_pie(df, column, title):
        counts = df[column].value_counts().reset_index()
        counts.columns = [column, 'count']
        counts['percent'] = counts['count'] / counts['count'].sum()
        
        # etykieta: nazwa + procent
        counts['label'] = counts[column] + ': ' + (counts['percent'] * 100).round(1).astype(str) + '%'

        dark_contrast_colors = [
            "#FF4B4B",  # czerwony
            "#4B9EFF",  # jasny niebieski
            "#2ECC71",  # zieleń
            "#9B4BFF",  # fiolet
            "#FFD700",  # złoty
            "#00CED1"   # turkus
        ]

        fig = px.pie(
            counts,
            values='count',
            names='label',  # używamy przygotowanej etykiety
            title=title,
            hole=0.4,
            color_discrete_sequence=dark_contrast_colors
        )

        fig.update_traces(
            textposition='inside',
            textinfo='label',  # tylko nasza etykieta
            textfont_size=18,
            textfont_color='white',
            marker=dict(line=dict(color='#000000', width=2))
        )

        fig.update_layout(
            showlegend=False,  # legenda zbędna
            paper_bgcolor='rgba(0,0,0,0)',  # transparentne tło
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')  # białe napisy w tytule
        )

        return fig

    def plotly_gauge(df, title):
        # obliczamy średnie wykonanie planu
        if df.empty:
            value = 0
        else:
            value = (df["zrobione_pelne"].sum() / df["deklarowane"].sum()) * 100

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            number={'suffix': '%', 'font': {'color': 'white', 'size': 48}},
            title={'text': title, 'font': {'color': 'white', 'size': 24}},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': 'white'},
                'bar': {'color': '#FF4B4B', 'thickness': 1},  # czerwony pasek postępu
                'bgcolor': "#FF9797",         # wyblakłe tło
                'borderwidth': 0,
                'bordercolor': 'white'
            }
        ))

        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font={'color': 'white'}
        )

        return fig

    col1, col2, col3 = st.columns(3)
    with col1:
        st.plotly_chart(plotly_pie(df_filtered, 'plec', 'Udział uczestników wg płci'), use_container_width=True)
    with col2:
        st.plotly_chart(plotly_pie(df_filtered, 'typ_uczestnika', 'Udział wg typu uczestnika'), use_container_width=True)
    with col3:
        st.plotly_chart(plotly_pie(df_filtered, 'pora_startu', 'Udział wg pory startu'), use_container_width=True)

    # Dodatkowy wykres słupkowy - liczba zrobionych pełnych okrążeń
    okr_data = df_filtered["zrobione_pelne"].value_counts().reset_index()
    okr_data.columns = ["Okrążenia", "Liczba"]

    bar_fig = px.bar(okr_data, x="Okrążenia", y="Liczba",
                     title="Liczba uczestników wg liczby zrobionych okrążeń",
                     labels={"Okrążenia": "Liczba okrążeń", "Liczba": "Ilość uczestników"},
                     color_discrete_sequence=["#FF4B4B"])

    col1, col2 = st.columns([2, 1])
    with col1:
        st.plotly_chart(bar_fig, use_container_width=True)
    with col2:
        st.plotly_chart(plotly_gauge(df_filtered, "Średnia realizacja deklarowanych okrążeń [%]"), use_container_width=True)