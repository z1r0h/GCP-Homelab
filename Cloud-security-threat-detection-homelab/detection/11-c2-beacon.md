# 11 — C2 Beacon Simulation

| Field           | Detail                                                                           |
| --------------- | -------------------------------------------------------------------------------- |
| Status          | ✅ Completed                                                                      |
| MITRE Technique | [T1071 — Application Layer Protocol](https://attack.mitre.org/techniques/T1071/) |
| MITRE Tactic    | Command & Control                                                                |
| Log Source      | Sysmon Event 3 (Network) + Event 22 (DNS)                                        |
| Attack file     | [attacks/11-c2-beacon.md](../attacks/11-c2-beacon/README.md)                     |

---

## SPL Query

The most reliable signal in this lab is the **initial outbound connection** from a binary in a suspicious location (Temp/AppData) to an external host — not a count of repeated connections (see Notes for why).

```spl
index=* source="XmlWinEventLog:Microsoft-Windows-Sysmon/Operational" EventCode=3
(Image="*\\Temp\\*" OR Image="*\\AppData\\*")
Initiated="true"
| table _time, Computer, Image, DestinationIp, DestinationPort
| eval mitre_technique="T1071", mitre_tactic="Command and Control"
| sort -_time
```

This catches `C:\Windows\Temp\beacon.exe` making an outbound connection — a binary in Temp talking to the network is highly abnormal, regardless of how many times it connects.

### Optional — connection-count version (limited, see Notes)

```spl
index=* source="XmlWinEventLog:Microsoft-Windows-Sysmon/Operational" EventCode=3 DestinationIp="10.0.10.3"
| bucket _time span=5m
| stats count as connections values(DestinationPort) as ports by _time, Image, DestinationIp
| where connections > 2
| eval mitre_technique="T1071", mitre_tactic="Command and Control"
```

---

## Alert Settings

| Field      | Value                                                |
| ---------- | ---------------------------------------------------- |
| Title      | `C2 Beacon - Suspicious Outbound Connection - T1071` |
| Alert Type | Scheduled — Cron `*/5 * * * *` (every 5 min)         |
| Time range | Last 5 minutes                                       |
| Trigger    | Number of Results > 0                                |
| Throttle   | Off                                                  |
| Expires    | 24 hours                                             |
| Action     | Add to Triggered Alerts                              |

---

## Notes

- Key signal in this lab: a binary in `\Temp\` or `\AppData\` making an outbound connection (`Initiated="true"`). Normal software does not run from those paths and call out to the internet.

### Lab gotcha — why Event 3 doesn't show ongoing C2 traffic

During testing, the initial beacon connection (`beacon.exe → 10.0.10.3:443`) was logged, but **interacting with the Meterpreter session produced no new Event 3 records**. The reason:

- Meterpreter `reverse_https` establishes **one persistent (long-lived) connection**, then sends all C2 traffic *inside* that single connection.
- Sysmon Event 3 logs the **creation** of a network connection, not the data flowing through an existing one. So commands run over the session don't generate new Event 3 events.

This is why a connection-count threshold (`connections > N`) is unreliable for this kind of C2 — the count stays low even during heavy interaction. The detection above instead keys on the **initial connection from a suspicious binary**, which is the part Event 3 reliably captures.

### Real-world note

- **Persistent-connection C2 vs periodic beaconing are two different patterns.** Periodic beacons (e.g. some Cobalt Strike profiles) make repeated short connections at a fixed interval + jitter — those *are* visible as repeated Event 3 records and can be found with interval analysis. Persistent-connection C2 (Meterpreter reverse_https here) hides traffic in one long connection.
- For full C2 visibility, endpoint logs are not enough — production SOCs add **network-layer analysis** (Zeek/NetFlow/IDS) to inspect traffic volume, duration, and beacon timing inside connections.
- High-end C2 also uses domain fronting and legitimate cloud services as redirectors, making destination-IP-based detection weaker. Behavioural signals (binary location, parent process, JA3/TLS fingerprint) become more important.
- Sysmon Event 22 (DNS query) is a complementary signal when C2 resolves a domain rather than connecting to a hardcoded IP.
