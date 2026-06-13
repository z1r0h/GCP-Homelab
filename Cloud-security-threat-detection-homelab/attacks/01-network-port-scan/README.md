# 01 — Network Port Scan

## Overview

| Field           | Detail                                                                          |
| --------------- | ------------------------------------------------------------------------------- |
| Status          | ✅ Completed                                                                     |
| Date            | 13 June 2026                                                                    |
| Tier            | Beginner                                                                        |
| Attacker        | kali-linux-attacker-vm (10.0.10.3)                                              |
| Target          | win-dc (10.0.10.10)                                                             |
| MITRE Tactic    | Discovery (TA0007)                                                              |
| MITRE Technique | [T1046 — Network Service Discovery](https://attack.mitre.org/techniques/T1046/) |
| Tool            | nmap                                                                            |
| Log Source      | Sysmon Event 3 (Network Connection)                                             |
| Detection       | [detection/01-network-port-scan.md](../../detection/01-network-port-scan.md)    |

---

## Attack Steps

```bash
# TCP connect scan (-sT) — completes the handshake so Sysmon Event 3 fires
nmap -sT 10.0.10.10

# Service version detection (more events)
nmap -sT -sV 10.0.10.10
```

---

## Detection (summary)

Full SPL and alert settings: [detection/01-network-port-scan.md](../../detection/01-network-port-scan.md).


---

## Findings

| Field                   | Result              |
| ----------------------- | ------------------- |
| Date                    | 13 June 2026        |
| Command used            | nmap -sV 10.0.10.10 |
| Unique ports detected   | 3                   |
| Alert triggered         | Yes                 |
| Time from scan to alert | 5 Minuts            |

---

## Screenshots

- (screenshots/01-nmap-output.png)
- screenshots/02-splunk-eventcode3.png
- screenshots/03-alert-triggered.png
