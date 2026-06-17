# 07 — Persistence via Scheduled Task

| Field           | Detail                                                                                           |
| --------------- | ------------------------------------------------------------------------------------------------ |
| Status          | ✅ Completed                                                                                      |
| MITRE Technique | [T1053.005 — Scheduled Task/Job: Scheduled Task](https://attack.mitre.org/techniques/T1053/005/) |
| MITRE Tactic    | Persistence                                                                                      |
| Log Source      | Windows Security Event 4698                                                                      |
| Attack file     | [attacks/07-scheduled-task.md](https://claude.ai/attacks/07-scheduled-task/README.md)            |

---

## SPL Query
check for event id 1698 for schedule task created
```spl
index=wineventlog source="XmlWinEventLog:Security" EventCode=4698
```

discovered, proceed to create alert rules
```spl
index=wineventlog source="XmlWinEventLog:Security" EventCode=4698
| table _time, Computer, Task_Name, user_name, Command
| eval mitre_technique="T1053.005", mitre_tactic="Persistence"
```

---

## Alert Settings

| Field      | Value                                        |
| ---------- | -------------------------------------------- |
| Title      | `Scheduled Task Created - T1053`             |
| Alert Type | Scheduled — Cron `*/5 * * * *` (every 5 min) |
| Time range | Last 5 minutes                               |
| Trigger    | Number of Results > 0                        |
| Throttle   | Off                                          |
| Expires    | 24 hours                                     |
| Action     | Add to Triggered Alerts                      |

---

## Notes

- Event 4698 = scheduled task created. The event's `TaskContent` field holds the full task XML, including the command to run, the run-as user, and the schedule interval — read it to see exactly what the attacker scheduled.
- Tasks running as **SYSTEM**, or pointing at scripts/temp paths, are high-risk. Microsoft notes that tasks created manually or by malware usually sit in the Task Scheduler Library root (`\TaskName`).
- Sysmon Event 1 (process create) for `schtasks.exe` is a useful secondary signal.

### Setup gotcha — why 4698 may not appear

Event 4698 needs the **Other Object Access Events** subcategory enabled. But enabling it with `auditpol` is not enough on its own — Windows ignores subcategory settings unless the legacy-override registry value is set first:

```powershell
# 1. Force subcategory settings to take precedence (one-time)
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Lsa" /v SCENoApplyLegacyAuditPolicy /t REG_DWORD /d 1 /f

# 2. Enable the subcategory
auditpol /set /subcategory:"Other Object Access Events" /success:enable /failure:enable

# 3. Apply
gpupdate /force
```

Without step 1, `auditpol /get` will show the subcategory as enabled but no 4698 events are ever written. After enabling, recreate the task — events generated before the policy took effect are not captured retroactively. This is now part of [setup 06](https://claude.ai/docs/setup/06%20%E2%80%94%20Sysmon%2C%20Forwarder%20%26%20Full%20Logging%20Setup.md).