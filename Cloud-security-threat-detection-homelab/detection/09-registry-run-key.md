# 09 — Persistence via Registry Run Key

| Field           | Detail                                                                                                   |
| --------------- | -------------------------------------------------------------------------------------------------------- |
| Status          | ✅ Completed                                                                                              |
| MITRE Technique | [T1547.001 — Boot or Logon Autostart: Registry Run Keys](https://attack.mitre.org/techniques/T1547/001/) |
| MITRE Tactic    | Persistence                                                                                              |
| Log Source      | Sysmon Event 13 (Registry Value Set)                                                                     |
| Attack file     | [attacks/09-registry-run-key.md](../attacks/09-registry-run-key/README.md)                               |

---

## SPL Query

```spl
index=wineventlog source="XmlWinEventLog:Microsoft-Windows-Sysmon/Operational" EventCode=13
| search TargetObject="*\\CurrentVersion\\Run*"
| table _time, Computer, Image, TargetObject, Details
| eval mitre_technique="T1547.001", mitre_tactic="Persistence"
```

---

## Alert Settings

| Field      | Value                                        |
| ---------- | -------------------------------------------- |
| Title      | `Registry Run Key Persistence - T1547.001`   |
| Alert Type | Scheduled — Cron `*/5 * * * *` (every 5 min) |
| Time range | Last 5 minutes                               |
| Trigger    | Number of Results > 0                        |
| Throttle   | Off                                          |
| Expires    | 24 hours                                     |
| Action     | Add to Triggered Alerts                      |

---

## Notes

- Event 13 = registry value set. sysmon-modular already monitors Run keys.
- Run / RunOnce keys under HKCU and HKLM are classic autostart persistence.
- Check the Details field for the executable path — temp/user paths are suspicious.
- SPL Search for TargetObject="*\\CurrentVersion\\Run*"
- check image, which process modify it. modification by `powershell.exe` and `reg.exe` more suspicious than normal app installation