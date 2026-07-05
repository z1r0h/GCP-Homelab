# 🚀 Scenario 12 Detailed Guide: AI Threat Hunting via NL Queries

## 📖 1. Background & Theory
**Framework Mapping**: ATT&CK: General

Threat hunting requires deep knowledge of SPL. By translating English to SPL, junior analysts can perform advanced hunts (e.g., identifying rare processes or temporal anomalies) effortlessly.

**Objective**: Develop a middleware that translates Natural Language (NL) threat hunting queries into complex Splunk SPL syntax using LLMs.

---

## 🛠️ 2. Environment Setup
1. SSH into the GCP lab VM via IAP and ensure Docker is running (`docker ps`).
2. Execute the following command to prepare the target environment:
```bash
Run the `nl_to_spl.py` middleware API locally.
```
3. Ensure Splunk HEC is receiving logs over the VPC-internal network.

---

## 🔴 3. Red Team Walkthrough (Attack)
Follow these exact steps to simulate the attack.

**Command:**
```bash
curl -X POST http://localhost:5010/translate -H "Content-Type: application/json" -d '{"query": "Find any PowerShell processes launched by Word documents in the last 7 days"}'
```

**What is happening?**
The middleware queries Ollama, which generates the correct SPL: `index=sysmon EventCode=1 Image="*powershell.exe" ParentImage="*winword.exe"`. The script then executes this against the Splunk API.

**Expected Output:**
You should see a successful execution or data exfiltration on your attacker terminal. **Take a screenshot and save it to the `evidence/` folder in the scenario directory.**

---

## 🔵 4. Blue Team Walkthrough (Detection)
Now that the attack has occurred, switch to your Splunk Web Interface (GCP IAP Tunnel).

1. Open `Apps -> Search & Reporting`.
2. Set the Time Range to `Last 15 minutes` to filter out noise.
3. Run the following Advanced SPL query:

```spl
# The AI generated SPL:
index=sysmon EventCode=1 Image="*powershell.exe" ParentImage="*winword.exe"
| table _time, host, CommandLine, ParentCommandLine
```

**Analysis:**
This query searches the logs and correlates the malicious indicators. Review the results table. **Take a screenshot of the detected attack and save it to the `evidence/` folder.**

---

## 🛡️ 5. Mitigation & Fix
To secure the system against this vulnerability, implement the following:

**Recommendation:**
> This is a defensive capability. Ensure the AI is provided with the exact schema of your Sysmon/Wazuh logs via RAG to improve SPL accuracy.

*Once you have completed these steps, fill out the `README.md` file in this scenario's directory and push your changes to GitHub!*
