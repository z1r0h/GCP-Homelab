# 04 — Splunk Server Setup

## Install Splunk Enterprise on Ubuntu

SSH into `splunk-server` and run:

```bash
# Download Splunk (check splunk.com for the current version/build string)
wget -O splunk.deb \
  "https://download.splunk.com/products/splunk/releases/10.4.0/linux/splunk-10.4.0-f798d4d49089-linux-amd64.deb"

# Install (extracts to /opt/splunk)
sudo dpkg -i splunk.deb

# Create the dedicated splunk user (best practice — do NOT run as root)
sudo useradd -m splunk
sudo chown -R splunk:splunk /opt/splunk

# First start as the splunk user — accepts license and creates the admin account
sudo -u splunk /opt/splunk/bin/splunk start --accept-license

# Stop it again so we can enable boot-start under systemd
sudo -u splunk /opt/splunk/bin/splunk stop

# Enable boot-start as a systemd service owned by the splunk user
sudo /opt/splunk/bin/splunk enable boot-start -user splunk -systemd-managed 1

# Start via systemd and check status
sudo systemctl start Splunkd
sudo systemctl status Splunkd
```

> The systemd service is named `Splunkd` by default. If your version names it differently, run `systemctl list-units | grep -i splunk` to confirm.

> ⚠️ Do **not** use `--run-as-root`. Running Splunk as root and then enabling boot-start as the `splunk` user causes file-ownership/PID conflicts and the service fails to start on boot.

---

## Access Splunk Web

Open IAP tunnel then go to `http://localhost:8000`

```bash
gcloud compute start-iap-tunnel splunk-server 8000 --local-host-port=127.0.0.1:8000 --zone=asia-southeast1-a
```

First login uses the admin account created during the first start.

---

## Activate License

1. Go to **Settings → Licensing**
2. Click **Add License**
3. Upload your Developer license file
4. Restart when prompted: `sudo systemctl restart Splunkd`

---

## Create the Index

**Settings → Indexes → New Index**
- Index name: `wineventlog`
- Leave defaults → Save

---

## Enable Log Receiving (Port 9997)

1. Go to **Settings → Forwarding and Receiving**
2. Under **Receive Data** column → **Configure Receiving**
3. Click **New Receiving Port** → enter `9997` → Save

Splunk is now ready to receive logs from Windows forwarders.

---

## Install Splunk Apps

Install the following apps via **Apps → Find More Apps**. Install in this exact order:

| Order | App                                 | Splunkbase ID                                  | Role                                                                              |
| ----- | ----------------------------------- | ---------------------------------------------- | --------------------------------------------------------------------------------- |
| 1     | Splunk Add-on for Sysmon            | [5709](https://splunkbase.splunk.com/app/5709) | Parses Sysmon XML into searchable fields (EventCode, SourceIp, CommandLine, etc.) |
| 2     | Splunk Add-on for Microsoft Windows | [742](https://splunkbase.splunk.com/app/742)   | Parses native Windows Event Log fields (EventCode 4625, 4720, 4698, etc.)         |
| 3     | Splunk Security Essentials          | [3435](https://splunkbase.splunk.com/app/3435) | SPL reference library and detection rule templates mapped to MITRE ATT&CK         |


Restart Splunk after installing all apps:
```bash
sudo systemctl restart Splunkd
```

> ⚠️ The old Sysmon App (ID 3544) is archived — do not use it. Use 5709 instead.

### What each app actually does

**Apps 1 & 2 — Data foundation (install first)**
Without these, Sysmon and Windows logs arrive as raw XML with no searchable fields. These TAs parse the data so fields like `EventCode`, `SourceIp`, `Image`, `CommandLine` are available in SPL.

> **Note:** After installing TA for Windows (742), all Windows sourcetypes are normalised to `xmlwineventlog` (lowercase). This is expected behaviour — it does not affect functionality.

**App 3 — SPL reference library (not auto-alerting)**
Security Essentials is a detection rule library, not an automatic alert system. All 900+ rules are **disabled by default**. Use it to:
- Look up how to detect a specific attack
- Copy and adapt SPL queries for your own alerts
- Understand what data sources each detection needs


### Important: Alerts must be built manually

None of these apps auto-generate alerts. To detect attacks, you must write SPL queries and save them as alerts. See [`detection/`](../../detection/) for all SPL queries used in this lab.

Example — Port Scan detection (T1046):

```spl
index=wineventlog source="XmlWinEventLog:Microsoft-Windows-Sysmon/Operational" EventCode=3
| bucket _time span=1m
| stats dc(DestinationPort) as unique_ports by _time, SourceIp, DestinationIp
| where unique_ports > 20
| eval mitre_technique="T1046"
| eval mitre_tactic="Discovery"
```

Save as: **Alert → Real-time → Per-Result → Add to Triggered Alerts**
