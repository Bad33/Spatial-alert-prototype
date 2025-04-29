import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
import geojson

def run_dbscan(df: pd.DataFrame,
               eps_km: float = 2.0,
               min_samples: int = 10):
    """Return cluster labels & GeoJSON centroids."""
    # convert eps from km to radians (haversine expects radians)
    kms_per_radian = 6371.0088
    coords = np.radians(df[["latitude", "longitude"]].to_numpy())
    db = DBSCAN(eps=eps_km / kms_per_radian,
                min_samples=min_samples,
                algorithm="ball_tree",
                metric="haversine").fit(coords)
    df = df.copy()
    df["cluster"] = db.labels_

    clusters = []
    for cl in sorted(c for c in set(db.labels_) if c != -1):
        subset = df[df["cluster"] == cl]
        lat_c, lon_c = subset[["latitude", "longitude"]].mean()
        clusters.append(
            geojson.Feature(
                geometry=geojson.Point((lon_c, lat_c)),
                properties=dict(
                    cluster_id=int(cl),
                    count=int(len(subset)),
                ),
            )
        )
    return df["cluster"].tolist(), geojson.FeatureCollection(clusters)
