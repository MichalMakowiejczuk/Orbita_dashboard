import gpxpy
import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from geopy.geocoders import Nominatim

class GPXParser:
    def __init__(self, gpx_path):
        self.gpx_path = gpx_path
        self.track_df = None

    def _get_distance(self, lat1, lon1, lat2, lon2):
        earthRadius = 6371  # km
        if None in (lat1, lon1, lat2, lon2):
            return 0
        latFrom = radians(lat1)
        lonFrom = radians(lon1)
        latTo = radians(lat2)
        lonTo = radians(lon2)
        dlon = lonTo - lonFrom
        dlat = latTo - latFrom
        a = sin(dlat / 2)**2 + cos(latFrom) * cos(latTo) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return earthRadius * c

    def parse_to_dataframe(self):
        with open(self.gpx_path, 'r', encoding='utf-8') as gpx_file:
            gpx = gpxpy.parse(gpx_file)

        track_data = []
        km = 0
        last_lat = None
        last_lon = None

        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    dist = self._get_distance(last_lat, last_lon, point.latitude, point.longitude)
                    km += dist
                    track_data.append([km, point.latitude, point.longitude, point.elevation])
                    last_lat = point.latitude
                    last_lon = point.longitude

        self.track_df = pd.DataFrame(track_data, columns=['km', 'latitude', 'longitude', 'elevation'])
        return self.track_df


class ElevationProfile:
    """
    Klasa do analizy i wizualizacji profilu wysokościowego z pliku GPX.

    Parametry:
    -----------
    track_df : pandas.DataFrame
        DataFrame z kolumnami ['km', 'latitude', 'longitude', 'elevation'].
    seg_unit_km : float
        Długość segmentu w kilometrach do podziału trasy na odcinki (domyślnie 0.5 km).

    Metody:
    --------
    geolocate_places(min_distance_km=5)
        Wyszukuje nazwy miejscowości na podstawie współrzędnych GPS, z minimalnym odstępem między etykietami.
    plot(show_labels=True, show_background=True, background_color='gray', background_shift_km=0.5, background_shift_elev=15)
        Rysuje profil wysokościowy z opcjonalnym tłem i etykietami miejscowości.
    """

    def __init__(self, track_df, seg_unit_km=0.5):
        self.track_df = track_df.copy()
        self.seg_unit_km = seg_unit_km
        self._assign_segments()
        self._compute_slopes()
        self.places_df = None  # DataFrame miejscowości po geolokalizacji

    def _assign_segments(self):
        self.track_df['segment'] = (self.track_df['km'] // self.seg_unit_km).astype(int)

    def _compute_slopes(self):
        slopes = []
        for segment in self.track_df['segment'].unique():
            segment_df = self.track_df[self.track_df['segment'] == segment]
            from_elev = segment_df['elevation'].iloc[0]
            to_elev = segment_df['elevation'].iloc[-1]
            length_km = segment_df['km'].max() - segment_df['km'].min()
            slope = 0 if length_km == 0 else (to_elev - from_elev) / (length_km * 1000) * 100
            slopes.append([segment, slope])
        slopes_df = pd.DataFrame(slopes, columns=['segment', 'slope'])
        self.track_df = self.track_df.merge(slopes_df, on='segment', how='left')

    def geolocate_places(self, min_distance_km=5):
        geolocator = Nominatim(user_agent="ElevationProfileApp")
        places = []
        place_last_km = {}
        place_group = 0

        for segment in self.track_df['segment'].unique():
            segment_df = self.track_df[self.track_df['segment'] == segment]
            row = segment_df.loc[segment_df['km'].idxmin()]
            lat, lon, elev, km = row['latitude'], row['longitude'], row['elevation'], row['km']

            try:
                location = geolocator.reverse(f"{lat},{lon}", exactly_one=True, timeout=10)
                address = location.raw.get('address', {})
                place_name = (
                    address.get('city') or
                    address.get('town') or
                    address.get('village') or
                    None
                )
                if place_name is None:
                    continue

                if (place_name not in place_last_km) or (km - place_last_km[place_name] >= min_distance_km):
                    place_group += 1
                    place_last_km[place_name] = km
                    places.append([segment, place_name, elev, km, place_group])
            except Exception as e:
                # Można tutaj dodać logowanie błędów, ale lepiej nie przerywać działania
                continue

        self.places_df = pd.DataFrame(places, columns=['segment', 'place', 'elevation', 'km', 'group'])
        # Usuwamy duplikaty i sortujemy
        self.places_df = self.places_df.drop_duplicates(subset=['place']).sort_values(['group', 'km'])

    def smooth_profile(self, signal, L=10):
        res = np.copy(signal)
        for i in range(1, len(signal) - 1):
            L_g = min(i, L)
            L_d = min(len(signal) - i - 1, L)
            Li = min(L_g, L_d)
            res[i] = np.sum(signal[i - Li:i + Li + 1]) / (2 * Li + 1)
        return res

    def plot(
        self,
        show_labels=True,
        show_background=True,
        background_color='gray',
        background_shift_km=0.5,
        background_shift_elev=15,
        smooth_L=10
    ):
        legend = []
        slopes_table = [
            lambda x: x < 2,
            lambda x: (x >= 2) & (x < 4),
            lambda x: (x >= 4) & (x < 5),
            lambda x: (x >= 5) & (x < 8),
            lambda x: x >= 8,
        ]
        slopes_color = ['palegreen', 'yellow', 'orange', 'orangered', 'maroon']
        slopes_descr = ['inf 2%', '2 ~ 4%', '4 ~ 5%', '5 ~ 8%', 'sup 8%']

        fig, ax = plt.subplots(figsize=(12, 4))
        ax.set_xlabel("Kilometers")
        ax.set_ylabel("Elevation [m]")
        ax.spines[['right', 'top']].set_visible(False)

        elevation_smooth = self.smooth_profile(self.track_df['elevation'], smooth_L)

        if show_background:
            ax.fill_between(
                self.track_df['km'] + background_shift_km,
                elevation_smooth + background_shift_elev,
                color=background_color,
                zorder=0,
            )

        for i, slope_cond in enumerate(slopes_table):
            ax.fill_between(
                self.track_df['km'],
                elevation_smooth,
                where=slope_cond(self.track_df['slope']),
                color=slopes_color[i],
                zorder=1,
            )
            legend.append(mpatches.Patch(color=slopes_color[i], label=slopes_descr[i]))

        if show_labels and self.places_df is not None:
            annotations_anchor = self.track_df['elevation'].max() * 1.1
            min_distance_km = 5
            last_label_km = -min_distance_km
            for _, row in self.places_df.iterrows():
                if row['km'] - last_label_km >= min_distance_km:
                    ax.annotate(
                        row['place'],
                        xy=(row['km'], row['elevation']),
                        xytext=(row['km'], annotations_anchor),
                        arrowprops=dict(arrowstyle="-", color='lightgray'),
                        horizontalalignment='center',
                        rotation=90,
                        size=10,
                        color='gray',
                    )
                    last_label_km = row['km']

        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        ax.legend(handles=legend, loc='center left', bbox_to_anchor=(1, 0.5))

        return fig, ax

if __name__ == "__main__":
    # Parsowanie pliku GPX
    parser = GPXParser("data/track/orbita25.gpx")
    df = parser.parse_to_dataframe()

    # Tworzenie profilu i pobieranie miejscowości
    profile = ElevationProfile(df, seg_unit_km=0.5)
    #profile.geolocate_places(min_distance_km=5)

    # Rysowanie wykresu z tłem i etykietami miejsc
    fig, ax = profile.plot(show_labels=True, show_background=True, background_color='lightgray', background_shift_km=0.5, background_shift_elev=10)
    ax.set_title("Profil wysokości - Orbita 25")
    ax.set_xlabel("Dystans [km]")
    ax.set_ylabel("Wysokość [m]")
    ax.set_ylim(200, profile.track_df['elevation'].max() * 1.1)
    plt.savefig("img/elevation_profile.png", bbox_inches='tight', dpi=300)