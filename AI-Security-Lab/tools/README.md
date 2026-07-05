# tools/ — Red-Team & Offensive Automation Scripts

Attack-side automation run from Kali or the host. **Authorized lab use only.**

| Script | Scenario | What it does |
|--------|----------|--------------|
| `ai_pentest_agent.py` | 01, 21 | LLM-driven recon→plan loop against lab targets (dry-run by default) |
| `model_extractor.py` | 08 | Harvests `/predict` confidences, trains a shadow model |
| `generate_adv_samples.py` | 05 | ZOO black-box evasion vs the target classifier |

Install deps:
```bash
pip install -r tools/requirements.txt
```

Blue-team / defensive automation lives in `../scripts/` (`ai_soc_triage.py`,
`soar_playbook.py`, `nl_to_spl.py`).
