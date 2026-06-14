# 02 — RDP Brute Force

| Field | Detail |
|---|---|
| Status | ✅ Completed |
| MITRE Technique | [T1110.001 — Brute Force: Password Guessing](https://attack.mitre.org/techniques/T1110/001/) |
| MITRE Tactic | Credential Access |
| Log Source | Windows Security Event 4625 |
| Attack file | [attacks/02-rdp-brute-force.md](../attacks/02-rdp-brute-force/README.md) |

---

## SPL Query
Check for failed Login
```spl
index=* EventCode=4625 source="XmlWinEventLog:Security" src_ip="10.0.10.3"
| bucket _time span=1m
| stats count as failed_logons by _time, src_ip
| where failed_logons > 3
| eval mitre_technique="T1110.001", mitre_tactic="Credential Access"
```

Check for successful login
```spl
index=* EventCode=4624 source="XmlWinEventLog:Security" src_ip="10.0.10.3"
|bucket _time span=10m
| stats count as successful_login by _time, src_ip
| sort _time
```

Create Detection Alert
```spl
index=* EventCode=4625 source="XmlWinEventLog:Security"
| bucket _time span=1m
| stats count as failed_logons by _time, src_ip
| where failed_logons > 3
| eval mitre_technique="T1110.001", mitre_tactic="Credential Access"
```

---

## Alert Settings

| Field      | Value                                        |
| ---------- | -------------------------------------------- |
| Title      | `RDP Brute Force - T1110.001`                |
| Alert Type | Scheduled — Cron `*/5 * * * *` (every 5 min) |
| Time range | Last 5 minutes                               |
| Trigger    | Number of Results > 0                        |
| Throttle   | Off                                          |
| Expires    | 24 hours                                     |
| Action     | Add to Triggered Alerts                      |


---

## Notes

- Event 4625 = failed logon. Logon Type 10 = RDP, Type 3 = network.
- Threshold >3 failed logons per minute from one source IP indicates brute force.
- A successful 4624 right after many 4625s from the same IP = successful compromise — worth a separate correlation alert.
