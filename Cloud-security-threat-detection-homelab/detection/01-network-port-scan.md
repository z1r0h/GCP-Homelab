# 01 — Network Port Scan

| Field           | Detail                                                                          |
| --------------- | ------------------------------------------------------------------------------- |
| Status          | ✅ Completed                                                                     |
| MITRE Technique | [T1046 — Network Service Discovery](https://attack.mitre.org/techniques/T1046/) |
| MITRE Tactic    | Discovery (TA0007)                                                              |
| Log Source      | Sysmon Event 3 (Network Connection)                                             |
| Attack file     | [attacks/01-network-port-scan](../attacks/01-network-port-scan/README.md)       |

---

## SPL Query

```spl
index=wineventlog source="XmlWinEventLog:Microsoft-Windows-Sysmon/Operational" EventCode=3 SourceIp="10.0.10.3"
| bucket _time span=1m
| stats dc(DestinationPort) as unique_ports by _time, SourceIp, DestinationIp
| where unique_ports > 1
| eval mitre_technique="T1046", mitre_tactic="Discovery"
| table _time, SourceIp, DestinationIp, unique_ports, mitre_technique, mitre_tactic
```

---

## Alert Settings

| Field      | Value                                        |
| ---------- | -------------------------------------------- |
| Title      | `Port Scan Detected - T1046`                 |
| Alert Type | Scheduled — Cron `*/5 * * * *` (every 5 min) |
| Time range | Last 5 minutes                               |
| Trigger    | Number of Results > 0                        |
| Throttle   | Off                                          |
| Expires    | 24 hours                                     |
| Action     | Add to Triggered Alerts                      |

> Scheduled (not real-time) is the recommended type — Splunk's own docs advise scheduled alerts to save resources, and they show reliably in **Activity → Triggered Alerts**, simulating a Tier 1 analyst's alert queue.

---

## Notes

- **Sysmon cannot see most of a port scan. This is normal, not a setup mistake.** Sysmon Event 3 only logs connections that a program on the machine starts or fully completes. An nmap probe coming _in_ to win-dc is handled by Windows itself, not by a program, so Sysmon does not log it. Even `nmap -sT` usually shows only a few ports (like 3389 RDP, 5985-5986 WinRM), not all the open ports nmap finds.
- **Why nmap still sees everything:** nmap checks the open/closed state from the replies win-dc sends back (this is network-level info, seen from the attacker side). Sysmon runs on the victim and logs what programs do. They are two different data sources, so they don't have to match.
- **The right tool for port scans:** the network layer — firewall logs, IDS/IPS (Suricata/Snort), or NetFlow / GCP VPC Flow Logs. A real SOC catches all scan types there. Sysmon Event 3 is better for finding **C2 beacons** and **lateral movement** (outbound connections started by a program), which this lab uses it for later.
- **What this scenario really teaches:** the limit of endpoint logs. Knowing _what each log source can and cannot see_ is a key SOC analyst skill. The query below catches the part of the scan that Sysmon does log.
- The `unique_ports > N` value and `SourceIp="10.0.10.3"` filter are set for the lab. In production, use the internal subnet range and exclude known scanners.
