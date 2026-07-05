# 🔍 Sysmon Configurations

We use **[olafhartong/sysmon-modular](https://github.com/olafhartong/sysmon-modular)** — the industry-standard,
community-maintained Sysmon config (widely used by real SOC teams, rules tagged to MITRE ATT&CK techniques).
It is **not vendored into this repo** — like CALDERA, it's fetched live at deploy time (see `docs/setup/09` §9.3),
since it's actively maintained upstream and we want the latest rules, not a frozen copy.

- **Variant used**: the default **balanced** config (`sysmonconfig.xml`, schemaversion 4.90, "medium verbosity").
- **Download**: `https://raw.githubusercontent.com/olafhartong/sysmon-modular/master/sysmonconfig.xml`
- **Install**: `Sysmon64.exe -accepteula -i sysmonconfig.xml` (first install) or `-c sysmonconfig.xml` (update existing).

> ⚠️ **License warning**: this config is far more verbose than a hand-trimmed minimal config — it enables
> EventID 7 (ImageLoad), which alone is typically 60-80% of total Sysmon volume. On a 10GB/day Splunk
> Developer License, this can blow the quota fast. **See `docs/setup/08` §8.1a** for the required Splunk-side
> ingest-time filter (drops EventID 7 before indexing, at zero license cost) before you rely on this in the lab.
