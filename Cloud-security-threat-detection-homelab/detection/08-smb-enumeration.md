# 08 — SMB Share Enumeration

| Field           | Detail                                                                        |
| --------------- | ----------------------------------------------------------------------------- |
| Status          | ✅ Completed                                                                   |
| MITRE Technique | [T1135 — Network Share Discovery](https://attack.mitre.org/techniques/T1135/) |
| MITRE Tactic    | Discovery                                                                     |
| Log Source      | Windows Security Event 5140                                                   |
| Attack file     | [attacks/08-smb-enumeration.md](../attacks/08-smb-enumeration/README.md)      |

---

## SPL Query
discovered eventid 5140
```spl
index=* source="XmlWinEventLog:Security" EventCode=5140
```

narrow down searches, lots of shares visit from src_ip 10.0.10.3
```
index=* source="XmlWinEventLog:Security" EventCode=5140 src_ip="10.0.10.3"
| table _time, user, src_ip, comouter, ShareName
```

create alerts
```spl
index=* source="XmlWinEventLog:Security" EventCode=5140 src_ip="10.0.10.3" user !="ANONYMOUS LOGON"
| bucket _time span=1m
| stats dc(ShareName) as share_touched by _time, src_ip, user
| where share_touched > 3
| eval mitre_technique="T1135", mitre_tactic="Discovery"
```

---

## Alert Settings

| Field      | Value                                        |
| ---------- | -------------------------------------------- |
| Title      | `SMB Share Enumeration - T1135`              |
| Alert Type | Scheduled — Cron `*/5 * * * *` (every 5 min) |
| Time range | Last 5 minutes                               |
| Trigger    | Number of Results > 0                        |
| Throttle   | Off                                          |
| Expires    | 24 hours                                     |
| Action     | Add to Triggered Alerts                      |

---

## Notes

- Event 5140 = a network share was accessed. Requires 'Audit File Share' (enabled in setup 06).
- One source touching many shares quickly indicates enumeration.
- IPC$ and ADMIN$ access from an unknown host is a common recon signal.
- Multiple access in very short period indicate a malicious activity.
