# 06 — Pass-the-Hash Lateral Movement

| Field           | Detail                                                                                                             |
| --------------- | ------------------------------------------------------------------------------------------------------------------ |
| Status          | ✅ Completed                                                                                                        |
| MITRE Technique | [T1550.002 — Use Alternate Authentication Material: Pass the Hash](https://attack.mitre.org/techniques/T1550/002/) |
| MITRE Tactic    | Lateral Movement                                                                                                   |
| Log Source      | Windows Security Event 4624 (Logon Type 3)                                                                         |
| Attack file     | [attacks/06-pass-the-hash.md](../attacks/06-pass-the-hash/README.md)                                               |

---

## SPL Query
look for eventcode 4624/4625 and authname = NTLM because normal login wont use NTLM
```spl
index=* source="XmlWinEventLog:Security" (EventCode=4624 OR EventCode=4625) AuthenticationPackageName=NTLM
```

narrow down searches and list table, found that authentic login from google server
```spl
index=* source="XmlWinEventLog:Security" (EventCode=4624 OR EventCode=4625) Logon_Type=3 AuthenticationPackageName=NTLM src_ip!="35.235.243.162"
| search Target_User_Name!="ANONYMOUS LOGON" Target_User_Name!="*$"
| table _time, Computer, EventCode, Target_User_Name, src_ip, AuthenticationPackageName, Logon_Type
| eval mitre_technique="T1550.002", mitre_tactic="Lateral Movement"
| sort -_time
```

add filter to exclude known IP address and create alert
```spl
index=* source="XmlWinEventLog:Security" (EventCode=4624 OR EventCode=4625) Logon_Type=3 AuthenticationPackageName=NTLM src_ip!="35.235.243.162"
| search Target_User_Name!="ANONYMOUS LOGON" Target_User_Name!="*$"
| table _time, Computer, EventCode, Target_User_Name, src_ip, AuthenticationPackageName, Logon_Type
| eval mitre_technique="T1550.002", mitre_tactic="Lateral Movement"
| sort -_time
```

---

## Alert Settings

| Field      | Value                                        |
| ---------- | -------------------------------------------- |
| Title      | `Pass-the-Hash NTLM Logon - T1550`           |
| Alert Type | Scheduled — Cron `*/5 * * * *` (every 5 min) |
| Time range | Last 5 minutes                               |
| Trigger    | Number of Results > 0                        |
| Throttle   | Off                                          |
| Expires    | 24 hours                                     |
| Action     | Add to Triggered Alerts                      |

---

## Notes

- Event 4624 Logon Type 3 = network logon. NTLM auth package + admin account from an unusual host is suspicious.
- In an AD environment, Kerberos is normal; NTLM network logons to workstations can indicate PtH.
- Correlate with the source host — lateral movement shows one host authenticating to many.
- Administrator NTLM Hash was found during hash dumping in win-client, because administrator account was used to login to win-client, so lsass cached the password. never login to workstastion with admin account.
