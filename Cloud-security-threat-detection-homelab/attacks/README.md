# 🎯 Attack Scenarios Overview

14 attack simulations from beginner to advanced. Each runs from `kali-linux-attacker-vm` (10.0.10.3) against the AD environment, with a matching Splunk detection mapped to MITRE ATT&CK.

All scenarios run against the baseline configured in [setup 06](../docs/setup/06%20%E2%80%94%20Sysmon%2C%20Forwarder%20%26%20Full%20Logging%20Setup.md) — no per-attack reconfiguration needed.

---

## 🟢 Beginner

| # | Scenario | MITRE | Tactic | Tool | Log Source | Target | Restore After |
|---|---|---|---|---|---|---|---|
| 01 | [Network Port Scan](01-network-port-scan/README.md) | T1046 | Discovery | nmap | Sysmon EID 3 | win-dc | No |
| 02 | [RDP Brute Force](02-rdp-brute-force/README.md) | T1110.001 | Credential Access | hydra | Security 4625 | win-dc | No |
| 03 | [PowerShell Download Cradle](03-powershell-cradle/README.md) | T1059.001 | Execution | PowerShell IEX | PowerShell 4104 | win-client | No |
| 04 | [Rogue Local User Creation](04-rogue-user/README.md) | T1136.001 | Persistence | net user | Security 4720 | win-client | Yes |

## 🟡 Intermediate

| # | Scenario | MITRE | Tactic | Tool | Log Source | Target | Restore After |
|---|---|---|---|---|---|---|---|
| 05 | [Credential Dumping (Mimikatz)](05-credential-dumping/README.md) | T1003.001 | Credential Access | mimikatz | Sysmon EID 10 | win-client | Yes |
| 06 | [Pass-the-Hash](06-pass-the-hash/README.md) | T1550.002 | Lateral Movement | crackmapexec | Security 4624 (LT3) | win-client | Yes |
| 07 | [Scheduled Task Persistence](07-scheduled-task/README.md) | T1053.005 | Persistence | schtasks | Security 4698 | win-client | Yes |
| 08 | [SMB Share Enumeration](08-smb-enumeration/README.md) | T1135 | Discovery | enum4linux | Security 5140 | win-dc | No |
| 09 | [Registry Run Key Persistence](09-registry-run-key/README.md) | T1547.001 | Persistence | reg add | Sysmon EID 13 | win-client | Yes |
| 10 | [Kerberoasting](10-kerberoasting/README.md) | T1558.003 | Credential Access | impacket GetUserSPNs | Security 4769 | win-dc | No |

## 🔴 Advanced

| # | Scenario | MITRE | Tactic | Tool | Log Source | Target | Restore After |
|---|---|---|---|---|---|---|---|
| 11 | [C2 Beacon Simulation](11-c2-beacon/README.md) | T1071 | Command & Control | metasploit | Sysmon EID 3 + 22 | win-client | Yes |
| 12 | [DCSync Attack](12-dcsync/README.md) | T1003.006 | Credential Access | impacket secretsdump | Security 4662 | win-dc | Yes |
| 13 | [Golden Ticket](13-golden-ticket/README.md) | T1558.001 | Credential Access | mimikatz | Security 4768/4769 | win-dc | Yes |
| 14 | [Full APT Attack Chain](14-apt-chain/README.md) | Multiple | Multiple | All of the above | Correlation | Full env | Yes |

---

## Recommended Order

1. **Start with 01–04** — quick wins, build confidence, easy to verify
2. **02 + 05 are interview favourites** — brute force and credential dumping come up constantly
3. **10 (Kerberoasting) + 12 (DCSync)** — the AD attack highlights, do these once comfortable
4. **14 (APT Chain)** — capstone, chains everything into one incident report

---

## Standard Workflow per Scenario

```
1. Open IAP tunnels (Kali SSH + Splunk Web)
2. Run attack from attacks/NN-name/README.md
3. Confirm events in Splunk (search from detection/NN-name.md)
4. Save As → Alert (settings in detection file)
5. Trigger again → check Activity → Triggered Alerts
6. Screenshot: attack, events, alert
7. Fill in Findings table + flip status 🔜 → ✅ Completed
8. If "Restore After" = Yes:  ./scripts/recovery/restore.sh win-client
```

---

## MITRE ATT&CK Coverage

| Tactic | Techniques Covered |
|---|---|
| Discovery | T1046, T1135 |
| Credential Access | T1110.001, T1003.001, T1558.003, T1003.006, T1558.001 |
| Execution | T1059.001 |
| Persistence | T1136.001, T1053.005, T1547.001 |
| Lateral Movement | T1550.002 |
| Command & Control | T1071 |

6 tactics · 13 unique techniques · 14 scenarios
