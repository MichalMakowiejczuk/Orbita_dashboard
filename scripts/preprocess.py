import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data
def load_data(path='data/transformed/startlist_transformed.xlsx'):
    df = pd.read_excel(path, sheet_name='clean')

    # feature engineering
    df['DNS'] = df['pora_startu_z_DNS'] == 'DNS'
    df['mniej_niz_1_orbita'] = df['dystans_km'].between(1, 124, inclusive="both")
    df['zrobione_pelne'] = np.floor(df['zrobione']).astype(int)
    df.sort_values(by=['dystans_km', 'nr_startowy'], ascending=[False, True], inplace=True)
    df["Pozycja globalna"] = np.arange(1, len(df) + 1) 

    return df
