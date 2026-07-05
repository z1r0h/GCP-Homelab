# 📓 Machine Learning Notebooks

Jupyter Notebooks for the AI/ML-specific scenarios. Start the bundled Jupyter service:

```bash
docker compose -f infrastructure/docker-compose.yml --profile ml up -d jupyter-ml-lab
# open http://localhost:8889  (token: cyberlab)  — this folder is mounted at /home/jovyan/work
```
(Or run locally on the lab VM with `pip install -r ../../tools/requirements.txt && jupyter lab`.)

> The `jupyter/scipy-notebook` image already has numpy/pandas/scikit-learn/matplotlib.
> For notebooks needing IBM ART (e.g. adversarial ZOO), run `pip install adversarial-robustness-toolbox`
> in a cell — or use the host + `tools/requirements.txt` (which pins ART).

## Available notebooks
| Notebook | Scenario(s) | Purpose |
|----------|-------------|---------|
| `train_isolation_forest.ipynb` | 11, 15, 23 | Unsupervised anomaly detection (low-and-slow C2 beaconing); reused by scenario 23 to retrain on realistic DVWA/Juice Shop traffic |

## Planned notebooks (stubs to add as you reach each scenario)
| Notebook | Scenario | Purpose |
|----------|----------|---------|
| `adversarial_ml_zoo.ipynb` | 05 | ART ZOO evasion vs the ml-api classifier (companion to `tools/generate_adv_samples.py`) |
| `dns_tunneling_rf.ipynb` | 15 | Random Forest on DNS query entropy / subdomain length |
| `data_poisoning_drift.ipynb` | 16 | KL-divergence data-drift monitor to reject poisoned retraining batches |
| `deepfake_mel_spectrogram.ipynb` | 13 | Mel-spectrogram artifact detection for synthetic audio |

## How the notebooks fit the pipeline
Anomaly scores are forwarded to Splunk HEC (`index=ml_alerts`, `sourcetype=isolation_forest`)
via the `SPLUNK_HEC` / `SPLUNK_TOKEN` env vars, so blue-team detections show up alongside
the Wazuh alerts.
