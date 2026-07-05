# 🛡️ Cyber AI Lab — AI-Powered Cybersecurity Attack & Defense Laboratory

> A fully GCP-hosted homelab for simulating real-world AI-driven cybersecurity scenarios, designed specifically to develop practical blue-team, red-team, and detection engineering skills.

## 🎯 Project Overview

This project serves as a submodule to the existing `GCP-Homelab` repository, focusing entirely on the intersection of Artificial Intelligence and Cybersecurity. 

As the AI arms race escalates between attackers and defenders, this lab provides 23 hands-on scenarios to study:
- **Offensive AI**: How attackers use LLMs for automated pentesting, deepfakes, phishing, and malware creation.
- **Defensive AI**: How defenders utilize AI for anomaly detection, automated SOC analysis, and SOAR.
- **AI/ML Vulnerabilities**: Securing AI systems themselves against Prompt Injection, Model Extraction, and RAG Poisoning.

---

## 🏗️ Lab Infrastructure & Architecture

The lab runs entirely on a **GCP Spot VM** (NVIDIA T4 GPU) in the **same VPC** as the Splunk SIEM, so log forwarding (Wazuh → Splunk HEC) goes directly over the private network — no tunnel needed.

### Overall Architecture

```mermaid
---
config:
  theme: neo-dark
  layout: elk
---
flowchart LR
 subgraph subGraph0["🔵 Blue Net (Defense)"]
        W["Wazuh SIEM"]
        A["AI SOC Analyst Script"]
  end
 subgraph subGraph1["🔴 Red Net (Attack)"]
        K["Kali Linux"]
        C["CALDERA"]
        G["GoPhish"]
  end
 subgraph subGraph2["🎯 Target Net (Vulnerable Apps)"]
        D["DVWA & JuiceShop"]
        L["Vulnerable LLM App"]
        R["Vulnerable RAG App"]
  end
 subgraph subGraph3["🤖 AI Native (GPU Hardware)"]
        O["Ollama Server - T4 GPU"]
  end
 subgraph subGraph4["☁️ GCP Spot VM (Ubuntu + T4 GPU, Docker)"]
        subGraph0
        subGraph1
        subGraph2
        subGraph3
  end
 subgraph subGraph5["☁️ GCP Environment"]
        IAP["GCP IAP (admin SSH + Splunk Web)"]
        S["Splunk Enterprise"]
        AD["Windows AD DC"]
        WC["Windows Client"]
  end
    K -- Attacks --> D & L & R
    A -- Queries --> O
    L -- Uses --> O
    R -- Uses --> O
    W -. Monitors .-> D & L & R
    W == "JSON Alerts (VPC internal :8088)" ==> S
    IAP -. admin access .-> S
    AD == WinEventLog ==> S
    WC == Sysmon ==> S
    C -. Automated APT .-> AD & WC
    G -. Phishing Emails .-> WC
```

### Splunk Logging & Connectivity Architecture

Because the lab VM and Splunk are in the **same VPC**, log forwarding (HEC) goes directly over the private network — no tunnel. GCP IAP is used only for the analyst to reach the lab VM (SSH) and the Splunk Web UI from an external machine.

```mermaid
---
config:
  theme: redux-dark-color
  look: handDrawn
  fontFamily: '''Merriweather Variable'', serif'
---
sequenceDiagram
    participant Docker as Lab VM Docker (Wazuh/Apps)
    participant HEC as Splunk HEC (GCP VM:8088)
    participant Splunk as Splunk Indexer (GCP)
    Note over Docker, Splunk: Log Ingestion Pipeline (VPC internal, no tunnel)
    Docker->>HEC: 1. POST JSON alert to Splunk internal IP:8088 (Wazuh_Token)
    HEC->>Splunk: 2. Authenticate via Token & ingest to index=ai_logs
    participant Analyst as SOC Analyst (work PC)
    participant IAPWeb as GCP IAP Tunnel (Localhost:8000)
    participant Web as Splunk Web (GCP VM:8000)
    Note over Analyst, Web: Analysis Pipeline (IAP from outside)
    Analyst->>IAPWeb: 3. Access Splunk UI (https://localhost:8000)
    IAPWeb->>Web: 4. Securely tunnel UI traffic
    Web->>Analyst: 5. Render Dashboards & SPL Results
```

---

## 🛠️ Technology Stack & Tools Glossary

This lab integrates cutting-edge AI and enterprise-grade security tools:

### 🔴 Offense (Red Team)
- **Kali Linux**: The primary attacker machine equipped with pentesting tools.
- **CALDERA**: MITRE's autonomous adversary-emulation platform — chains ATT&CK techniques (discovery, privilege escalation, lateral movement) with no human input. Drives scenarios 01, 20, and 22.
- **GoPhish**: An open-source phishing framework used to simulate AI-generated social engineering campaigns.

### 🎯 Target (Vulnerable Applications)
- **llm-app**: A vulnerable Python Flask chatbot susceptible to Prompt Injection.
- **rag-app**: A Retrieval-Augmented Generation application vulnerable to Data Poisoning via its file-based knowledge base.
- **agent-app**: An AI agent suffering from Excessive Agency, allowing unauthorized OS command execution.
- **ml-api**: A model endpoint that leaks full-precision confidence scores — the target for Model Extraction (08) and Adversarial ML Evasion (05).
- **DVWA & Juice Shop**: Classic, vulnerability-rich web targets used as a realistic attack surface for the AI pentest agent (21) and for generating training traffic for anomaly detection (23).

### 🛡️ Defense (Blue Team)
- **Wazuh (EDR/SIEM)**: The lab VM's security agent and log aggregator, collecting app logs (via a shared `ai-logs` volume) and forwarding alerts to Splunk over the **VPC-internal network**.
- **AI SOC Analyst Script**: `scripts/ai_soc_triage.py` — feeds Wazuh alerts to the local LLM for True/False-Positive triage and MITRE mapping, then forwards verdicts to Splunk.
- **Sysmon**: Advanced Windows system monitor (deployed on the GCP Windows AD/Client VMs) running [olafhartong/sysmon-modular](https://github.com/olafhartong/sysmon-modular)'s balanced config — an industry-standard, MITRE ATT&CK-tagged ruleset — with an ingest-time filter on Splunk to keep the noisiest event type (ImageLoad) from blowing the 10GB/day license.
- **Splunk Enterprise**: The central SIEM on a GCP VM (same VPC) for advanced SPL threat hunting and log correlation.

### 🤖 AI Backend & Cloud Infrastructure
- **Ollama**: AI inference engine utilizing the lab VM's **NVIDIA T4 GPU (16GB)** to run `llama3.1` and `codellama` entirely offline.
- **GCP Spot VM**: A preemptible n1-standard-8 + T4 instance running the full Docker stack; cheap (60-70% off) and stoppable between sessions.
- **GCP IAP**: Used for admin access only — SSH to the lab VM and reaching Splunk Web — without any public IP. Log forwarding is VPC-internal, not via IAP.
- **Splunk HEC (HTTP Event Collector)**: Ingests structured JSON alerts from Wazuh over the VPC-internal network on port 8088.

---

## 📂 Repository Structure

```text
gcp-cyber-ai-lab/
├── README.md                           # Main dashboard & project overview
├── docs/                               # Scenario guides, setup & syllabus
│   ├── SCENARIOS_GUIDE.md              # Master syllabus, SOP & 23-scenario index
│   ├── setup/                          # 00-13 from-scratch GCP setup (VPC→firewall→NAT→4 VMs→config→ignite→snapshot→cost)
│   └── scenarios/                      # 23 Super Detailed HTB-style Guides
│       ├── 01-AI-Autonomous-Pentesting-Agent.md
│       ├── 02-AI-Powered-Phishing-&-Social-Engineering.md
│       └── ... (23 detailed guides)
│
├── infrastructure/                     # Environment configurations & setup
│   ├── LOCAL_MACHINE_SETUP.md          # GCP lab VM setup (specs, install, networks)
│   ├── SPLUNK_SETUP.md                 # GCP Splunk HEC, indexes & VPC access
│   ├── configs/                        # Wazuh & Sysmon configs
│   ├── kali/                           # Kali attacker image (Dockerfile bakes in nmap/sqlmap/hydra/…)
│   └── docker-compose.yml              # Main docker environment (profiles: defense/targets/offense/ml/all)
│
├── apps/                               # Vulnerable applications source code
│   ├── llm-app/                        # Prompt Injection target (5002)
│   ├── rag-app/                        # RAG Poisoning target (5001)
│   ├── agent-app/                      # Excessive Agency target (5003)
│   ├── ml-api/                         # Model Extraction / Adversarial ML target (5005)
│   └── ml-notebooks/                   # Jupyter notebooks for ML scenarios
│
├── detection-rules/                    # Detection Engineering as Code (DaC)
│   ├── splunk/                         # SPL queries (.spl)
│   ├── wazuh/                          # Custom rules (.xml)
│   └── sigma/                          # Sigma rules (.yml)
│
├── scenarios/                          # Individual scenario workspaces
│   ├── 01-ai-autonomous-pentest/
│   │   ├── README.md                   # Specific Scenario Report Template
│   │   └── evidence/                   # Screenshots & logs
│   ├── 02-ai-phishing/
│   └── ... (23 scenario folders)
│
├── scripts/                            # Blue-team & lab automation
│   ├── start_lab.sh                    # Interactive menu to start lab (bash)
│   ├── verify_health.sh                # Connection health check (bash)
│   ├── recover_vm.sh                   # One-command VM restore from baseline snapshot (bash)
│   ├── ai_soc_triage.py                # AI SOC alert triage (scenario 10)
│   ├── soar_playbook.py                # AI SOAR auto-response (scenario 14)
│   └── nl_to_spl.py                    # Natural-language-to-SPL middleware (scenario 12)
│
└── tools/                              # Red-team offensive automation
    ├── ai_pentest_agent.py             # LLM-driven autonomous pentest (scenarios 01, 21)
    ├── model_extractor.py              # Model extraction attack (scenario 08)
    └── generate_adv_samples.py         # ZOO adversarial evasion (scenario 05)
```

---

## 📋 Scenario Matrix (23 Scenarios)

> **Status Key:** 
> ⚪ PLANNED (Not started)
> 🟢 COMPLETED (Report and evidence uploaded)

| # | Scenario | Type | Framework Focus | Status |
|:---|:---|:---|:---|:---:|
| 01 | AI Autonomous Pentesting Agent | 🔴 Offense | ATT&CK, ATLAS AML.T0016 | ⚪ PLANNED |
| 02 | AI-Powered Phishing | 🔴 Offense | ATT&CK, ATLAS AML.T0048 | ⚪ PLANNED |
| 03 | LLM Prompt Injection & Jailbreak | 🔴 Offense | OWASP LLM01, LLM02, LLM07 | ⚪ PLANNED |
| 04 | RAG Poisoning Attack | 🔴 Offense | OWASP LLM04, LLM08 | ⚪ PLANNED |
| 05 | Adversarial ML Evasion | 🔴 Offense | ATLAS AML.T0015 | ⚪ PLANNED |
| 06 | AI Supply Chain Attack (Malicious Models)| 🔴 Offense | OWASP LLM03, ATLAS AML.T0010 | ⚪ PLANNED |
| 07 | Agentic AI Hijacking | 🔴 Offense | OWASP LLM05, LLM06 | ⚪ PLANNED |
| 08 | Model Extraction & Membership Inference | 🔴 Offense | ATLAS AML.T0024, T0025 | ⚪ PLANNED |
| 09 | AI-Generated Malware Analysis | 🔴 Offense | ATLAS AML.T0017, ATT&CK | ⚪ PLANNED |
| 10 | AI SOC Analyst (Alert Triage) | 🔵 Defense | NIST CSF (DE.AE) | ⚪ PLANNED |
| 11 | AI Anomaly Detection (Isolation Forest) | 🔵 Defense | ATT&CK TA0008, TA0010 | ⚪ PLANNED |
| 12 | AI Threat Hunting via NL Queries | 🔵 Defense | ATT&CK General | ⚪ PLANNED |
| 13 | Deepfake Detection & Defense | 🔵 Defense | ATLAS AML.T0048 | ⚪ PLANNED |
| 14 | AI-Powered Automated SOAR | 🔵 Defense | NIST CSF (RS.RP, RS.MI) | ⚪ PLANNED |
| 15 | DNS Tunneling + AI Detection | 🔵 Defense | ATT&CK T1071.004 | ⚪ PLANNED |
| 16 | Data Poisoning Defense | 🟣 Both | ATLAS AML.T0020, OWASP LLM04 | ⚪ PLANNED |
| 17 | Purple Team AD Attack + AI Detection | 🟣 Both | ATT&CK General (GCP based) | ⚪ PLANNED |
| 18 | MFA Bypass & Credential Attacks + AI | 🟣 Both | ATT&CK T1556, T1110 | ⚪ PLANNED |
| 19 | LLM Misinformation & Hallucination Defense| 🟣 Both | OWASP LLM09 | ⚪ PLANNED |
| 20 | AI vs AI Final Exercise | 🟣 Both | ALL Frameworks | ⚪ PLANNED |
| 21 | AI-Driven Web Pentest (Juice Shop) | 🔴 Offense | ATT&CK T1595/T1190, ATLAS AML.T0016 | ⚪ PLANNED |
| 22 | CALDERA Autonomous Red vs AI Blue | 🟣 Both | ATT&CK (Full Chain) | ⚪ PLANNED |
| 23 | Real-Traffic AI Anomaly Detection Training | 🔵 Defense | ATT&CK TA0008/TA0010, OWASP LLM04 | ⚪ PLANNED |

## ⚠️ Disclaimer

This lab is for **educational purposes only**.  
All credentials shown in setup docs are lab-only and should never be used in production.

---


## 📜 Author

**Jeremy Lim**  
Cybersecurity Enthusiast | SOC Analyst (aspiring)  
[LinkedIn](https://www.linkedin.com/in/jeremy-lzh/) · [GitHub](https://github.com/z1r0h)
