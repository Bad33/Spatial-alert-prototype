from backend import create_app

def test_clusters():
    app = create_app()
    client = app.test_client()
    r = client.get("/clusters?eps_km=5&min_samples=5")
    assert r.status_code == 200
    data = r.get_json()
    assert data["type"] == "FeatureCollection"
