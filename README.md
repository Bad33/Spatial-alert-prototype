# Spatial Emergency Alert Prototype (SAP)

A real-time demo inspired by **Amber Alerts** that showcases spatial-data-mining
workflows:

* **Simulated alert stream** → DBSCAN / KDE / Isolation-Forest analytics  
* **Flask + Flask-SocketIO** backend (Python 3.11)  
* **React + Leaflet** interactive map frontend  
* Live anomaly push, hotspots, density heatmaps, and spatio-temporal queries

---

## 1  Quick start (dev)

```bash
# clone & create venv
git clone https://github.com/Bad33/Spatial-alert-prototype.git
cd Spatial-alert-prototype
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python ml_services/train_models.py        # one-off model artifacts
python -m backend.run                     # ➜ http://127.0.0.1:8000

# in another terminal
cd frontend
npm install
npm run dev                               # ➜ http://localhost:5173



#Simulating New Alert

curl -X POST http://127.0.0.1:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
        "alert_id": 9999,
        "timestamp": "2025-04-30 12:34:56",
        "latitude": 41.70,
        "longitude": -88.30,
        "alert_type": "Kidnapping"
      }'


#Branch off develop