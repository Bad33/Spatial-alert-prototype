import pandas as pd, joblib
from pathlib import Path

MODEL_DIR = Path(__file__).parent / "artifacts"
clf = joblib.load(MODEL_DIR / "rf_classifier.joblib")
risk_reg = joblib.load(MODEL_DIR / "xgb_risk.joblib")
iso = joblib.load(MODEL_DIR / "iso_anomaly.joblib")

def features_from_record(rec: dict) -> pd.DataFrame:
    ts = pd.to_datetime(rec["timestamp"])
    return pd.DataFrame([{
        "hour": ts.hour,
        "month": ts.month,
        "lat_bin": int(rec["latitude"] * 10),
        "lon_bin": int(rec["longitude"] * 10)
    }])

def classify(rec: dict) -> str:
    X = features_from_record(rec)
    pred = clf.predict(X)[0]
    return ["Low", "Medium", "High", "Critical"][pred]

def risk_score(rec: dict) -> float:
    X = features_from_record(rec)
    return float(risk_reg.predict(X)[0])

def is_anomaly(rec: dict) -> bool:
    X = features_from_record(rec)
    return bool(iso.predict(X)[0] == -1)
