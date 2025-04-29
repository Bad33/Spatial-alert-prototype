from pathlib import Path
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS

CSV_PATH = Path(__file__).parent.parent / "sim_alerts.csv"

def create_app():
    app = Flask(__name__)
    CORS(app)  # allow React later

    # ------------ Data loading ------------
    alerts_df = pd.read_csv(CSV_PATH, parse_dates=["timestamp"])

    # ------------ Routes ------------------
    @app.route("/alerts")
    def list_alerts():
        """Return latest N alerts (default 100)."""
        n = int(request.args.get("limit", 100))
        data = (
            alerts_df.sort_values("timestamp", ascending=False)
            .head(n)
            .to_dict(orient="records")
        )
        return jsonify(data)

    @app.route("/alerts/<int:alert_id>")
    def get_alert(alert_id):
        record = alerts_df.loc[alerts_df["alert_id"] == alert_id]
        if record.empty:
            return {"error": "not found"}, 404
        return jsonify(record.to_dict(orient="records")[0])

    @app.route("/alerts/heatmap")
    def heatmap():
        """Return simple 2-D histogram counts for a 100x100 grid."""
        import numpy as np

        lat = alerts_df["latitude"].to_numpy()
        lon = alerts_df["longitude"].to_numpy()
        counts, xedges, yedges = np.histogram2d(
            lat, lon, bins=100, range=[[lat.min(), lat.max()], [lon.min(), lon.max()]]
        )
        return jsonify(
            dict(
                counts=counts.tolist(),
                lat_bins=xedges.tolist(),
                lon_bins=yedges.tolist(),
            )
        )
    
    from ml_services.clustering import run_dbscan

    @app.route("/clusters")
    def clusters():
        eps = float(request.args.get("eps_km", 2.0))
        min_samples = int(request.args.get("min_samples", 10))
        labels, features = run_dbscan(alerts_df, eps, min_samples)
        return jsonify(features)
    
    from sklearn.neighbors import KernelDensity

    @app.route("/kde")
    def kde():
        bw = float(request.args.get("bw_km", 1.0))
        coords = alerts_df[["latitude", "longitude"]].to_numpy()
        kde = KernelDensity(bandwidth=bw/111, metric="haversine").fit(np.radians(coords))
        log_dens = kde.score_samples(np.radians(coords))
        return jsonify(dict(
            lat=alerts_df["latitude"].tolist(),
            lon=alerts_df["longitude"].tolist(),
            density=np.exp(log_dens).tolist()
        ))



    return app
