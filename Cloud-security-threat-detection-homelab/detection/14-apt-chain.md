# 14 — Full APT Attack Chain

| Field | Detail |
|---|---|
| Status | ✅ Completed |
| MITRE Technique | [Multiple — Recon → Initial Access → Persistence → Cred Access → Lateral → Exfil](https://attack.mitre.org/matrices/enterprise/) |
| MITRE Tactic | Multiple |
| Log Source | Correlation across all sources |
| Attack file | [attacks/14-apt-chain.md](../attacks/14-apt-chain/README.md) |

---

## SPL Query

### Panel 1 — Kill chain stage summary (filtered to suspicious activity only)

This version does **not** count raw events. Each stage is filtered to the malicious pattern only — so the numbers reflect *attacker activity*, not normal background noise (e.g. routine 4624 logons or AD-internal 4662 replication).

```spl
index=* source="XmlWinEventLog:*"
| eval stage=case(
    EventCode=3 AND DestinationIp="10.0.10.3", "1-Recon/C2",
    EventCode=4625, "2-Initial Access (Brute Force)",
    EventCode=4104 AND (match(ScriptBlockText,"(?i)DownloadString|IEX|Invoke-Expression|Net.WebClient")), "3-Execution (PowerShell)",
    EventCode=4720, "4-Persistence (New Account)",
    EventCode=10 AND match(TargetImage,"(?i)lsass\.exe") AND match(GrantedAccess,"0x1010|0x1410|0x143a|0x1438"), "5-Credential Access (LSASS)",
    EventCode=4624 AND Logon_Type=3 AND AuthenticationPackageName="NTLM" AND NOT match(src_user,"\$$"), "6-Lateral Movement (PtH)",
    EventCode=5140 AND src_ip="10.0.10.3", "7-Discovery (SMB)",
    EventCode=4769 AND SessionKeyEncryptionType="0x17", "8-Kerberoasting",
    EventCode=4662 AND match(Properties,"1131f6aa") AND NOT match(src_user,"\$$"), "9-DCSync (Domain Dominance)")
| where isnotnull(stage)
| stats count as suspicious_events, min(_time) as first_seen, max(_time) as last_seen, dc(Computer) as hosts by stage
| sort stage
```

> Each branch reuses the exact filter from that scenario's detection rule (RC4 for Kerberoasting, replication GUID + non-DC account for DCSync, NTLM + non-machine for PtH, etc.). The result is a true attacker-activity timeline rather than a raw event dump.

### Panel 2 — Attack timeline

```spl
index=* source="XmlWinEventLog:*"
(EventCode=3 OR EventCode=4625 OR EventCode=4104 OR EventCode=4720 OR EventCode=10 OR EventCode=4624 OR EventCode=5140 OR EventCode=4769 OR EventCode=4662)
| eval stage=case(
    EventCode=3,"1-Recon/C2", EventCode=4625,"2-Initial Access",
    EventCode=4104,"3-Execution", EventCode=4720,"4-Persistence",
    EventCode=10,"5-Credential Access", EventCode=4624,"6-Lateral Movement",
    EventCode=5140,"7-Discovery", EventCode=4769,"8-Kerberoasting",
    EventCode=4662,"9-DCSync")
| timechart span=1h count by stage
```

---

## Dashboard

These panels are saved to the **APT Kill Chain Overview** dashboard, giving a single view of the full attack from recon to domain dominance — the way a SOC analyst presents an incident to stakeholders.

---

## The full kill chain

This capstone correlates all 13 prior scenarios into one attack story:

| Stage | Attack | Scenario | Technique |
|---|---|---|---|
| 1. Reconnaissance | Port scan | 01 | T1046 |
| 2. Initial Access | RDP brute force | 02 | T1110.001 |
| 3. Execution | PowerShell cradle | 03 | T1059.001 |
| 4. Persistence | New account / scheduled task / run key | 04, 07, 09 | T1136 / T1053 / T1547 |
| 5. Credential Access | Mimikatz LSASS dump | 05 | T1003.001 |
| 6. Lateral Movement | Pass-the-Hash | 06 | T1550.002 |
| 7. Discovery | SMB enumeration | 08 | T1135 |
| 8. Credential Access | Kerberoasting | 10 | T1558.003 |
| 9. Command & Control | C2 beacon | 11 | T1071 |
| 10. Domain Dominance | DCSync | 12 | T1003.006 |
| 11. Total Control | Golden Ticket | 13 | T1558.001 |

---

## Notes

- This is a **correlation dashboard**, not a single alert. The value is showing how individual detections combine into one coherent attack narrative — which is exactly what incident response and threat hunting require.
- **Raw event volume is not the same as alerts.** An early version of this panel counted raw event codes and showed ~10,000 "Lateral Movement" events — because successful logons (4624) happen constantly in normal operation, not only during Pass-the-Hash. The query above fixes this by applying each scenario's real detection filter (NTLM + non-machine account for PtH, RC4 for Kerberoasting, replication GUID + non-DC for DCSync, and so on), so every count reflects genuine attacker activity. This distinction — raw telemetry vs. true positives — is the single most important lesson of the capstone.
- In a real SOC this correlation work is done by an **Analytic Story / correlation search** in Splunk Enterprise Security, or by a SOAR playbook. This lab reproduces the concept manually with hand-built SPL and a dashboard.
- The timeline panel matters as much as the counts: seeing recon → access → persistence → credential theft → domain dominance unfold in time order is how an analyst reconstructs an incident and reports it.

## The takeaway

Individual detections answer "did this technique fire?" The correlation dashboard answers the question a SOC actually cares about: **"is there an attack in progress, and how far has it gone?"** Building that narrative from scattered events — and knowing which events are signal vs. noise — is the core analytical skill this entire lab was built to practise.
