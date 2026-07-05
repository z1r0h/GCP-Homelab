# 📝 Scenario 22: CALDERA Autonomous Red vs AI Blue

> **Setup** — `ai_soc_triage.py` is in `scripts/`. CALDERA is in `docker-compose.yml`
> (`offense` profile, 8888) but has **no official image** — clone & build it first:
> `git clone https://github.com/mitre/caldera.git --recursive external/caldera`.
> Recommended prerequisite for Scenario 20 (Final Boss).

## 📋 Executive Summary

| Item | Details |
|:---|:---|
| **Date Executed** | YYYY-MM-DD |
| **Difficulty Level** | ⭐⭐⭐⭐ |
| **Time Spent** | X hours |
| **Framework Mapping** | MITRE ATT&CK (full chain) / ATLAS: AML.T0016 |
| **Attack Status** | Success / Partial Success / Failed |
| **Detection Status** | Detected / Partially Detected / Undetected |

## 🎯 Objective
Run CALDERA in autonomous mode against the target network while an AI SOC triage loop ingests Wazuh alerts in real time. Measure detection coverage and time-to-detect (machine vs machine).

## 🏗️ Lab Environment

| Component | Details |
|:---|:---|
| Attacker / C2 | [e.g., CALDERA + sandcat agent on target] |
| Target Network | [e.g., target-net 10.10.30.0/24] |
| Detection / Monitor | [e.g., Wazuh + ai_soc_triage.py -> Splunk] |
| AI Model Used | [e.g., Ollama - llama3.1:8b] |

---

## 🔴 Attack Execution

### Step 1: Start autonomous CALDERA operation
**Action/Command:**
```bash
# CALDERA UI (https://localhost:8888): Adversary = Discovery+Lateral, Planner = autonomous
```

**Result:**
[Which ATT&CK techniques did CALDERA execute? Record the operation timeline.]

**Evidence:**
> `![CALDERA Operation](evidence/01-caldera-op.png)`

---

## 🔵 Detection & Analysis

### Wazuh Alerts (if applicable)
| Time | Rule ID | Description | Level |
|:---|:---|:---|:---|
| HH:MM:SS | XXXXX | [Alert description] | High |

### Splunk Detection
**SPL Query Used:**
```spl
index=ai_logs sourcetype=ai_soc_triage | stats count BY mitre_technique, classification
```

**Results Analysis:**
[Compare AI-flagged techniques vs CALDERA's actual timeline. List detection gaps.]

**Evidence:**
> `![Coverage Comparison](evidence/coverage.png)`

---

## 🛡️ Mitigations & Recommendations

| # | Mitigation | Priority | Status |
|:---|:---|:---|:---|
| 1 | [e.g., New Wazuh rule for missed technique] | High | ⬜ Planned |

## 📝 Lessons Learned
1. [How well did the AI triage keep up with autonomous attack speed?]
2. [Which techniques slipped past detection, and why?]

## 📚 References
- MITRE CALDERA · MITRE ATT&CK · MITRE ATLAS
