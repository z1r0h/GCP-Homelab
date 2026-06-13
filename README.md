# GCP Homelab

A hands-on home lab hosted on **Google Cloud Platform (GCP)**, built to develop practical blue-team and detection-engineering skills for a SOC Analyst role.

This repo is an umbrella for several labs. Each lab has its own folder with setup notes, configs, and detection work. It is an active, ongoing project — sections are marked with their current status.

**Status key:** 🟢 Done &nbsp;·&nbsp; 🟡 In progress &nbsp;·&nbsp; ⚪ Planned

---

## Labs in this repo

| Lab | Focus | Status |
|---|---|---|
| [Cloud Security Threat Detection Homelab](./Cloud-security-threat-detection-homelab) | Splunk + Sysmon detection engineering on a GCP VPC | 🟡 In progress |
| AI Security Lab | LLM-assisted SOC workflows (alert triage, enrichment) | ⚪ Planned |

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

### Current focus 🟡

Detection engineering, working through scenarios one at a time. Currently on:

- **Network Scanning — MITRE ATT&CK [T1046](https://attack.mitre.org/techniques/T1046/)**
  - Running Nmap port/host scans from Kali against the Windows endpoint
  - Writing and tuning the detection SPL in Splunk
  - Investigating Sysmon network-connection logging (Event ID 3) for scan traffic — looking at why SYN scans aren't reliably logged (SYN-scan vs full TCP-connect behaviour) and selecting the right telemetry source for inbound scan detection

### Roadmap ⚪

- [ ] Finish T1046 network-scan detection
- [ ] Brute-force detection (failed/successful logon patterns)
- [ ] Lateral movement detection
- [ ] Map each detection to its MITRE ATT&CK technique
- [ ] Write up notes / lessons learned per scenario

---

## Tools & Tech

GCP · Splunk Enterprise (SPL) · Sysmon · Windows Server / Active Directory · Kali Linux · MITRE ATT&CK · Nmap

---

## About

I'm transitioning into a SOC Analyst / detection-engineering role. Certified in **CEH** and **Splunk SCDA (SPLK-5001)**, and building this lab to get hands-on with the full detection workflow — from generating attacker telemetry to writing and tuning the SPL that catches it.

🔗 LinkedIn: [linkedin.com/in/jeremy-lzh](https://linkedin.com/in/jeremy-lzh)
