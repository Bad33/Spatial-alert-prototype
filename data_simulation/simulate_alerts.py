# data_simulation/simulate_alerts.py
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import random

ALERT_TYPES = ["Kidnapping", "Fire", "Accident", "MissingPerson"]
SEVERITY    = ["Low", "Medium", "High", "Critical"]

def random_point(city_center=(41.881832, -87.623177), radius_km=50):
    """Generate lat/lon within a circle (haversine-approx)."""
    lat0, lon0 = np.radians(city_center)
    r = radius_km / 6371.0                           # angular radius
    u, v = np.random.rand(), np.random.rand()
    w = r * np.sqrt(u)
    t = 2 * np.pi * v
    lat = np.arcsin(np.sin(lat0)*np.cos(w) + np.cos(lat0)*np.sin(w)*np.cos(t))
    lon = lon0 + np.arctan2(np.sin(t)*np.sin(w)*np.cos(lat0),
                            np.cos(w)-np.sin(lat0)*np.sin(lat))
    return np.degrees(lat), np.degrees(lon)

def simulate(n_records=5000,
             start=datetime(2025, 1, 1),
             outfile="sim_alerts.csv"):
    rows = []
    for i in range(n_records):
        ts = start + timedelta(minutes=random.randint(0, 60*24*60))
        lat, lon = random_point()
        rows.append(
            dict(
                alert_id=i,
                timestamp=ts.isoformat(sep=" ", timespec="seconds"),
                latitude=lat,
                longitude=lon,
                alert_type=random.choice(ALERT_TYPES),
                severity=random.choice(SEVERITY),
            )
        )
    df = pd.DataFrame(rows)
    Path(outfile).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(outfile, index=False)
    print(f"Saved {len(df)} alerts ➜ {outfile}")

if __name__ == "__main__":
    simulate()
