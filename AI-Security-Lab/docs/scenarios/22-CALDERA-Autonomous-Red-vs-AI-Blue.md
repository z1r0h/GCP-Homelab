# 🚀 Scenario 22 Detailed Guide: CALDERA Autonomous Red vs AI Blue

> **✅ Dependencies provisioned.** `ai_soc_triage.py` is in `scripts/`. CALDERA is wired
> into `docker-compose.yml` (`offense` profile, port 8888) — note it has no official
> Docker Hub image, so clone & build it first:
> `git clone https://github.com/mitre/caldera.git --recursive external/caldera`.
> This scenario is the recommended *prerequisite* for Scenario 20 (Final Boss).

## 📖 1. Background & Theory
**Framework Mapping**: MITRE ATT&CK (full chain) · ATLAS: AML.T0016

CALDERA is MITRE's adversary-emulation platform. With autonomous planners it chains ATT&CK techniques (discovery → privilege escalation → lateral movement) without human input. Pairing it against an AI blue-team triage loop creates a controlled, repeatable **machine-vs-machine** exercise — a smaller, focused rehearsal before the Scenario 20 grand finale.

**Objective**: Run CALDERA in autonomous mode against the target network while an AI SOC triage loop ingests Wazuh alerts in real time, and measure detection coverage and time-to-detect.

---

## 🛠️ 2. Environment Setup
1. Ensure Docker is running on the lab VM and the lab is up.
2. Start defense + offense + targets:
```bash
docker compose -f infrastructure/docker-compose.yml --profile all up -d
```
3. Deploy a CALDERA `sandcat` agent onto a target container so CALDERA has a foothold to operate from.
4. Start the AI triage loop on the host: `python3 scripts/ai_soc_triage.py`.

---

## 🔴 3. Red Team Walkthrough (Attack)
**Command:**
```bash
# In the CALDERA web UI (https://localhost:8888), start an operation:
#   - Adversary profile: "Discovery + Lateral Movement"
#   - Planner: autonomous (batch)
# Or via API:
curl -X POST http://localhost:8888/api/v2/operations -H "KEY: $CALDERA_API_KEY" \
  -d '{"name":"auto-op","adversary":{"adversary_id":"<id>"},"planner":{"id":"batch"}}'
```

**What is happening?**
CALDERA's planner autonomously selects and executes ATT&CK abilities through the sandcat agent, adapting based on results — no operator clicks required.

**Expected Output:**
A populated operation timeline showing executed techniques (T1046, T1021, etc.). **Screenshot the operation graph and save it to `evidence/`.**

---

## 🔵 4. Blue Team Walkthrough (Detection)
The `ai_soc_triage.py` loop should already be summarizing alerts. Verify in Splunk:

1. Open `Apps -> Search & Reporting`.
2. Run:

```spl
index=ai_logs sourcetype=ai_soc_triage
| spath path=mitre_technique
| stats count BY mitre_technique, classification
| sort - count
```

**Analysis:**
Compare the techniques the AI flagged (`classification="TruePositive"`) against CALDERA's actual operation timeline. Every missed technique is a detection gap. **Screenshot the comparison and save it to `evidence/`.**

---

## 🛡️ 5. Mitigation & Fix
**Recommendation:**
> Use the gap analysis to write new Wazuh/Sigma rules for any technique the AI triage missed, then re-run the operation to confirm coverage improves (purple-team feedback loop).

*Once complete, fill out `scenarios/22-caldera-vs-ai-blue/README.md` and push to GitHub!*
