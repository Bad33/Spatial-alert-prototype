import json
from backend import create_app

def test_list_alerts():
    app = create_app()
    client = app.test_client()
    resp = client.get("/alerts?limit=3")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert len(data) == 3
    assert {"alert_id", "latitude", "longitude"} <= data[0].keys()
