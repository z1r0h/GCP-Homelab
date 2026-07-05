# 🚀 Scenario 14 Detailed Guide: AI-Powered Automated SOAR

## 📖 1. Background & Theory
**Framework Mapping**: NIST CSF: RS.RP, RS.MI

By chaining SIEM -> AI Analysis -> Firewall/EDR APIs, we can achieve sub-minute response times. The AI acts as the decision engine determining if isolation is necessary.

**Objective**: Build an AI-driven Security Orchestration, Automation, and Response (SOAR) playbook that investigates alerts and autonomously isolates compromised hosts.

---

## 🛠️ 2. Environment Setup
1. SSH into the GCP lab VM via IAP and ensure Docker is running (`docker ps`).
2. Start a target (DVWA has a classic SQLi login), then arm the playbook:
```bash
docker compose -f infrastructure/docker-compose.yml up -d dvwa
# soar_playbook.py reads SPLUNK_HEC/SPLUNK_TOKEN/EDR_API from env; it is DRY-RUN unless --execute
python3 scripts/soar_playbook.py --demo
```
3. Ensure Splunk HEC is receiving logs over the VPC-internal network.

---

## 🔴 3. Red Team Walkthrough (Attack)
Follow these exact steps to simulate the attack.

**Command:**
```bash
docker exec -it kali sqlmap -u "http://dvwa/login.php?id=1" --batch --dbs   # DVWA reachable as http://dvwa on target-net (or http://localhost:8081 from the host)
```

**What is happening?**
We launch a loud SQLi attack. Splunk triggers a high-severity alert. The SOAR script intercepts it, asks Ollama for verification, and upon 95% confidence, calls the Wazuh API to drop the attacker's IP.

**Expected Output:**
You should see a successful execution or data exfiltration on your attacker terminal. **Take a screenshot and save it to the `evidence/` folder in the scenario directory.**

---

## 🔵 4. Blue Team Walkthrough (Detection)
Now that the attack has occurred, switch to your Splunk Web Interface (GCP IAP Tunnel).

1. Open `Apps -> Search & Reporting`.
2. Set the Time Range to `Last 15 minutes` to filter out noise.
3. Run the following Advanced SPL query:

```spl
index=ai_logs sourcetype=ai_soar
| timechart count by action_taken
# Look for 'host_isolated' or 'ip_blocked' events correlating with the attack time.
```

**Analysis:**
This query searches the logs and correlates the malicious indicators. Review the results table. **Take a screenshot of the detected attack and save it to the `evidence/` folder.**

---

## 🛡️ 5. Mitigation & Fix
To secure the system against this vulnerability, implement the following:

**Recommendation:**
> Defensive scenario. Ensure the AI SOAR has 'fail-safe' thresholds (e.g., do not isolate Domain Controllers automatically) to prevent self-inflicted Denial of Service.

*Once you have completed these steps, fill out the `README.md` file in this scenario's directory and push your changes to GitHub!*
