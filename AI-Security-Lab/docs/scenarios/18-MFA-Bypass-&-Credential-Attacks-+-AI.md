# 🚀 Scenario 18 Detailed Guide: MFA Bypass & Credential Attacks + AI

> **⚠️ Prerequisite — Windows VM.** The spray targets a Windows host and is detected via WinEventLog 4625 (`index=wineventlog`). Build the AD/client VMs first (setup `05` + `09`), and replace `WIN_CLIENT_IP` below with the client VM's VPC-internal IP.

## 📖 1. Background & Theory
**Framework Mapping**: ATT&CK: T1556, T1110

Instead of using RockYou.txt, AI can scrape a company's LinkedIn and generate passwords like `CompanyName2025!`. A slow spray (1 attempt/hour/user) evades normal lockout rules.

**Objective**: Use AI to generate highly targeted password dictionaries based on OSINT, execute a slow spray attack, and detect it using Splunk statistical modeling.

---

## 🛠️ 2. Environment Setup
1. SSH into the GCP lab VM via IAP and ensure Docker is running (`docker ps`).
2. Execute the following command to prepare the target environment:
```bash
docker exec -it kali bash
```
3. Ensure Splunk HEC is receiving logs over the VPC-internal network.

---

## 🔴 3. Red Team Walkthrough (Attack)
Follow these exact steps to simulate the attack.

**Command:**
```bash
# Spray RDP on the Windows client so each failed logon produces WinEventLog 4625 (matches the detection).
hydra -L users.txt -P ai_generated_passwords.txt rdp://WIN_CLIENT_IP -t 1 -w 3600
```

**What is happening?**
We run a highly distributed, slow password spray attack over several hours.

**Expected Output:**
You should see a successful execution or data exfiltration on your attacker terminal. **Take a screenshot and save it to the `evidence/` folder in the scenario directory.**

---

## 🔵 4. Blue Team Walkthrough (Detection)
Now that the attack has occurred, switch to your Splunk Web Interface (GCP IAP Tunnel).

1. Open `Apps -> Search & Reporting`.
2. Set the Time Range to `Last 15 minutes` to filter out noise.
3. Run the following Advanced SPL query:

```spl
index=wineventlog EventCode=4625
| bin _time span=24h
| stats count as failures, dc(Account_Name) as targeted_users by Source_Network_Address
| where targeted_users > 5 AND failures < 50
# Detects low-and-slow spraying across multiple accounts.
```

**Analysis:**
This query searches the logs and correlates the malicious indicators. Review the results table. **Take a screenshot of the detected attack and save it to the `evidence/` folder.**

---

## 🛡️ 5. Mitigation & Fix
To secure the system against this vulnerability, implement the following:

**Recommendation:**
> Enforce phishing-resistant MFA (FIDO2/WebAuthn). Block legacy authentication protocols.

*Once you have completed these steps, fill out the `README.md` file in this scenario's directory and push your changes to GitHub!*
