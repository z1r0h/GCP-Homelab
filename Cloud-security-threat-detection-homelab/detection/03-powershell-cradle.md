# 03 — PowerShell Download Cradle

| Field           | Detail                                                                                                      |
| --------------- | ----------------------------------------------------------------------------------------------------------- |
| Status          | ✅ Completed                                                                                                 |
| MITRE Technique | [T1059.001 — Command and Scripting Interpreter: PowerShell](https://attack.mitre.org/techniques/T1059/001/) |
| MITRE Tactic    | Execution                                                                                                   |
| Log Source      | PowerShell Event 4104 (Script Block Logging)                                                                |
| Attack file     | [attacks/03-powershell-cradle.md](../attacks/03-powershell-cradle/README.md)                                |

---

## SPL Query

First Query
```spl
index=* host="win-client" EventID=4104
```
Looking for any powershell execution that logged by **PowerShell Script Block Logging**. Which is EventID = 4104

Narrow down the searches and create an alert for this senarios.
```spl
index=wineventlog source="XmlWinEventLog:Microsoft-Windows-PowerShell/Operational" EventCode=4104
| search ScriptBlockText="*DownloadString*" OR ScriptBlockText="*IEX*" OR ScriptBlockText="*Invoke-Expression*" OR ScriptBlockText="*Net.WebClient*"
| table _time, Computer, User, ScriptBlockText
| eval mitre_technique="T1059.001", mitre_tactic="Execution"
```

---

## Alert Settings

| Field      | Value                                        |
| ---------- | -------------------------------------------- |
| Title      | `PowerShell Download Cradle - T1059.001`     |
| Alert Type | Scheduled — Cron `*/5 * * * *` (every 5 min) |
| Time range | Last 5 minutes                               |
| Trigger    | Number of Results > 0                        |
| Throttle   | Off                                          |
| Expires    | 24 hours                                     |
| Action     | Add to Triggered Alerts                      |

---

## Notes

- Requires PowerShell Script Block Logging (enabled in setup 06). Its very important for SOC to know this logging.
- Event 4104 captures the actual PowerShell code executed, even if obfuscated/encoded.
- Common malicious patterns: IEX, DownloadString, Net.WebClient, FromBase64String, -enc.
