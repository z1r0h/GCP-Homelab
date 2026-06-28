# GCP Homelab

A hands-on home lab hosted on **Google Cloud Platform (GCP)** and local machines, built to develop practical blue-team and detection-engineering skills for a SOC Analyst role.

This repo is an umbrella for several labs. Each lab has its own folder with setup notes, configs, and detection work. It is an active, ongoing project — sections are marked with their current status.

**Status key:** 🟢 Done &nbsp;·&nbsp; 🟡 In progress &nbsp;·&nbsp; ⚪ Planned

---

## Labs in this repo

| Lab | Focus | Status |
|---|---|---|
| [Cloud Security Threat Detection Homelab](./Cloud-security-threat-detection-homelab) | Splunk + Sysmon detection engineering on a GCP VPC | 🟢 Done |
| [AI Security Lab](./AI-Security-Lab) | AI-powered attack & defense: 20 scenarios covering OWASP LLM Top 10, MITRE ATLAS, adversarial ML | 🟡 In progress |
> More labs will be added to this repo over time.

---

### AI Security Lab
A comprehensive hybrid lab focusing on the intersection of AI and Cybersecurity. It features 20 hands-on scenarios covering offensive AI, defensive AI, and AI/ML vulnerabilities, bridging local GPU-accelerated workloads with cloud-based SIEM analysis.
Architecture
A hybrid environment prioritizing local execution for heavy AI inference tasks (GPU utilization) while securely routing telemetry to the GCP Cloud SIEM via IAP Tunnels:

| Component | Role |
| :--- | :--- |
| Kali Linux & GoPhish | Offensive toolkit for AI-powered attacks and social engineering (Red Net) |
| Vulnerable AI Apps | Custom targets (llm-app, rag-app, agent-app) built to practice prompt injection, data poisoning, and more |
| Ollama Server (RTX 5060) | Local AI backend running Llama 3 models entirely offline |
| Wazuh & Sysmon | Local defense layer for EDR, endpoint monitoring, and log aggregation |
| Splunk Enterprise (GCP) | Cloud SIEM for threat hunting, securely ingesting logs via GCP IAP & Splunk HEC |

### What's built 🟡
- 20 distinct hands-on scenarios spanning Offensive AI (autonomous pentesting), Defensive AI (SOC alert triage, SOAR), and AI Vulnerability Exploitation.
- Custom-built vulnerable AI applications (llm-app, rag-app, agent-app).
- Secure end-to-end telemetry pipeline routing Wazuh JSON alerts over GCP IAP Tunnels (port 8088) directly into Splunk HEC.
- Splunk Web UI accessible securely via IAP Tunnels (port 8000) without exposing public IPs.
- Lab scenarios mapped against MITRE ATT&CK, MITRE ATLAS, and OWASP LLM Top 10 frameworks.
Tools & Tech
Ollama (Llama 3 / CodeLlama) · Python · Docker · Wazuh · Sysmon · Splunk Enterprise · GCP IAP Tunnels · Kali Linux · GoPhish · MITRE ATLAS · OWASP LLM Top 10

---

## Cloud Security Threat Detection Homelab

A small enterprise-style environment on GCP for simulating attacks and building the matching detections in Splunk.

### Architecture

A 4-VM private VPC (no public IPs — access via IAP tunnelling):

| VM | Role |
|---|---|
| Windows Server | Active Directory Domain Controller |
| Windows client | Domain-joined endpoint (telemetry source) |
| Splunk Enterprise | SIEM |
| Kali Linux | Attacker box |

**Telemetry pipeline:** Sysmon (**sysmon-modular** config) → Splunk Universal Forwarder → Splunk Enterprise

### What's built 🟢

- 4-VM private VPC on GCP, with custom Kali image imported
- IAP tunnelling and VPC firewall rules for secure access (no public exposure)
- Splunk Enterprise set up as the SIEM
- Sysmon telemetry flowing end-to-end into Splunk

## Tools & Tech

GCP · Splunk Enterprise (SPL) · Sysmon · Windows Server / Active Directory · Kali Linux · MITRE ATT&CK · Nmap

---

## About

I'm transitioning into a SOC Analyst / detection-engineering role. Certified in **CEH** and **Splunk SCDA (SPLK-5001)**, and building this lab to get hands-on with the full detection workflow — from generating attacker telemetry to writing and tuning the SPL that catches it.

🔗 LinkedIn: [linkedin.com/in/jeremy-lzh](https://linkedin.com/in/jeremy-lzh)
