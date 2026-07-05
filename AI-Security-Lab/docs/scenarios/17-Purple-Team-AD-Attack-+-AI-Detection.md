# 🚀 Scenario 17 Detailed Guide: Purple Team AD Attack + AI Detection

> **⚠️ Prerequisite — Windows VMs.** Requires the AD DC + client VMs with Atomic Red Team installed and the Universal Forwarder shipping WinEventLog to Splunk (`index=wineventlog`). Build them first (setup `05` + `09`).

## 📖 1. Background & Theory
**Framework Mapping**: ATT&CK: General (GCP AD)

AD attacks like Pass-the-Hash or SMB lateral movement generate specific Windows Event IDs (4624, 4656, 5140). AI can correlate these seemingly disconnected events across multiple hosts into a single attack graph.

**Objective**: Execute advanced Active Directory lateral movement on the GCP Windows VMs and use local AI scripts to correlate the distributed WinEventLogs.

---

## 🛠️ 2. Environment Setup
1. SSH into the GCP lab VM via IAP and ensure Docker is running (`docker ps`).
2. Execute the following command to prepare the target environment:
```bash
Connect to GCP Win Client via RDP/IAP. Ensure Atomic Red Team is installed.
```
3. Ensure Splunk HEC is receiving logs over the VPC-internal network.

---

## 🔴 3. Red Team Walkthrough (Attack)
Follow these exact steps to simulate the attack.

**Command:**
```bash
Invoke-AtomicTest T1003.001 -TestNumbers 1
Invoke-AtomicTest T1021.002 -TestNumbers 1
```

**What is happening?**
We dump LSASS memory and attempt SMB lateral movement. The GCP Universal Forwarder sends the logs to Splunk.

**Expected Output:**
You should see a successful execution or data exfiltration on your attacker terminal. **Take a screenshot and save it to the `evidence/` folder in the scenario directory.**

---

## 🔵 4. Blue Team Walkthrough (Detection)
Now that the attack has occurred, switch to your Splunk Web Interface (GCP IAP Tunnel).

1. Open `Apps -> Search & Reporting`.
2. Set the Time Range to `Last 15 minutes` to filter out noise.
3. Run the following Advanced SPL query:

```spl
index=wineventlog EventCode=4656 ObjectName="*lsass.exe*" AccessMask="0x1410"
| table _time, host, Account_Name, Process_Name
| append [search index=wineventlog EventCode=5140 ShareName="*\\IPC$"]
```

**Analysis:**
This query searches the logs and correlates the malicious indicators. Review the results table. **Take a screenshot of the detected attack and save it to the `evidence/` folder.**

---

## 🛡️ 5. Mitigation & Fix
To secure the system against this vulnerability, implement the following:

**Recommendation:**
> Implement LAPS, disable SMBv1, enforce strict Tiered Admin access, and enable Windows Defender Credential Guard.

*Once you have completed these steps, fill out the `README.md` file in this scenario's directory and push your changes to GitHub!*
