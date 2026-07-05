# 🚀 Scenario 16 Detailed Guide: Data Poisoning Defense

## 📖 1. Background & Theory
**Framework Mapping**: ATLAS: AML.T0020, OWASP: LLM04

If an attacker controls telemetry that feeds into a model retraining pipeline, they can slowly introduce mislabeled data. Over time, the model's decision boundary shifts, allowing malware to pass as benign.

**Objective**: Simulate an attacker slowly poisoning a training dataset to degrade model accuracy, and implement Data Drift monitoring to catch it.

---

## 🛠️ 2. Environment Setup
1. SSH into the GCP lab VM via IAP and ensure Docker is running (`docker ps`).
2. Execute the following command to prepare the target environment:
```bash
docker compose -f infrastructure/docker-compose.yml --profile ml up -d jupyter-ml-lab
# Open http://localhost:8889 (token: cyberlab). NOTE: data_poisoning_drift.ipynb is a STUB —
# build it per apps/ml-notebooks/README.md, or adapt train_isolation_forest.ipynb.
```
3. Ensure Splunk HEC is receiving logs over the VPC-internal network.

---

## 🔴 3. Red Team Walkthrough (Attack)
Follow these exact steps to simulate the attack.

**Command:**
```bash
echo '192.168.1.100, 4444, 50000, 0' >> dataset_baseline.csv
```

**What is happening?**
We append 1% malicious C2 traffic but label it as '0' (Benign). When the model retrains on Sunday, it learns that port 4444 traffic is normal.

**Expected Output:**
You should see a successful execution or data exfiltration on your attacker terminal. **Take a screenshot and save it to the `evidence/` folder in the scenario directory.**

---

## 🔵 4. Blue Team Walkthrough (Detection)
Now that the attack has occurred, switch to your Splunk Web Interface (GCP IAP Tunnel).

1. Open `Apps -> Search & Reporting`.
2. Set the Time Range to `Last 15 minutes` to filter out noise.
3. Run the following Advanced SPL query:

```spl
index=ml_alerts sourcetype=data_drift
| search event="Data Drift Detected"
| table _time, feature, drift_score, threshold
```

**Analysis:**
This query searches the logs and correlates the malicious indicators. Review the results table. **Take a screenshot of the detected attack and save it to the `evidence/` folder.**

---

## 🛡️ 5. Mitigation & Fix
To secure the system against this vulnerability, implement the following:

**Recommendation:**
> Implement rigorous data provenance checks. Use statistical drift detection (e.g., Kullback-Leibler divergence) on new data batches before allowing retraining to proceed.

*Once you have completed these steps, fill out the `README.md` file in this scenario's directory and push your changes to GitHub!*
