# 🚀 Scenario 08 Detailed Guide: Model Extraction & Membership Inference

## 📖 1. Background & Theory
**Framework Mapping**: ATLAS: AML.T0024, AML.T0025

If an ML API returns exact confidence probabilities, an attacker can send thousands of random queries, collect the input-output pairs, and train a 'shadow model' that perfectly mimics the victim model.

**Objective**: Steal an ML model's parameters by querying its API repeatedly, and determine if specific data was used in the training set.

---

## 🛠️ 2. Environment Setup
1. SSH into the GCP lab VM via IAP and ensure Docker is running (`docker ps`).
2. Execute the following command to prepare the target environment:
```bash
docker compose up -d target-ml-api
```
3. Ensure Splunk HEC is receiving logs over the VPC-internal network.

---

## 🔴 3. Red Team Walkthrough (Attack)
Follow these exact steps to simulate the attack.

**Command:**
```bash
python3 tools/model_extractor.py --api http://localhost:5005/predict --queries 5000 --output shadow_model.pkl
```

**What is happening?**
The script floods the API with uniform random feature queries. It then uses the high-precision probability responses to train a local replica.

**Expected Output:**
You should see a successful execution or data exfiltration on your attacker terminal. **Take a screenshot and save it to the `evidence/` folder in the scenario directory.**

---

## 🔵 4. Blue Team Walkthrough (Detection)
Now that the attack has occurred, switch to your Splunk Web Interface (GCP IAP Tunnel).

1. Open `Apps -> Search & Reporting`.
2. Set the Time Range to `Last 15 minutes` to filter out noise.
3. Run the following Advanced SPL query:

```spl
index=ai_logs sourcetype=ml_api endpoint="/predict"
| bin _time span=1m
| stats count as request_count by src_ip, _time
| where request_count > 500
| table _time, src_ip, request_count
```

**Analysis:**
This query searches the logs and correlates the malicious indicators. Review the results table. **Take a screenshot of the detected attack and save it to the `evidence/` folder.**

---

## 🛡️ 5. Mitigation & Fix
To secure the system against this vulnerability, implement the following:

**Recommendation:**
> Apply rate limiting to prediction endpoints. Round probabilities to 2 decimal places or only return class labels (Top-1) to reduce information leakage.

*Once you have completed these steps, fill out the `README.md` file in this scenario's directory and push your changes to GitHub!*
