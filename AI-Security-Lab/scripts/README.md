# ⚙️ Automation Scripts

## Lab control (Bash — run on the GCP lab VM)
- `start_lab.sh`: Interactive menu to start Docker profiles (defense / targets / offense / all / stop). Prompts to clone CALDERA if missing before starting offense/all. Run: `bash scripts/start_lab.sh`
- `verify_health.sh`: Run before any scenario to check Ollama, Splunk HEC (same-VPC internal IP, set `SPLUNK_HEC_URL`), and Docker container status. Run: `bash scripts/verify_health.sh`
- `recover_vm.sh`: **One-command VM recovery** from a `baseline-<vm>` snapshot (see `docs/setup/12`). Rebuilds the boot disk + instance with the correct machine/GPU/Spot/network profile. Run where gcloud is authenticated (Cloud Shell or laptop), NOT on the VM: `bash scripts/recover_vm.sh cyber-ai-lab-vm asia-southeast1-a`

## Blue-team automation (Python)
> `pip install -r requirements.txt`

- `ai_soc_triage.py`: AI SOC analyst (Scenario 10) — tails Wazuh alerts, asks Ollama for True/False-Positive + MITRE mapping, forwards verdicts to Splunk HEC. Try `--demo`.
- `soar_playbook.py`: AI SOAR auto-response (Scenario 14) — high-confidence Critical alerts trigger an EDR isolate call (dry-run by default; `--execute` to arm). Try `--demo`.
- `nl_to_spl.py`: Natural-language-to-SPL middleware (Scenario 12) — Flask service turning English hunting questions into SPL via Ollama. `--once "..."` for one-shot.

> Red-team offensive scripts (`ai_pentest_agent.py`, `model_extractor.py`,
> `generate_adv_samples.py`) live in `../tools/`.
