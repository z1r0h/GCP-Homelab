# 05 — Credential Dumping (Mimikatz)

| Field           | Detail                                                                                            |
| --------------- | ------------------------------------------------------------------------------------------------- |
| Status          | ✅ Completed                                                                                       |
| MITRE Technique | [T1003.001 — OS Credential Dumping: LSASS Memory](https://attack.mitre.org/techniques/T1003/001/) |
| MITRE Tactic    | Credential Access                                                                                 |
| Log Source      | Sysmon Event 10 (ProcessAccess)                                                                   |
| Attack file     | [attacks/05-credential-dumping.md](../attacks/05-credential-dumping/README.md)                    |

---

## SPL Query
discovered mimikatz targeting lsass
```spl
index=* EventCode=10 host="win-client" TargetImage="C:\\Windows\\system32\\lsass.exe"
```

narrow down searches but alots of noise.
```spl
index=* source="XmlWinEventLog:Microsoft-Windows-Sysmon/Operational" EventCode=10 TargetImage="*lsass.exe"
| search GrantedAccess IN ("0x1010","0x1410","0x143a","0x1438","0x1f0fff")
| table _time, Computer, SourceImage, TargetImage, GrantedAccess
| eval mitre_technique="T1003.001", mitre_tactic="Credential Access"
```

continue tuning and create alert that exclude legitimate Source Image!="*google-cloud-metrics-agent_windows_amd64.exe" 
```spl
index=* source="XmlWinEventLog:Microsoft-Windows-Sysmon/Operational" EventCode=10 TargetImage="*lsass.exe" SourceImage!="*google-cloud-metrics-agent_windows_amd64.exe"
| search GrantedAccess IN ("0x1010","0x1410","0x143a","0x1438","0x1f0fff")
| table _time, Computer, SourceImage, TargetImage, GrantedAccess
| eval mitre_technique="T1003.001", mitre_tactic="Credential Access"
```


---

## Alert Settings

| Field      | Value                                              |
| ---------- | -------------------------------------------------- |
| Title      | `LSASS Memory Access (Credential Dumping) - T1003` |
| Alert Type | Scheduled — Cron `*/5 * * * *` (every 5 min)       |
| Time range | Last 5 minutes                                     |
| Trigger    | Number of Results > 0                              |
| Throttle   | Off                                                |
| Expires    | 24 hours                                           |
| Action     | Add to Triggered Alerts                            |

---

## Notes

- Event 10 = one process opening a handle to another. Filter TargetImage=lsass.exe.
- GrantedAccess values 0x1010 / 0x1410 / 0x143a are typical of credential dumping tools.
- Legitimate AV/EDR also access lsass — exclude known SourceImage paths to cut noise.
- `CallTrace` reveals the calling module even if the tool is renamed — look for ntdll.dll/KERNELBASE.dll patterns from a non-system path.
