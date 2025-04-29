import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, IsolationForest
import xgboost as xgb
import joblib

DATA = Path(__file__).parents[1] / "sim_alerts.csv"
MODEL_DIR = Path(__file__).parent / "artifacts"
MODEL_DIR.mkdir(exist_ok=True)

def make_features(df: pd.DataFrame):
    df = df.copy()
    df["hour"] = df["timestamp"].str.slice(11, 13).astype(int)
    df["month"] = df["timestamp"].str.slice(5, 7).astype(int)
    df["lat_bin"] = (df["latitude"] * 10).astype(int)
    df["lon_bin"] = (df["longitude"] * 10).astype(int)
    X = df[["hour", "month", "lat_bin", "lon_bin"]]
    y = df["severity"].map({"Low": 0, "Medium": 1, "High": 2, "Critical": 3})
    return X, y

def train():
    df = pd.read_csv(DATA)
    X, y = make_features(df)

    # --- classification ---
    clf = RandomForestClassifier(
        n_estimators=150, max_depth=None, random_state=42)
    clf.fit(X, y)
    joblib.dump(clf, MODEL_DIR / "rf_classifier.joblib")

    # --- risk prediction (XGB regressor) ---
    reg = xgb.XGBRegressor(
        n_estimators=200, learning_rate=0.1, subsample=0.8, random_state=42)
    reg.fit(X, y)                       # treat severity index as risk score
    joblib.dump(reg, MODEL_DIR / "xgb_risk.joblib")

    # --- anomaly detection ---
    iso = IsolationForest(contamination=0.02, random_state=42)
    iso.fit(X)
    joblib.dump(iso, MODEL_DIR / "iso_anomaly.joblib")

    print("Models trained & saved to", MODEL_DIR)

if __name__ == "__main__":
    train()
