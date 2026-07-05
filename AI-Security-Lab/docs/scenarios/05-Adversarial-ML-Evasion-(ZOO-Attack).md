# 🚀 Scenario 05 Detailed Guide: Adversarial ML Evasion (ZOO Attack)

## 📖 1. Background & Theory
**Framework Mapping**: ATLAS: AML.T0015

ML models rely on specific statistical boundaries. By mathematically altering the input features just enough (perturbation), we can cross the decision boundary without destroying the exploit payload's functionality.

**Objective**: Use the Adversarial Robustness Toolbox (ART) to apply perturbations to malicious network traffic features, causing an ML classifier to predict it as benign.

---

## 🛠️ 2. Environment Setup
1. SSH into the GCP lab VM via IAP and ensure Docker is running (`docker ps`).
2. Prepare the target model + attack deps (there is no Jupyter service in compose — run the tooling on the host):
```bash
# Start the target model API; it trains & caches target_classifier.pkl on first boot
docker compose -f infrastructure/docker-compose.yml up -d target-ml-api
# Export the trained model out of the container to use as the ZOO attack target
docker cp "$(docker ps -qf name=target-ml-api)":/app/target_classifier.pkl .
# Install attack deps (IBM ART, scikit-learn, numpy) on the host
pip install -r tools/requirements.txt
```
3. Ensure Splunk HEC is receiving logs over the VPC-internal network.

---

## 🔴 3. Red Team Walkthrough (Attack)
Follow these exact steps to simulate the attack.

**Command:**
```bash
python3 tools/generate_adv_samples.py --model target_classifier.pkl --method zoo
# (--dataset is optional; without it the script auto-generates synthetic malicious samples)
```

**What is happening?**
The script uses Zeroth-Order Optimization (ZOO) to modify traffic features (like byte variance). The generated adversarial samples will bypass the ML detection engine.

**Expected Output:**
You should see a successful execution or data exfiltration on your attacker terminal. **Take a screenshot and save it to the `evidence/` folder in the scenario directory.**

---

## 🔵 4. Blue Team Walkthrough (Detection)
Now that the attack has occurred, switch to your Splunk Web Interface (GCP IAP Tunnel).

1. Open `Apps -> Search & Reporting`.
2. Set the Time Range to `Last 15 minutes` to filter out noise.
3. Run the following Advanced SPL query:

```spl
index=ml_alerts sourcetype=model_metrics
| timechart avg(confidence_score) as avg_confidence by predicted_class
| eval drift_detected=if(avg_confidence < 0.8, 1, 0)
# Look for sudden drops in model confidence on 'benign' traffic.
```

**Analysis:**
This query searches the logs and correlates the malicious indicators. Review the results table. **Take a screenshot of the detected attack and save it to the `evidence/` folder.**

---

## 🛡️ 5. Mitigation & Fix
To secure the system against this vulnerability, implement the following:

**Recommendation:**
> Implement Adversarial Training (train the model on adversarial examples) and add an anomaly detector before the classifier to catch perturbed inputs.

*Once you have completed these steps, fill out the `README.md` file in this scenario's directory and push your changes to GitHub!*
