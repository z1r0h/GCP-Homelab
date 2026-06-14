# 04 — Rogue Local User Creation

| Field           | Detail                                                                                      |
| --------------- | ------------------------------------------------------------------------------------------- |
| Status          | ✅ Completed                                                                                 |
| MITRE Technique | [T1136.001 — Create Account: Local Account](https://attack.mitre.org/techniques/T1136/001/) |
| MITRE Tactic    | Persistence                                                                                 |
| Log Source      | Windows Security Event 4720                                                                 |
| Attack file     | [attacks/04-rogue-user.md](../attacks/04-rogue-user/README.md)                              |

---

## SPL Query
Search for Event ID
```SPL
index=* source="XmlWinEventLog:Security" (EventCode=4720 OR EventCode=4732)
```

Create Alert 
```spl
index=* source="XmlWinEventLog:Security" (EventCode=4720 OR EventCode=4732)
| table _time, Computer, EventID , TargetUserName, SubjectUserName
| eval mitre_technique="T1136.001", mitre_tactic="Persistence"
| sort _time
```

---

## Alert Settings

| Field      | Value                                        |
| ---------- | -------------------------------------------- |
| Title      | `New Account Created - T1136`                |
| Alert Type | Scheduled — Cron `*/5 * * * *` (every 5 min) |
| Time range | Last 5 minutes                               |
| Trigger    | Number of Results > 0                        |
| Throttle   | Off                                          |
| Expires    | 24 hours                                     |
| Action     | Add to Triggered Alerts                      |

---

## Notes

- Event 4720 = user account created. Event 4732 = member added to a security group.
- A 4720 immediately followed by 4732 (Administrators) is a strong backdoor indicator.
- Baseline legitimate account creation in your environment to reduce false positives.
