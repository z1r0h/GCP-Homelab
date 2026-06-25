# 10 — Kerberoasting

| Field           | Detail                                                                                                       |
| --------------- | ------------------------------------------------------------------------------------------------------------ |
| Status          | ✅ Completed                                                                                                  |
| MITRE Technique | [T1558.003 — Steal or Forge Kerberos Tickets: Kerberoasting](https://attack.mitre.org/techniques/T1558/003/) |
| MITRE Tactic    | Credential Access                                                                                            |
| Log Source      | Windows Security Event 4769                                                                                  |
| Attack file     | [attacks/10-kerberoasting.md](../attacks/10-kerberoasting/README.md)                                         |

---

## SPL Query

```spl
index=* source="XmlWinEventLog:Security" EventCode=4769 SessionKeyEncryptionType=0x17
| search ServiceName!="krbtgt" ServiceName!="*$"
| table _time, Computer, TargetUserName, ServiceName, SessionKeyEncryptionType, IpAddress
| eval mitre_technique="T1558.003", mitre_tactic="Credential Access"
| sort -_time
```

> Field names here match this lab's TA output: `SessionKeyEncryptionType`, `ServiceName`, `TargetUserName`, `IpAddress`. Other TA versions may use `Ticket_Encryption_Type` / `Service_Name` / `Account_Name` — confirm with `| table *` on a sample event.


---

## Alert Settings

| Field      | Value                                                |
| ---------- | ---------------------------------------------------- |
| Title      | `Kerberoasting - RC4 Service Ticket Request - T1558` |
| Alert Type | Scheduled — Cron `*/5 * * * *` (every 5 min)         |
| Time range | Last 5 minutes                                       |
| Trigger    | Number of Results > 0                                |
| Throttle   | Off                                                  |
| Expires    | 24 hours                                             |
| Action     | Add to Triggered Alerts                              |

---

## Notes

- Event 4769 = Kerberos service ticket (TGS) requested. Encryption type **0x17 (RC4)** is the classic Kerberoasting signal — attackers request RC4 because the resulting ticket hash is far easier to crack offline than AES.
- Key fields: `ServiceName` = the targeted service account (e.g. svc-sql), `TargetUserName` = the account making the request, `IpAddress` = source, `SessionKeyEncryptionType` = 0x17 for RC4.
- Exclude `krbtgt` and machine accounts (`ServiceName` ending in `$`) — those are normal Kerberos traffic.


### Lab gotcha — modern DCs disable RC4 by default

Windows Server 2022 disables RC4 out of the box, so the first Kerberoasting attempt fails with:

```
KDC_ERR_ETYPE_NOSUPP (KDC has no support for encryption type)
```

This is the DC being correctly hardened. To demonstrate classic RC4 Kerberoasting in the lab, RC4 was explicitly enabled on the target service account:

powershell

```powershell
# On win-dc — enable RC4 for the service account (simulates a weak/legacy config)
Set-ADUser svc-sql -KerberosEncryptionType RC4,AES128,AES256
```

After this, the attacker can request an RC4 ticket and the 0x17 event appears.

### Real-world note

- In a fully AES environment, Kerberoasting still happens but uses AES tickets — the `0x17` filter would miss it. There, detection shifts to **behaviour**: a single account requesting TGS tickets for many different SPNs in a short window, regardless of encryption type.
- Some legacy applications legitimately use RC4, so baseline normal RC4 usage before alerting in production.
- Requesting a service ticket is a normal Kerberos operation and does **not** generate a logon failure — this is why Kerberoasting is stealthy and why 4769 monitoring matters.