import json
from backend import create_app

sample = {
    "alert_id": 1,
    "timestamp": "2025-01-08 12:34:56",
    "latitude": 41.9,
    "longitude": -87.6
}

def test_predict():
    app = create_app()
    c = app.test_client()
    r = c.post("/predict", json=sample)
    assert r.status_code == 200
    data = r.get_json()
    assert "predicted_severity" in data
    assert "risk_score" in data

def test_anomaly():
    app = create_app()
    c = app.test_client()
    r = c.post("/anomaly", json=sample)
    assert r.status_code == 200
    assert isinstance(r.get_json()["is_anomaly"], bool)
