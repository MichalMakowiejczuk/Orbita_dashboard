import gpxpy
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from math import radians, sin, cos, atan2, sqrt
from geopy.geocoders import Nominatim

class ElevationProfile:
    """
    Klasa do analizy i wizualizacji profilu wysokościowego trasy GPS zapisanej w pliku GPX.

    Funkcjonalności:
    - Parsowanie pliku GPX i wyliczanie segmentów trasy oraz dystansów.
    - Obliczanie nachylenia (slope) dla segmentów trasy.
    - Opcjonalna geolokalizacja miejscowości na trasie z wykorzystaniem API Nominatim.
    - Wykres profilu wysokości z kolorowaniem segmentów wg nachylenia oraz z opcjonalnymi etykietami miejsc.

    Parametry konstruktora:
    ---------------
    gpx_path : str
        Ścieżka do pliku GPX z trasą.
    seg_unit_km : float, opcjonalnie (domyślnie 0.25)
        Długość segmentu w kilometrach dla podziału profilu.
    smooth_L : int, opcjonalnie (domyślnie 10)
        Parametr wygładzania profilu (długość okna wygładzania).
    slope_thresholds : tuple, opcjonalnie (domyślnie (2,4,5,8))
        Progi nachylenia w procentach, służące do kategoryzacji segmentów.
    slope_colors : tuple, opcjonalnie (domyślnie ('palegreen', 'yellow', 'orange', 'orangered', 'maroon'))
        Kolory przypisane do poszczególnych kategorii nachylenia.
    slope_labels : tuple, opcjonalnie (domyślnie ('inf 2%', '2 ~ 4%', '4 ~ 5%', '5 ~ 8%', 'sup 8%'))
        Opisy kategorii nachylenia wykorzystywane w legendzie wykresu.
    background_shadow : bool, opcjonalnie (domyślnie True)
        Czy rysować tło cienia profilu.
    background_shadow_offset_km : float, opcjonalnie (domyślnie 0.5)
        Poziome przesunięcie cienia w km.
    background_shadow_elevation_offset : float, opcjonalnie (domyślnie 15)
        Pionowe przesunięcie cienia w metrach.
    background_shadow_color : str, opcjonalnie (domyślnie 'gray')
        Kolor tła cienia.

    Metody:
    ---------------
    parse_gpx()
        Parsuje plik GPX, oblicza dystanse i nachylenia segmentów, tworzy DataFrame z danymi trasy.
    geolocate_places(min_distance_km=5)
        Wykonuje geolokalizację miejscowości na trasie i tworzy DataFrame z miejscami.
    plot(show_labels=True)
        Rysuje profil wysokości z kolorowaniem segmentów i opcjonalnymi etykietami miejscowości.
    """
    def __init__(self, 
                 gpx_path, 
                 seg_unit_km=0.25, 
                 smooth_L=10,
                 slope_thresholds=(2, 4, 5, 8),
                 slope_colors=('palegreen', 'yellow', 'orange', 'orangered', 'maroon'),
                 slope_labels=('< 2%', '2 ~ 4%', '4 ~ 5%', '5 ~ 8%', '> 8%'),
                 background_shadow=True,
                 background_shadow_offset_km=0.5,
                 background_shadow_elevation_offset=15,
                 background_shadow_color='gray'):
        self.gpx_path = gpx_path
        self.seg_unit_km = seg_unit_km
        self.smooth_L = smooth_L
        self.slope_thresholds = slope_thresholds
        self.slope_colors = slope_colors
        self.slope_labels = slope_labels
        self.background_shadow = background_shadow
        self.background_shadow_offset_km = background_shadow_offset_km
        self.background_shadow_elevation_offset = background_shadow_elevation_offset
        self.background_shadow_color = background_shadow_color
        self.track_df = None
        self.places_df = None

    # -------------------
    # Helper functions
    # -------------------
    @staticmethod
    def get_distance_between_coords(lat1, long1, lat2, long2):
        """Computing distance in km between 2 points"""
        earth_radius = 6371
        if None in (lat1, long1, lat2, long2):
            return 0
        lat_from = radians(lat1)
        lon_from = radians(long1)
        lat_to = radians(lat2)
        lon_to = radians(long2)
        dlon = lon_to - lon_from
        dlat = lat_to - lat_from
        a = sin(dlat / 2)**2 + cos(lat_from) * cos(lat_to) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return earth_radius * c

    @staticmethod
    def smooth_profile(signal, L=10):
        """Simple moving average smoothing"""
        res = np.copy(signal)
        for i in range(1, len(signal) - 1):
            L_g = min(i, L)
            L_d = min(len(signal) - i - 1, L)
            Li = min(L_g, L_d)
            res[i] = np.sum(signal[i - Li:i + Li + 1]) / (2 * Li + 1)
        return res

    # -------------------
    # Core processing
    # -------------------
    def parse_gpx(self):
        """Parse GPX file and compute distance, slope segments."""
        with open(self.gpx_path, 'r', encoding='utf-8') as f:
            gpx = gpxpy.parse(f)

        track_data = []
        km = 0
        last_lat, last_lon = None, None

        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    dist = self.get_distance_between_coords(last_lat, last_lon, point.latitude, point.longitude)
                    km += dist
                    seg_id = km // self.seg_unit_km
                    track_data.append([seg_id, km, point.latitude, point.longitude, point.elevation])
                    last_lat, last_lon = point.latitude, point.longitude

        df = pd.DataFrame(track_data, columns=['segment', 'km', 'latitude', 'longitude', 'elevation'])

        # Compute slopes
        slopes = []
        for seg in df['segment'].unique():
            first_st = df.loc[df[df['segment'] == seg]['km'].idxmin()]
            last_st = df.loc[df[df['segment'] == seg]['km'].idxmax()]
            seg_len = df[df['segment'] == seg]['km'].max() - df[df['segment'] == seg]['km'].min()
            seg_slope = (last_st['elevation'] - first_st['elevation']) / (seg_len * 1000) * 100 if seg_len > 0 else 0
            slopes.append([seg, seg_slope])

        slopes_df = pd.DataFrame(slopes, columns=['segment', 'slope'])
        self.track_df = pd.merge(df, slopes_df, on='segment')
        return self

    def geolocate_places(self, min_distance_km=5):
        """Optional geolocation of places along the track."""
        if self.track_df is None:
            raise ValueError("Run parse_gpx() first.")
        geolocator = Nominatim(user_agent="MyApp")
        places = []
        place_last_km = {}
        place_group = 0

        for seg in self.track_df['segment'].unique():
            seg_df = self.track_df[self.track_df['segment'] == seg]
            row = seg_df.loc[seg_df['km'].idxmin()]
            from_lat, from_lon, from_elv, from_km = row['latitude'], row['longitude'], row['elevation'], row['km']

            try:
                location = geolocator.reverse(f"{from_lat},{from_lon}")
                address = location.raw['address']
                place_name = address.get('city') or address.get('town') or address.get('village') or 'Unknown'

                if place_name == 'Unknown':
                    continue

                if (place_name not in place_last_km) or (from_km - place_last_km[place_name] >= min_distance_km):
                    place_group += 1
                    place_last_km[place_name] = from_km
                    places.append([seg, place_name, from_elv, from_km, place_group])

            except Exception as e:
                print(f"Błąd geolokalizacji dla segmentu {seg}: {e}")
                continue

        df_places = pd.DataFrame(places, columns=['segment', 'place', 'elevation', 'km', 'group'])
        df_places = df_places[df_places['place'] != 'Unknown']
        df_places = df_places.sort_values(['group', 'km']).drop_duplicates(subset=['place'], keep='first')
        self.places_df = df_places
        return self

    # -------------------
    # Plotting
    # -------------------
    def plot(self, show_labels=True):
        """Plot the elevation profile."""
        if self.track_df is None:
            raise ValueError("No track data to plot. Run parse_gpx() first.")

        thresholds = self.slope_thresholds
        slope_conditions = [
            lambda x: x < thresholds[0],
            lambda x: (x >= thresholds[0]) & (x < thresholds[1]),
            lambda x: (x >= thresholds[1]) & (x < thresholds[2]),
            lambda x: (x >= thresholds[2]) & (x < thresholds[3]),
            lambda x: x >= thresholds[3]
        ]

        fig, ax = plt.subplots(figsize=(12, 4))
        plt.xlabel("Kilometers")
        plt.ylabel("Elevation")
        ax.spines[['right', 'top']].set_visible(False)

        # Background "shadow" profile
        if self.background_shadow:
            plt.fill_between(
                self.track_df['km'] + self.background_shadow_offset_km,
                self.smooth_profile(self.track_df['elevation'], self.smooth_L) + self.background_shadow_elevation_offset,
                color=self.background_shadow_color,
                zorder=0
            )

        # Color segments by slope category
        legend_patches = []
        for cond, color, label in zip(slope_conditions, self.slope_colors, self.slope_labels):
            plt.fill_between(
                self.track_df['km'],
                self.smooth_profile(self.track_df['elevation'], self.smooth_L),
                where=cond(self.track_df['slope']),
                color=color, zorder=1
            )
            legend_patches.append(mpatches.Patch(color=color, label=label))

        # Place labels
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
                        size=10, color='gray'
                    )
                    last_label_km = row['km']

        # Legend
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        ax.legend(handles=legend_patches, loc='center left', bbox_to_anchor=(1, 0.5))
        return fig, ax

if __name__ == "__main__":
    # Example usage
    gpx_path = "data/track/orbita25.gpx"

    profile = ElevationProfile(gpx_path, 
                               seg_unit_km=0.5
                               ).parse_gpx()
    fig, ax = profile.plot()
    ax.set_title("Profil wysokości - Orbita 25")
    ax.set_xlabel("Dystans [km]")
    ax.set_ylabel("Wysokość [m]")
    ax.set_ylim(200, profile.track_df['elevation'].max() * 1.1)
    plt.savefig("img/elevation_profile.png", bbox_inches='tight', dpi=300)