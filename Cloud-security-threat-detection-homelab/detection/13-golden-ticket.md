# 13 — Golden Ticket

| Field           | Detail                                                                                                       |
| --------------- | ------------------------------------------------------------------------------------------------------------ |
| Status          | ✅ Completed                                                                                                  |
| MITRE Technique | [T1558.001 — Steal or Forge Kerberos Tickets: Golden Ticket](https://attack.mitre.org/techniques/T1558/001/) |
| MITRE Tactic    | Credential Access                                                                                            |
| Log Source      | Windows Security Event 4768 / 4769                                                                           |
| Attack file     | [attacks/13-golden-ticket.md](../attacks/13-golden-ticket/README.md)                                         |

---

## SPL Query

Golden Ticket has no single clean signal (see Notes). The best lab approach is to look for the structural anomaly: a service-ticket request (4769) with no preceding TGT request (4768) for the same account.

```spl
index=* source="XmlWinEventLog:Security" (EventCode=4768 OR EventCode=4769)
| stats values(EventCode) as events by TargetUserName
| where NOT (events="4768") AND events="4769"
| eval mitre_technique="T1558.001", mitre_tactic="Credential Access"
```

---

## Alert Settings

| Field      | Value                                                  |
| ---------- | ------------------------------------------------------ |
| Title      | `Possible Golden Ticket - TGS without TGT - T1558.001` |
| Alert Type | Scheduled — Cron `*/5 * * * *` (every 5 min)           |
| Time range | Last 5 minutes                                         |
| Trigger    | Number of Results > 0                                  |
| Throttle   | Off                                                    |
| Expires    | 24 hours                                               |
| Action     | Add to Triggered Alerts                                |

---

## How Golden Ticket works

DCSync (scenario 12) provided the `krbtgt` hash. Because `krbtgt` signs every TGT in the domain, owning its hash means you can **forge a TGT for any identity, with any privileges** — including users that don't exist.

The attack (run with mimikatz):
```
kerberos::golden /user:FakeAdmin2 /domain:200teamok.local /sid:<DOMAIN_SID> /krbtgt:<KRBTGT_HASH> /ptt
```
`/ptt` injects the forged ticket into the current session. After that, `dir \\win-dc\c$` succeeded — a non-existent user read the Domain Controller's C: drive. That is full, persistent domain control.

## Why it's hard to detect (honest limitation)

Unlike earlier scenarios, Golden Ticket has **no clean indicator**:

- **It's "legitimately" signed.** The forged TGT is signed with the real krbtgt key, so the DC accepts it as valid. In the lab's 4769 events, the activity showed up under normal-looking accounts (`WIN-DC$`, `Administrator`) — the forged `FakeAdmin2` name did not appear, because the ticket impersonates at the Kerberos layer.
- **No 4768.** A normal logon does 4768 (TGT request) then 4769 (service ticket). A Golden Ticket forges the TGT offline, so 4769 can appear with no matching 4768. The query above keys on this — but machine accounts (like `WIN-DC$`) legitimately produce unusual Kerberos patterns, so this filter has false positives and needs a clean baseline to be reliable.

### Better detection signals (production)

- **Abnormal ticket lifetime:** mimikatz defaults to a 10-year ticket lifetime; real TGTs last ~10 hours. A TGT lifetime far beyond domain policy is a strong signal.
- **Anomalous encryption / RC4 where AES is expected**, or tickets missing expected PAC fields.
- **Accounts that don't exist in AD** appearing in authentication logs.
- **4769 without 4768 correlation** at scale, baselined against normal machine-account behaviour.
- The only true remediation is resetting the `krbtgt` password **twice** — so detection focuses on the lateral movement and actions that follow ticket use, not just the forging.

## The takeaway

Golden Ticket is the end-goal of many AD attacks: total, persistent control. The honest lesson here is that **not every attack has a clean detection** — some are caught by their downstream effects (unusual access, abnormal ticket properties) rather than a single event. Recognising the limits of your telemetry is itself a core SOC skill, and worth stating plainly rather than pretending the detection is airtight.
