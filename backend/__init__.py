# backend/__init__.py
from pathlib import Path
import geojson
import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO

# ---------------------------------------------------------------------
# Globals
# ---------------------------------------------------------------------
CSV_PATH = Path(__file__).parent.parent / "sim_alerts.csv"
socketio = SocketIO(cors_allowed_origins="*")        # WebSocket + polling fallback


def create_app() -> Flask:
    """Application factory."""
    app = Flask(__name__)
    CORS(app)
    socketio.init_app(app)                            # << DON'T FORGET THIS!

    # ------------ Data loading ------------
    alerts_df = pd.read_csv(CSV_PATH, parse_dates=["timestamp"])

    # -----------------------------------------------------------------
    # REST endpoints
    # -----------------------------------------------------------------
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
        """Return simple 2-D histogram counts (100×100)."""
        lat = alerts_df["latitude"].to_numpy()
        lon = alerts_df["longitude"].to_numpy()
        counts, xedges, yedges = np.histogram2d(
            lat, lon, bins=100, range=[[lat.min(), lat.max()], [lon.min(), lon.max()]]
        )
        return jsonify(
            dict(counts=counts.tolist(), lat_bins=xedges.tolist(), lon_bins=yedges.tolist())
        )

    # -----------------------------------------------------------------
    # Spatial clustering
    # -----------------------------------------------------------------
    from ml_services.clustering import run_dbscan

    @app.route("/clusters")
    def clusters():
        eps = float(request.args.get("eps_km", 2.0))
        min_samples = int(request.args.get("min_samples", 10))
        _, features = run_dbscan(alerts_df, eps, min_samples)
        return jsonify(features)

    # KDE density
    from sklearn.neighbors import KernelDensity

    @app.route("/kde")
    def kde():
        bw = float(request.args.get("bw_km", 1.0))
        coords = alerts_df[["latitude", "longitude"]].to_numpy()
        kde = KernelDensity(bandwidth=bw / 111, metric="haversine").fit(np.radians(coords))
        log_dens = kde.score_samples(np.radians(coords))
        return jsonify(
            dict(
                lat=alerts_df["latitude"].tolist(),
                lon=alerts_df["longitude"].tolist(),
                density=np.exp(log_dens).tolist(),
            )
        )

    # -----------------------------------------------------------------
    # ML endpoints
    # -----------------------------------------------------------------
    from ml_services import predict

    @app.route("/predict", methods=["POST"])
    def predict_severity():
        rec = request.get_json()
        if not rec:
            return {"error": "JSON body required"}, 400
        return jsonify(
            dict(
                predicted_severity=predict.classify(rec),
                risk_score=predict.risk_score(rec),
            )
        )

    @app.route("/anomaly", methods=["POST"])
    def predict_anomaly():
        rec = request.get_json()
        if not rec:
            return {"error": "JSON body required"}, 400
        return jsonify(dict(is_anomaly=predict.is_anomaly(rec)))

    # -----------------------------------------------------------------
    # Ingest + real-time anomaly broadcast
    # -----------------------------------------------------------------
    @app.route("/ingest", methods=["POST"])
    def ingest_alert():
        """Simulate real-time arrival of one alert; body = alert JSON."""
        rec = request.get_json()
        if not rec:
            return {"error": "JSON body required"}, 400

        nonlocal alerts_df
        alerts_df = pd.concat([alerts_df, pd.DataFrame([rec])], ignore_index=True)

        # anomaly check
        if predict.is_anomaly(rec):
            feature = geojson.Feature(
                geometry=geojson.Point((rec["longitude"], rec["latitude"])),
                properties=dict(
                    alert_id=rec["alert_id"],
                    alert_type=rec["alert_type"],
                    timestamp=rec["timestamp"],
                ),
            )
            socketio.emit("anomaly", feature)        # broadcast

        return {"status": "ok"}, 200

    return app
