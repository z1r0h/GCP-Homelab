# 🚀 Scenario 13 Detailed Guide: Deepfake Detection & Defense

## 📖 1. Background & Theory
**Framework Mapping**: ATLAS: AML.T0048

AI voice cloning (Deepfakes) are increasingly used in vishing/BEC attacks. Synthetic audio often lacks high-frequency breath sounds and has abnormally smooth Mel Spectrograms compared to human voices.

**Objective**: Generate synthetic voice audio using TTS and build a spectral analysis pipeline to detect the deepfake.

---

## 🛠️ 2. Environment Setup
1. SSH into the GCP lab VM via IAP and ensure Docker is running (`docker ps`).
2. Execute the following command to prepare the target environment:
```bash
docker compose -f infrastructure/docker-compose.yml --profile ml up -d jupyter-ml-lab
# Open http://localhost:8889 (token: cyberlab), then in a notebook cell: pip install TTS
# NOTE: deepfake_mel_spectrogram.ipynb is a STUB — build it per apps/ml-notebooks/README.md.
```
3. Ensure Splunk HEC is receiving logs over the VPC-internal network.

---

## 🔴 3. Red Team Walkthrough (Attack)
Follow these exact steps to simulate the attack.

**Command:**
```bash
from TTS.api import TTS
tts = TTS('tts_models/en/ljspeech/tacotron2-DDC')
tts.tts_to_file('Wire 50k to vendor immediately.', file_path='fake.wav')
```

**What is happening?**
We generate a fake audio clip of an executive ordering a wire transfer. We then run our spectral analysis script against it.

**Expected Output:**
You should see a successful execution or data exfiltration on your attacker terminal. **Take a screenshot and save it to the `evidence/` folder in the scenario directory.**

---

## 🔵 4. Blue Team Walkthrough (Detection)
Now that the attack has occurred, switch to your Splunk Web Interface (GCP IAP Tunnel).

1. Open `Apps -> Search & Reporting`.
2. Set the Time Range to `Last 15 minutes` to filter out noise.
3. Run the following Advanced SPL query:

```spl
# Detection is done via Python script, not directly in Splunk initially.
# Splunk logs the result of the analysis:
index=ml_alerts sourcetype=deepfake
| search classification="synthetic"
| table _time, filename, spectral_variance, confidence
```

**Analysis:**
This query searches the logs and correlates the malicious indicators. Review the results table. **Take a screenshot of the detected attack and save it to the `evidence/` folder.**

---

## 🛡️ 5. Mitigation & Fix
To secure the system against this vulnerability, implement the following:

**Recommendation:**
> Implement mandatory out-of-band MFA (e.g., a push notification or secondary phone call) for any financial transactions requested via voice.

*Once you have completed these steps, fill out the `README.md` file in this scenario's directory and push your changes to GitHub!*
