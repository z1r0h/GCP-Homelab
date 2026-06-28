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
