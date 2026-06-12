# Detection Rules

All detections are hand-written SPL queries saved as Splunk alerts. Each maps to a MITRE ATT&CK technique.

Because logging is fully configured once in [setup step 06](../docs/setup/06%20%E2%80%94%20Sysmon%2C%20Forwarder%20%26%20Full%20Logging%20Setup.md), every detection below works without per-attack reconfiguration.

---

## How to use

1. Run the attack from the matching `attacks/NN-name/README.md`
2. Open the matching detection file below
3. Paste the SPL into Splunk Search to confirm results (set time range to **Last 15 minutes**)
4. Save As → Alert (settings listed in each file)

---

## ⚠️ Field name troubleshooting

The SPL queries use the field names produced by **Splunk Add-on for Microsoft Windows (742)** + **Add-on for Sysmon (5709)** in XML mode. If a query returns no results even though the events exist, the field name may differ slightly in your TA version. Two things to check:

**1. Confirm the events arrived** — strip the field filters and just look:
```spl
index=wineventlog source="XmlWinEventLog:Security" EventCode=4625
```
Then click a result and expand the fields list to see the actual field names.

**2. Security events have duplicate `Account_Name` fields.** In XML mode, events like 4624/4625 contain two `Account_Name` values (the Subject account and the target account), so Splunk treats it as a multivalue field. If filtering on `Account_Name` behaves oddly, use `mvindex(Account_Name, 1)` to get the second (target) value, or filter on a more specific field like `Source_Network_Address`.

Common field name variants you may see depending on TA version: `Account_Name` / `user`, `Source_Network_Address` / `src_ip` / `Source_Address`, `Logon_Type` / `LogonType`.

---

## Coverage

| # | Detection | Technique | Tactic | Log Source |
|---|---|---|---|---|
| 01 | [Network Port Scan](01-network-port-scan.md) | [T1046](https://attack.mitre.org/techniques/T1046/) | Discovery | Sysmon EID 3 |
| 02 | [RDP Brute Force](02-rdp-brute-force.md) | [T1110.001](https://attack.mitre.org/techniques/T1110/001/) | Credential Access | Security 4625 |
| 03 | [PowerShell Download Cradle](03-powershell-cradle.md) | [T1059.001](https://attack.mitre.org/techniques/T1059/001/) | Execution | PowerShell 4104 |
| 04 | [Rogue Local User Creation](04-rogue-user.md) | [T1136.001](https://attack.mitre.org/techniques/T1136/001/) | Persistence | Security 4720 |
| 05 | [Credential Dumping (Mimikatz)](05-credential-dumping.md) | [T1003.001](https://attack.mitre.org/techniques/T1003/001/) | Credential Access | Sysmon EID 10 |
| 06 | [Pass-the-Hash](06-pass-the-hash.md) | [T1550.002](https://attack.mitre.org/techniques/T1550/002/) | Lateral Movement | Security 4624 LT3 |
| 07 | [Scheduled Task Persistence](07-scheduled-task.md) | [T1053.005](https://attack.mitre.org/techniques/T1053/005/) | Persistence | Security 4698 |
| 08 | [SMB Share Enumeration](08-smb-enumeration.md) | [T1135](https://attack.mitre.org/techniques/T1135/) | Discovery | Security 5140 |
| 09 | [Registry Run Key Persistence](09-registry-run-key.md) | [T1547.001](https://attack.mitre.org/techniques/T1547/001/) | Persistence | Sysmon EID 13 |
| 10 | [Kerberoasting](10-kerberoasting.md) | [T1558.003](https://attack.mitre.org/techniques/T1558/003/) | Credential Access | Security 4769 |
| 11 | [C2 Beacon](11-c2-beacon.md) | [T1071](https://attack.mitre.org/techniques/T1071/) | Command & Control | Sysmon EID 3 + 22 |
| 12 | [DCSync](12-dcsync.md) | [T1003.006](https://attack.mitre.org/techniques/T1003/006/) | Credential Access | Security 4662 |
| 13 | [Golden Ticket](13-golden-ticket.md) | [T1558.001](https://attack.mitre.org/techniques/T1558/001/) | Credential Access | Security 4768/4769 |
| 14 | [Full APT Chain](14-apt-chain.md) | [Multiple](https://attack.mitre.org/matrices/enterprise/) | Multiple | Correlation |

Status legend in each file: 🔜 Pending · ✅ Completed
