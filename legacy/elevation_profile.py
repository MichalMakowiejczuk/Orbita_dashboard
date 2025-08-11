import json
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from geopy.geocoders import Nominatim


class ElevationProfile:
    """Analiza i wizualizacja profilu wysokościowego"""

    def __init__(self, track_df, seg_unit_km=0.5):
        if track_df.empty:
            raise ValueError("DataFrame jest pusty.")
        self.track_df = track_df.copy()
        self.seg_unit_km = seg_unit_km
        self._assign_segments()
        self._compute_slopes()
        self.places_df = None

    def _assign_segments(self):
        self.track_df["segment"] = (self.track_df["km"] // self.seg_unit_km).astype(int)

    def _compute_slopes(self):
        slopes_df = (
            self.track_df.groupby("segment")
            .agg(start_km=("km", "first"),
                end_km=("km", "last"),
                start_elev=("elevation", "first"),
                end_elev=("elevation", "last"))
            .assign(slope=lambda df: np.where(
                df["end_km"] == df["start_km"], 0,
                (df["end_elev"] - df["start_elev"]) / ((df["end_km"] - df["start_km"]) * 1000) * 100
            ))
            .reset_index()[["segment", "slope"]]
        )
        self.track_df = self.track_df.merge(slopes_df, on="segment", how="left")

    def _load_cache(self, cache_file):
        if os.path.exists(cache_file):
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_cache(self, cache, cache_file):
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)

    def geolocate_places(self, min_distance_km=5, cache_file="places_cache.json"):
        geolocator = Nominatim(user_agent="ElevationProfileApp")
        places = []
        place_last_km = {}
        place_group = 0

        cache = self._load_cache(cache_file)

        for segment in self.track_df["segment"].unique():
            segment_df = self.track_df[self.track_df["segment"] == segment]
            row = segment_df.loc[segment_df["km"].idxmin()]
            lat, lon, elev, km = row["latitude"], row["longitude"], row["elevation"], row["km"]
            coords_key = f"{lat:.5f},{lon:.5f}"

            place_name = cache.get(coords_key)
            if place_name is None:
                try:
                    location = geolocator.reverse(f"{lat},{lon}", exactly_one=True, timeout=10)
                    address = location.raw.get("address", {})
                    place_name = (
                        address.get("city") or
                        address.get("town") or
                        address.get("village") or
                        None
                    )
                    cache[coords_key] = place_name
                except Exception:
                    continue

            if place_name and ((place_name not in place_last_km) or (km - place_last_km[place_name] >= min_distance_km)):
                place_group += 1
                place_last_km[place_name] = km
                places.append([segment, place_name, elev, km, place_group])

        self._save_cache(cache, cache_file)
        self.places_df = pd.DataFrame(places, columns=["segment", "place", "elevation", "km", "group"])
        self.places_df = self.places_df.drop_duplicates(subset=["place"]).sort_values(["group", "km"])

    def smooth_profile(self, smooth_window=5):
        return self.track_df['elevation'].rolling(window=smooth_window, center=True, min_periods=1).mean()
    
    def compute_slope_lengths(self, smooth_window=5, slope_thresholds=(2, 4, 5, 8)):
        df = self.track_df.copy()
        # Wygładzamy profil
        df['elev_smooth'] = df['elevation'].rolling(window=smooth_window, center=True, min_periods=1).mean()

        # Obliczamy nachylenie między kolejnymi punktami
        df['delta_elev'] = df['elev_smooth'].diff()
        df['delta_km'] = df['km'].diff()

        # Unikamy dzielenia przez zero i wartości nan (pierwszy wiersz)
        df = df.dropna(subset=['delta_elev', 'delta_km'])
        df = df[df['delta_km'] > 0]

        # Nachylenie procentowe = zmiana wysokości / zmiana dystansu * 100
        df['slope'] = (df['delta_elev'] / (df['delta_km'] * 1000)) * 100

        # Długość segmentu to delta_km (odcinek między punktami)
        df['segment_length_km'] = df['delta_km']

        # Definiujemy progi nachyleń
        thresholds = [-np.inf] + list(slope_thresholds) + [np.inf]
        labels = []
        for i in range(len(thresholds) - 1):
            low = thresholds[i]
            high = thresholds[i + 1]
            if low == -np.inf:
                labels.append(f"< {high}%")
            elif high == np.inf:
                labels.append(f">= {low}%")
            else:
                labels.append(f"{low} ~ {high}%")

        # Przypisujemy do przedziałów (domknięte z prawej strony)
        df['slope_range'] = pd.cut(df['slope'], bins=thresholds, labels=labels, right=True)

        # Sumujemy długości dla każdego zakresu nachyleń
        result = (
            df.groupby('slope_range')['segment_length_km']
            .sum()
            .reset_index()
            .rename(columns={'segment_length_km': 'length_km'})
        )

        return pd.DataFrame({
            'slope_range': result['slope_range'],
            'length_km': round(result['length_km'], 2)
        })

    def plot(self,
             show_labels=True,
             show_background=True,
             background_color="gray",
             background_shift_km=0.5,
             background_shift_elev=15,
             smooth_window=5,
             slope_thresholds=(2, 4, 5, 8),
             slope_colors=("lightgreen", "yellow", "orange", "orangered", "maroon"),
             slope_labels=("< 2%", "2 ~ 4%", "4 ~ 5%", "5 ~ 8%", "> 8%")):
        """
        Rysuje profil wysokości.
        """
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.set_xlabel("Kilometers")
        ax.set_ylabel("Elevation [m]")
        ax.spines[["right", "top"]].set_visible(False)

        elevation_smooth = self.smooth_profile(smooth_window)

        if show_background:
            ax.fill_between(
                self.track_df["km"] + background_shift_km,
                elevation_smooth + background_shift_elev,
                color=background_color,
                zorder=0,
            )

        thresholds = [-np.inf] + list(slope_thresholds) + [np.inf]
        legend = []
        for i in range(len(slope_colors)):
            mask = (self.track_df["slope"] >= thresholds[i]) & (self.track_df["slope"] < thresholds[i + 1])
            ax.fill_between(
                self.track_df["km"],
                elevation_smooth,
                where=mask,
                color=slope_colors[i],
                zorder=1,
            )
            legend.append(mpatches.Patch(color=slope_colors[i], label=slope_labels[i]))

        if show_labels and self.places_df is not None:
            annotations_anchor = self.track_df["elevation"].max() * 1.1
            min_distance_km = 5
            last_label_km = -min_distance_km
            for _, row in self.places_df.iterrows():
                if row["km"] - last_label_km >= min_distance_km:
                    ax.annotate(
                        row["place"],
                        xy=(row["km"], row["elevation"]),
                        xytext=(row["km"], annotations_anchor),
                        arrowprops=dict(arrowstyle="-", color="lightgray"),
                        horizontalalignment="center",
                        rotation=90,
                        size=10,
                        color="gray",
                    )
                    last_label_km = row["km"]
        
        ax.plot(self.track_df["km"], elevation_smooth, color="darkgrey", linewidth=0.15)
        ax.set_xlim(self.track_df["km"].min(), self.track_df["km"].max())
        ax.legend(handles=legend, loc="center left", bbox_to_anchor=(1, 0.5))

        return fig, ax


if __name__ == "__main__":
    from gpx_parser import GPXParser

    parser = GPXParser("data/track/orbita25.gpx")
    df = parser.parse_to_dataframe()

    profile = ElevationProfile(df, seg_unit_km=0.5)
    profile.geolocate_places(min_distance_km=10)  # Odkomentuj, jeśli chcesz dodać nazwy miejsc
    lengths = profile.compute_slope_lengths(smooth_window=5, slope_thresholds=(2, 4, 5, 8))
    print(lengths)

    fig, ax = profile.plot(show_labels=True, background_color="lightgray",
                           background_shift_km=0.5, background_shift_elev=10, smooth_window=5)
    fig.set_size_inches(12, 4)
    # ax.set_title("Profil wysokości - Orbita 25")
    ax.set_xlabel("Dystans [km]")
    ax.set_ylabel("Wysokość [m]")
    ax.set_ylim(200, profile.track_df["elevation"].max() * 1.1)
    plt.savefig("static/elevation_profile.png", bbox_inches="tight", dpi=300)
    plt.show()
