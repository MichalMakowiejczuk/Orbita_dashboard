import gpxpy
import pandas as pd
from geopy.distance import geodesic

class GPXParser:
    """Parser GPX -> DataFrame"""

    def __init__(self, gpx_path):
        self.gpx_path = gpx_path
        self.track_df = None

    def _get_distance(self, lat1, lon1, lat2, lon2):
        if None in (lat1, lon1, lat2, lon2):
            return 0
        return geodesic((lat1, lon1), (lat2, lon2)).km

    def parse_to_dataframe(self):
        with open(self.gpx_path, "r", encoding="utf-8") as gpx_file:
            gpx = gpxpy.parse(gpx_file)

        track_data = []
        km = 0
        last_lat, last_lon = None, None

        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    dist = self._get_distance(last_lat, last_lon, point.latitude, point.longitude)
                    km += dist
                    track_data.append([km, point.latitude, point.longitude, point.elevation])
                    last_lat, last_lon = point.latitude, point.longitude

        self.track_df = pd.DataFrame(track_data, columns=["km", "latitude", "longitude", "elevation"])
        if self.track_df.empty:
            raise ValueError("Brak punktów w ścieżce GPX.")
        return self.track_df
    
    def get_total_ascent(self, smooth_window=5):
        if self.track_df is None:
            raise ValueError("Brak danych – najpierw uruchom parse_to_dataframe().")

        # wygładzenie filtrem średniej kroczącej
        smoothed = self.track_df["elevation"].rolling(window=smooth_window, center=True, min_periods=1).mean()
        
        elevation_diff = smoothed.diff()
        total_ascent = elevation_diff[elevation_diff > 0].sum()
        return total_ascent
