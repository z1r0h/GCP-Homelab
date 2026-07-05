# 📝 Scenario 23: Real-Traffic AI Anomaly Detection Training

> **✅ Dependencies provisioned** — DVWA (8081) & Juice Shop (3000) are wired into
> `docker-compose.yml` (`targets` profile); reuses the Scenario 11 Isolation Forest
> model. Feeds Scenario 11 with realistic training data. Not yet executed (awaiting lab ignition).

## 📋 Executive Summary

| Item | Details |
|:---|:---|
| **Date Executed** | YYYY-MM-DD |
| **Difficulty Level** | ⭐⭐⭐ |
| **Time Spent** | X hours |
| **Framework Mapping** | MITRE ATT&CK: TA0008, TA0010 / OWASP LLM04 |
| **Attack Status** | Success / Partial Success / Failed |
| **Detection Status** | Detected / Partially Detected / Undetected |

## 🎯 Objective
Generate realistic mixed (legitimate + attack) traffic against DVWA/Juice Shop, retrain the Isolation Forest model on it, and demonstrate improved precision/recall versus the Scenario 11 baseline.

## 🏗️ Lab Environment

| Component | Details |
|:---|:---|
| Traffic Generator | [e.g., Kali: curl loop + sqlmap] |
| Target IP / Service | [e.g., 10.10.30.x:3000, Juice Shop / DVWA] |
| ML Workbench | [e.g., apps/ml-notebooks/train_isolation_forest.ipynb] |
| Detection / Monitor | [e.g., Splunk via HEC] |

---

## 🔴 Attack Execution

### Step 1: Generate mixed traffic dataset
**Action/Command:**
```bash
# 500 legit calls interleaved with an sqlmap campaign (see detailed guide)
```

**Result:**
[Describe the captured dataset: volume, normal/malicious ratio, labelling.]

**Evidence:**
> `![Traffic Generation](evidence/01-traffic-gen.png)`

---

## 🔵 Detection & Analysis

### Model Retraining (Jupyter)
```python
model.fit(X_realistic_train)
preds = model.predict(X_test)   # -1 = anomaly
```

### Splunk Detection
**SPL Query Used:**
```spl
index=ml_alerts sourcetype=isolation_forest model_version=realistic_v2 anomaly_score=-1
```

**Results Analysis:**
[Compare precision/recall: realistic-trained model vs Scenario 11 baseline. Did false positives drop?]

**Evidence:**
> `![Precision/Recall Comparison](evidence/comparison.png)`

---

## 🛡️ Mitigations & Recommendations

| # | Mitigation | Priority | Status |
|:---|:---|:---|:---|
| 1 | [e.g., Continuous retraining pipeline + model versioning] | Medium | ⬜ Planned |

## 📝 Lessons Learned
1. [How did realistic training data change model performance?]
2. [What does this imply about deploying ML detection in production?]

## 📚 References
- scikit-learn Isolation Forest · OWASP Juice Shop · MITRE ATT&CK
