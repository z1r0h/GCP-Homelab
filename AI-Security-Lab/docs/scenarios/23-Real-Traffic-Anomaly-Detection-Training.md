# 🚀 Scenario 23 Detailed Guide: Real-Traffic AI Anomaly Detection Training

> **✅ Dependencies provisioned.** DVWA (port 8081) and Juice Shop (port 3000) are wired
> into `docker-compose.yml` (`targets` profile), and the Isolation Forest model lives in
> `apps/ml-notebooks/train_isolation_forest.ipynb`. This scenario feeds Scenario 11 with
> richer training data.

## 📖 1. Background & Theory
**Framework Mapping**: MITRE ATT&CK: TA0008, TA0010 · OWASP LLM04 (data quality)

In Scenario 11 the anomaly model trains on clean, uniform logs from our minimal Flask apps — easy data that does not reflect production noise. A real vulnerable web app (DVWA / Juice Shop) under mixed legitimate + attack traffic produces a far richer, noisier baseline. Training the model on this realistic distribution dramatically improves its ability to separate true anomalies from benign variance.

**Objective**: Generate a realistic mixed-traffic dataset against DVWA/Juice Shop, retrain the Isolation Forest model on it, and demonstrate improved precision/recall versus the Scenario 11 baseline.

---

## 🛠️ 2. Environment Setup
1. Ensure Docker is running on the lab VM.
2. Start targets (DVWA/Juice Shop) and defense:
```bash
docker compose -f infrastructure/docker-compose.yml --profile targets --profile defense --profile ml up -d
```
3. Open Jupyter Lab at `http://localhost:8889` (token: cyberlab) and re-use `train_isolation_forest.ipynb` (notebooks are mounted at `/home/jovyan/work`).
4. Confirm Splunk HEC is ingesting web access logs.

---

## 🔴 3. Red Team Walkthrough (Attack)
**Command:**
```bash
docker exec -it kali bash
# Generate baseline "normal" traffic, then interleave attacks:
for i in $(seq 1 500); do curl -s http://juice-shop:3000/rest/products > /dev/null; sleep 1; done &
sqlmap -u "http://juice-shop:3000/rest/products/search?q=1" --batch --level=3
```

**What is happening?**
We produce a mixed stream: hundreds of legitimate API calls plus an interleaved SQLi campaign. This mirrors how attacks hide inside normal production traffic.

**Expected Output:**
A captured log dataset (normal + malicious labelled where known). **Screenshot the traffic-generation terminal and save it to `evidence/`.**

---

## 🔵 4. Blue Team Walkthrough (Detection)
In Jupyter, retrain and compare:

```python
# Retrain Isolation Forest on the new realistic dataset
model.fit(X_realistic_train)
preds = model.predict(X_test)   # -1 = anomaly
# Compare precision/recall vs the Scenario 11 baseline model
```

Then validate in Splunk:
```spl
index=ml_alerts sourcetype=isolation_forest model_version=realistic_v2
| search anomaly_score = -1
| table _time, src_ip, uri_path, anomaly_reason
```

**Analysis:**
Confirm the realistic-trained model catches the SQLi campaign while raising fewer false positives on benign traffic than the Scenario 11 baseline. **Screenshot the precision/recall comparison and save it to `evidence/`.**

---

## 🛡️ 5. Mitigation & Fix
**Recommendation:**
> Adopt a continuous-retraining pipeline: periodically refresh the anomaly baseline from production-like traffic so the model adapts to drift, and version models so detections are reproducible and auditable.

*Once complete, fill out `scenarios/23-real-traffic-anomaly/README.md` and push to GitHub!*
