import pandas as pd
import numpy as np

def load_data(path='data/transformed/startlist_transformed.xlsx'):
    df = pd.read_excel(path, sheet_name='clean')

    # Przykładowe nowe kolumny
    #df["% wykonania"] = round(df["Zrobione"] / df["Deklarowane"] * 100, 1)
    df['DNS'] = df['pora_startu_z_DNS'] == 'DNS'
    df['mniej_niz_1_orbita'] = df['dystans_km'].between(1, 124, inclusive="both")
    df['zrobione_pelne'] = np.floor(df['zrobione']).astype(int) 

    return df
