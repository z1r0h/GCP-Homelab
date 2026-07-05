"""
Target ML API — a deliberately over-sharing model endpoint.

Serves a RandomForest classifier (benign=0 / malicious=1) trained on synthetic
network-traffic features. Returns FULL confidence probabilities, which is exactly
what makes Model Extraction (scenario 08) and Adversarial ML Evasion (scenario 05)
possible — an attacker can harvest the probability surface to clone the model or
craft evasive samples.

Endpoints:
  POST /predict   {"features": [f1..f10]}  -> {"prediction": 0|1, "confidence": p}
  GET  /health
"""
from flask import Flask, request, jsonify
import numpy as np
import os, pickle, logging, sys, json
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone
from sklearn.ensemble import RandomForestClassifier

app = Flask(__name__)
MODEL_PATH = "target_classifier.pkl"
N_FEATURES = 10

# --- Structured JSON logger (stdout + shared volume for Wazuh/Splunk) ---
logger = logging.getLogger("ml-api")
logger.setLevel(logging.INFO)
_sh = logging.StreamHandler(sys.stdout)
_sh.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(_sh)
try:
    os.makedirs("/var/log/ai-lab", exist_ok=True)
    _fh = RotatingFileHandler("/var/log/ai-lab/ml-api.json", maxBytes=10 * 1024 * 1024, backupCount=3)
    _fh.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(_fh)
except OSError:
    pass  # shared volume not mounted (e.g. local run) — stdout still works


def _train_or_load():
    """Train a reproducible synthetic classifier once, then cache to disk."""
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            return pickle.load(f)
    rng = np.random.default_rng(42)
    # Benign: low-magnitude features; Malicious: shifted distribution.
    benign = rng.normal(0.3, 0.15, size=(2000, N_FEATURES))
    malicious = rng.normal(0.7, 0.15, size=(2000, N_FEATURES))
    X = np.vstack([benign, malicious])
    y = np.array([0] * 2000 + [1] * 2000)
    clf = RandomForestClassifier(n_estimators=50, random_state=42)
    clf.fit(X, y)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(clf, f)
    return clf


MODEL = _train_or_load()


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "n_features": N_FEATURES})


@app.route("/predict", methods=["POST"])
def predict():
    src_ip = request.remote_addr
    data = request.get_json(silent=True) or {}
    features = data.get("features")
    if not isinstance(features, list) or len(features) != N_FEATURES:
        return jsonify({"error": f"expected 'features' list of length {N_FEATURES}"}), 400

    x = np.array(features, dtype=float).reshape(1, -1)
    proba = MODEL.predict_proba(x)[0]
    pred = int(np.argmax(proba))
    confidence = float(proba[pred])

    # VULNERABILITY: leaking full-precision confidence enables extraction/evasion.
    logger.info(json.dumps({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "app": "ml-api",
        "endpoint": "/predict",
        "src_ip": src_ip,
        "prediction": pred,
        "confidence": round(confidence, 6),
        "event_type": "model_prediction",
    }))
    return jsonify({"prediction": pred, "confidence": confidence,
                    "probabilities": proba.tolist()})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005)
