#!/usr/bin/env python3
"""
generate_adv_samples.py — Adversarial ML Evasion via ZOO attack (Scenario 05).

Loads the target classifier (the ml-api's RandomForest, exported as
`target_classifier.pkl`), then uses IBM ART's ZooAttack — a gradient-free, black-box
method — to perturb malicious samples just enough to be misclassified as benign.

Usage:
  python3 generate_adv_samples.py --model target_classifier.pkl \
      --dataset malicious_traffic.csv --method zoo

If --dataset is omitted, synthetic malicious samples are generated so the script is
runnable standalone for a demo.

Requires: adversarial-robustness-toolbox, scikit-learn, numpy (see tools/requirements.txt)
"""
import argparse
import pickle

import numpy as np

N_FEATURES = 10


def load_model(path: str):
    with open(path, "rb") as f:
        return pickle.load(f)


def load_or_make_samples(dataset: str | None) -> np.ndarray:
    if dataset:
        try:
            import csv
            rows = []
            with open(dataset, newline="") as f:
                for row in csv.reader(f):
                    rows.append([float(x) for x in row[:N_FEATURES]])
            return np.array(rows, dtype=float)
        except (OSError, ValueError) as e:
            print(f"[!] Could not read {dataset} ({e}); using synthetic samples")
    rng = np.random.default_rng(7)
    return rng.normal(0.7, 0.15, size=(20, N_FEATURES))  # "malicious" cluster


def main():
    ap = argparse.ArgumentParser(description="ZOO adversarial sample generator")
    ap.add_argument("--model", default="target_classifier.pkl")
    ap.add_argument("--dataset", default=None)
    ap.add_argument("--method", default="zoo", choices=["zoo"])
    args = ap.parse_args()

    try:
        model = load_model(args.model)
    except OSError:
        print(f"[!] Model {args.model} not found. Export it from ml-api first "
              "(it is saved as target_classifier.pkl on first boot).")
        return

    x_mal = load_or_make_samples(args.dataset)
    print(f"[*] Loaded {len(x_mal)} malicious samples; baseline preds: "
          f"{model.predict(x_mal).tolist()}")

    try:
        from art.attacks.evasion import ZooAttack
        from art.estimators.classification import SklearnClassifier
    except ImportError:
        print("[!] ART not installed: pip install adversarial-robustness-toolbox")
        return

    classifier = SklearnClassifier(model=model)
    attack = ZooAttack(classifier=classifier, max_iter=20, nb_parallel=N_FEATURES)
    x_adv = attack.generate(x=x_mal)

    evaded = int(np.sum(model.predict(x_adv) == 0))
    print(f"[+] After ZOO perturbation: {evaded}/{len(x_adv)} malicious samples now "
          f"misclassified as BENIGN (0).")
    np.save("adversarial_samples.npy", x_adv)
    print("[*] Saved -> adversarial_samples.npy")
    print("[*] Defense (scenario 05): monitor model-confidence drift + add an "
          "adversarial-input detector before inference.")


if __name__ == "__main__":
    main()
