# 🚀 Scenario 11 Detailed Guide: AI Anomaly Detection (Isolation Forest)

## 📖 1. Background & Theory
**Framework Mapping**: ATT&CK: TA0008, TA0010

Signature-based rules often miss low-and-slow attacks. Isolation Forest is an unsupervised algorithm that isolates anomalies (outliers) in a dataset without needing labeled malicious data.

**Objective**: Train an unsupervised machine learning model to establish a network baseline and detect slow, stealthy C2 beaconing.

---

## 🛠️ 2. Environment Setup
1. SSH into the GCP lab VM via IAP and ensure Docker is running (`docker ps`).
2. Execute the following command to prepare the target environment:
```bash
docker compose -f infrastructure/docker-compose.yml --profile ml up -d jupyter-ml-lab
# Open http://localhost:8889 (token: cyberlab) and run train_isolation_forest.ipynb.
# The notebook trains on a SYNTHETIC baseline; feeding real 7-day Sysmon EventID 3 data is optional.
```
3. Ensure Splunk HEC is receiving logs over the VPC-internal network.

---

## 🔴 3. Red Team Walkthrough (Attack)
Follow these exact steps to simulate the attack.

**Command:**
```bash
docker exec -it kali bash
# Beacon against a real target on target-net (juice-shop). NOTE: the notebook flags a
# *synthetic* beacon it injects itself — this loop just illustrates the traffic pattern.
while true; do curl -s http://juice-shop:3000/ >/dev/null; sleep 300; done
```

**What is happening?**
We simulate a slow C2 beacon sending an HTTP request every 5 minutes. Traditional threshold rules (e.g., >100 req/min) will completely miss this.

**Expected Output:**
You should see a successful execution or data exfiltration on your attacker terminal. **Take a screenshot and save it to the `evidence/` folder in the scenario directory.**

---

## 🔵 4. Blue Team Walkthrough (Detection)
Now that the attack has occurred, switch to your Splunk Web Interface (GCP IAP Tunnel).

1. Open `Apps -> Search & Reporting`.
2. Set the Time Range to `Last 15 minutes` to filter out noise.
3. Run the following Advanced SPL query:

```spl
index=ml_alerts sourcetype=isolation_forest
| search anomaly_score = -1
| table _time, src_ip, dest_ip, bytes_out, anomaly_reason
```

**Analysis:**
This query searches the logs and correlates the malicious indicators. Review the results table. **Take a screenshot of the detected attack and save it to the `evidence/` folder.**

---

## 🛡️ 5. Mitigation & Fix
To secure the system against this vulnerability, implement the following:

**Recommendation:**
> Integrate ML anomaly scores directly into Splunk dashboards to alert on highly abnormal statistical deviations.

*Once you have completed these steps, fill out the `README.md` file in this scenario's directory and push your changes to GitHub!*
