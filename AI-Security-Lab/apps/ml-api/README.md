# ml-api — Target ML Model API

A deliberately over-sharing classifier endpoint, used as the **target** for:
- **Scenario 08** — Model Extraction & Membership Inference
- **Scenario 05** — Adversarial ML Evasion (ZOO attack)

## Why it's vulnerable
It returns **full-precision confidence probabilities** on every `/predict` call.
That probability surface is exactly what lets an attacker:
- clone the model with enough queries (extraction), and
- gradient-free-optimize evasive inputs (ZOO).

## API
| Method | Path | Body | Returns |
|--------|------|------|---------|
| POST | `/predict` | `{"features": [f1..f10]}` | `{prediction, confidence, probabilities}` |
| GET | `/health` | — | `{status, n_features}` |

The model (`RandomForestClassifier`, seed 42) is trained on synthetic benign/malicious
traffic at first boot and cached to `target_classifier.pkl` (reused by scenario 05's
`generate_adv_samples.py --model target_classifier.pkl`).

## Run
```bash
docker compose -f infrastructure/docker-compose.yml --profile targets up -d target-ml-api
curl -X POST http://localhost:5005/predict -H "Content-Type: application/json" \
  -d '{"features":[0.1,0.2,0.1,0.3,0.2,0.1,0.2,0.3,0.1,0.2]}'
```

## Mitigation (taught in the scenarios)
Round probabilities to 2 dp, return only Top-1 label, and rate-limit the endpoint.
