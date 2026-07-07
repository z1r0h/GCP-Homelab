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
docker compose -f infrastructure/docker-compose.yml up -d gophish mailpit
```
3. **One-time only**: log into GoPhish at `https://localhost:3333` (self-signed cert,
   accept the browser warning), go to **Settings**, generate an API key, and:
   ```bash
   export GOPHISH_API_KEY="paste-the-key-here"
   ```
4. Ensure Splunk HEC is receiving logs over the VPC-internal network.

---

## 🔴 3. Red Team Walkthrough (Attack)
Follow these exact steps to simulate the attack.

**Command:**
```bash
python3 tools/phishing_campaign.py --launch
```

**What is happening?**
Ollama writes the phishing email, then the script creates (or reuses) the GoPhish
sending profile/template/landing page/target group and launches a real campaign —
sent via Mailpit rather than a real mail server, so nothing leaves the lab. The
script then stops and hands off to **you**: open `http://localhost:8025` (Mailpit),
read the email like the target would, and click the link inside it yourself. A
script can't authentically play "the human who fell for it" — that part is on you.

Once you've clicked it, pull the real results:
```bash
python3 tools/phishing_campaign.py --report <campaign_id>   # id printed by --launch
```
This forwards the real email content plus GoPhish's real `opened`/`clicked` counts
to Splunk (`index=email_gateway`).

**Expected Output:**
`--launch` prints the generated email and a campaign ID. After you click the link
in Mailpit, `--report` should show `clicked: 1` (and very likely `opened: 1` too —
Mailpit's web UI doesn't block remote images/tracking pixels by default). **Take a
screenshot of the email in Mailpit and the `--report` output, save to `evidence/`.**

---

## 🔵 4. Blue Team Walkthrough (Detection)
Now that the attack has occurred, switch to your Splunk Web Interface (GCP IAP Tunnel).

> ✅ **Real data, not a sample injection.** `tools/phishing_campaign.py --report` forwards
> the actual GoPhish campaign — the real generated email content and the real
> `opened`/`clicked` counts from you clicking the link in Mailpit — to
> `index=email_gateway sourcetype=smtp` via Splunk HEC. Nothing below needs manual
> sample data; run `--report` first if you haven't yet.

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
