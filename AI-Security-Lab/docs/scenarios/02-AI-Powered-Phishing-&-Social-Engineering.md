# 🚀 Scenario 02 Detailed Guide: AI-Powered Phishing & Social Engineering

## 📖 1. Background & Theory
**Framework Mapping**: MITRE ATT&CK: T1566 / ATLAS: AML.T0048

Traditional phishing often suffers from poor grammar or generic context. AI-generated phishing uses OSINT data to craft perfectly personalized emails, increasing success rates dramatically.

**Objective**: Leverage LLMs to generate highly convincing, context-aware phishing emails without grammar errors, and develop detection mechanisms based on language patterns and sender anomalies.

---

## 🛠️ 2. Environment Setup
1. SSH into the GCP lab VM via IAP and ensure Docker is running (`docker ps`).
2. Execute the following command to prepare the target environment:
```bash
docker compose up -d gophish
```
3. Ensure Splunk HEC is receiving logs over the VPC-internal network.

---

## 🔴 3. Red Team Walkthrough (Attack)
Follow these exact steps to simulate the attack.

**Command:**
```bash
curl http://localhost:11434/api/generate -d '{"model":"llama3.1:8b", "prompt":"Write a highly urgent phishing email from IT support about VPN deactivation..."}'
```

**What is happening?**
Generate the email payload and use the GoPhish dashboard on port 3333 to launch the campaign against simulated internal users.

**Expected Output:**
You should see a successful execution or data exfiltration on your attacker terminal. **Take a screenshot and save it to the `evidence/` folder in the scenario directory.**

---

## 🔵 4. Blue Team Walkthrough (Detection)
Now that the attack has occurred, switch to your Splunk Web Interface (GCP IAP Tunnel).

> ⚠️ **No live email feed in this lab.** There is no mail gateway forwarding to Splunk, so
> `index=email_gateway` is empty by default. To exercise the SPL, inject a representative
> sample event via HEC (use a token whose allowed-index list includes `email_gateway`):
> ```bash
> curl -k https://YOUR_SPLUNK_INTERNAL_IP:8088/services/collector \
>   -H "Authorization: Splunk YOUR_SPLUNK_HEC_TOKEN" \
>   -d '{"index":"email_gateway","sourcetype":"smtp","event":{"sender":"it-support@evil.com","subject":"URGENT: VPN deactivation","body":"Your VPN will be deactivated immediately — click https://evil.com/vpn to keep access"}}'
> ```

1. Open `Apps -> Search & Reporting`.
2. Set the Time Range to `Last 15 minutes` to filter out noise.
3. Run the following Advanced SPL query:

```spl
index=email_gateway sourcetype=smtp
| search body="*urgent*" OR body="*deactivated*" OR body="*immediately*"
| eval has_suspicious_link=if(match(body, "https?://(?!.*yourcompany\.com).*"), 1, 0)
| where has_suspicious_link=1
```

**Analysis:**
This query searches the logs and correlates the malicious indicators. Review the results table. **Take a screenshot of the detected attack and save it to the `evidence/` folder.**

---

## 🛡️ 5. Mitigation & Fix
To secure the system against this vulnerability, implement the following:

**Recommendation:**
> Implement DMARC/DKIM/SPF strictly. Train email security gateways with ML models that detect artificial urgency and unexpected sender domains.

*Once you have completed these steps, fill out the `README.md` file in this scenario's directory and push your changes to GitHub!*
