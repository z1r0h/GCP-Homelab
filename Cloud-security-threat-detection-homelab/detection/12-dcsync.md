# 12 — DCSync Attack

| Field           | Detail                                                                                      |
| --------------- | ------------------------------------------------------------------------------------------- |
| Status          | ✅ Completed                                                                                 |
| MITRE Technique | [T1003.006 — OS Credential Dumping: DCSync](https://attack.mitre.org/techniques/T1003/006/) |
| MITRE Tactic    | Credential Access                                                                           |
| Log Source      | Windows Security Event 4662                                                                 |
| Attack file     | [attacks/12-dcsync.md](../attacks/12-dcsync/README.md)                                      |

---

## SPL Query

```spl
index=* source="XmlWinEventLog:Security" EventCode=4662
| search Properties="*1131f6aa*"
| search src_user!="*$"
| table _time, Computer, src_user, Properties
| eval mitre_technique="T1003.006", mitre_tactic="Credential Access"
| sort -_time
```

> Field name in this lab is `src_user` (other TA versions may use `Account_Name`/`SubjectUserName`). Confirm with `| table *` on a sample event.

---

## Alert Settings

| Field      | Value                                                        |
| ---------- | ------------------------------------------------------------ |
| Title      | `DCSync - Directory Replication by User Account - T1003.006` |
| Alert Type | Scheduled — Cron `*/5 * * * *` (every 5 min)                 |
| Time range | Last 5 minutes                                               |
| Trigger    | Number of Results > 0                                        |
| Throttle   | Off                                                          |
| Expires    | 24 hours                                                     |
| Action     | Add to Triggered Alerts                                      |

---

## How this detection works (line by line)

**Line 1 — find the event type**
```
EventCode=4662
```
DCSync abuses Active Directory's domain replication. Windows logs access to directory-service objects as **Event 4662**. Requesting password hashes via replication generates a 4662 on the DC.

**Line 2 — filter to the replication permission (the core of the detection)**
```
Properties="*1131f6aa*"
```
4662 is extremely noisy — AD generates huge volumes of it normally. The signal is the **GUID in the `Properties` field**, which identifies the exact operation:

| GUID | Right | Meaning |
|---|---|---|
| `1131f6aa-9c07-11d1-f79f-00c04fc2dcd2` | DS-Replication-Get-Changes | request directory changes (replication) |
| `1131f6ad-...` | DS-Replication-Get-Changes-All | request all changes, including passwords |

Only a real DC should ever request replication, so this GUID appearing is normal **between DCs** — but suspicious if triggered by a regular account.

**Line 3 — exclude legitimate DCs (the decisive filter)**
```
src_user!="*$"
```
This is what separates attack from normal traffic:

| src_user | Meaning |
|---|---|
| `WIN-DC$` (ends in `$`) | a machine account — normal DC-to-DC replication → ignore |
| `Administrator` (a user) | a user account requesting replication → **DCSync attack** |

Excluding `*$` removes legitimate DC replication and leaves only user accounts impersonating a DC to steal hashes.

**Line 4 — newest first**
```
sort -_time
```

---

## What was observed in the lab

The raw 4662 events showed the contrast clearly:

```
src_user: WIN-DC$        → machine account, normal replication
src_user: Administrator  → user account, DCSync attack (many events)
```

Both carried the replication GUID `1131f6aa-9c07-11d1-f79f-00c04fc2dcd2`. The only thing distinguishing attack from normal was **who** triggered it — exactly what the `src_user!="*$"` filter keys on.

---

## Why DCSync matters

- One DCSync dumps **every account hash in the domain**, including Domain Admins and `krbtgt` — remotely, with one command, without touching LSASS on each host.
- The `krbtgt` hash is the key ingredient for the next scenario (Golden Ticket, T1558.001).
- It requires replication rights (normally Domain Admin), so it's a **post-compromise** action — by the time you see it, an attacker already has high privilege.

## Detection thinking (the takeaway)

This is a model for detecting advanced attacks: a raw event ID (4662) is useless alone because of noise. You narrow it with a specific GUID (the replication right), then separate attack from normal by **who** performed it (non-DC account). Understanding *what normal looks like* (only DCs replicate) is what makes the malicious combination stand out.
