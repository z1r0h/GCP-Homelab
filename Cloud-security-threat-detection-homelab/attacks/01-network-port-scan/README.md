# 01 — Network Port Scan

## Overview

| Field | Detail |
|---|---|
| Status | 🔜 Pending |
| Date | — |
| Tier | Beginner |
| Attacker | kali-linux-attacker-vm (10.0.10.3) |
| Target | win-dc (10.0.10.10) |
| MITRE Tactic | Discovery (TA0007) |
| MITRE Technique | [T1046 — Network Service Discovery](https://attack.mitre.org/techniques/T1046/) |
| Tool | nmap |
| Log Source | Sysmon Event 3 (Network Connection) |
| Detection | [detection/01-network-port-scan.md](../../detection/01-network-port-scan.md) |

---

## Attack Steps

```bash
# TCP connect scan (-sT) — completes the handshake so Sysmon Event 3 fires
nmap -sT 10.0.10.10

# Service version detection (more events)
nmap -sT -sV 10.0.10.10
```

> Use `-sT` not the default `-sS`. SYN scans don't complete the TCP handshake, so Sysmon Event 3 won't record them. With the sysmon-modular config from setup 06, all open-port connections are logged.

---

## Detection (summary)

Full SPL and alert settings: [detection/01-network-port-scan.md](../../detection/01-network-port-scan.md).

After `nmap -sT 10.0.10.10` you should see connections to many ports (53, 88, 135, 389, 445, 3389...) from 10.0.10.3.

---

## Findings

> *(Fill in after completing)*

| Field | Result |
|---|---|
| Date | — |
| Command used | — |
| Unique ports detected | — |
| Alert triggered | — |
| Time from scan to alert | — |

---

## Screenshots

- `screenshots/01-nmap-output.png`
- `screenshots/02-splunk-eventcode3.png`
- `screenshots/03-alert-triggered.png`
- `screenshots/04-mitre-matrix.png`
