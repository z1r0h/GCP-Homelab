# GCP Homelab

A hands-on home lab hosted on **Google Cloud Platform (GCP)** and local machines, built to develop practical blue-team and detection-engineering skills for a SOC Analyst role.

This repo is an umbrella for several labs. Each lab has its own folder with setup notes, configs, and detection work. It is an active, ongoing project — sections are marked with their current status.

**Status key:** 🟢 Done &nbsp;·&nbsp; 🟡 In progress &nbsp;·&nbsp; ⚪ Planned

---

## Labs in this repo

| Lab | Focus | Status |
|---|---|---|
| [Cloud Security Threat Detection Homelab](./Cloud-security-threat-detection-homelab) | Splunk + Sysmon detection engineering on a GCP VPC | 🟢 Done |
| [AI Security Lab](./AI-Security-Lab) | AI-powered attack & defense: 23 scenarios covering OWASP LLM Top 10, MITRE ATLAS, adversarial ML | 🟡 In progress(Temp Pause for SEC+ exam prep |
> More labs will be added to this repo over time.

---

### AI Security Lab
A fully GCP-hosted lab focusing on the intersection of AI and Cybersecurity. It features 23 hands-on scenarios covering offensive AI, defensive AI, and AI/ML vulnerabilities, running entirely on a single GCP Spot VM in the same VPC as the Splunk SIEM.

### Architecture
Everything runs on one **GCP Spot VM** (NVIDIA T4 GPU, Docker) in the same VPC as Splunk, so log forwarding (Wazuh → Splunk HEC) goes **directly over the private network — no tunnel needed**. GCP IAP is used only for admin access (SSH to the lab VM, Splunk Web UI), never for the telemetry pipeline itself.

| Component | Role |
| :--- | :--- |
| Kali Linux, CALDERA & GoPhish | Offensive toolkit — manual pentesting, autonomous ATT&CK chains, and phishing simulation (Red Net) |
| Vulnerable AI Apps | Custom targets (llm-app, rag-app, agent-app, ml-api) for prompt injection, data poisoning, excessive agency, and model extraction |
| Ollama Server (GCP T4 GPU) | AI backend running Llama 3 / CodeLlama entirely offline, on the lab VM's GPU |
| Wazuh & Sysmon | Endpoint/app log aggregation and detection, forwarding alerts to Splunk over the VPC-internal network |
| Splunk Enterprise (GCP, same VPC) | Cloud SIEM for threat hunting, ingesting logs directly via Splunk HEC — no tunnel |

### What's built 🟡
- 23 distinct hands-on scenarios spanning Offensive AI (autonomous pentesting), Defensive AI (SOC alert triage, SOAR), and AI Vulnerability Exploitation.
- Custom-built vulnerable AI applications (llm-app, rag-app, agent-app, ml-api).
- Secure end-to-end telemetry pipeline routing Wazuh JSON alerts directly into Splunk HEC over the VPC-internal network (no tunnel).
- Splunk Web UI accessible securely via a GCP IAP tunnel (port 8000) without exposing public IPs.
- Lab scenarios mapped against MITRE ATT&CK, MITRE ATLAS, and OWASP LLM Top 10 frameworks.

### Tools & Tech
Ollama (Llama 3 / CodeLlama) · Python · Docker · Wazuh · Sysmon · Splunk Enterprise · GCP IAP · CALDERA · Kali Linux · GoPhish · MITRE ATLAS · OWASP LLM Top 10

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
