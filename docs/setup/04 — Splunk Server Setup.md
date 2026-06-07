# 04 — Splunk Server Setup

## Install Splunk Enterprise on Ubuntu

SSH into `splunk-server` and run:

```bash
# Download Splunk
wget -O splunk-10.4.0-linux-amd64.deb \
  "https://download.splunk.com/products/splunk/releases/10.4.0/linux/splunk-10.4.0-f798d4d49089-linux-amd64.deb"

# Install
sudo dpkg -i splunk-10.4.0-linux-amd64.deb

# First start (creates admin account)
sudo /opt/splunk/bin/splunk start --accept-license --run-as-root

# Create splunk user and transfer ownership
sudo useradd -m splunk
sudo chown -R splunk:splunk /opt/splunk

# Enable auto-start on boot
sudo /opt/splunk/bin/splunk enable boot-start -user splunk

# Check status
sudo systemctl status splunk
```

---

## Access Splunk Web

Open IAP tunnel then go to `http://localhost:8000`

```bash
gcloud compute start-iap-tunnel splunk-server 8000 --local-host-port=127.0.0.1:8000 --zone=asia-southeast1-a
```

---

## Activate License

1. Go to **Settings → Licensing**
2. Click **Add License**
3. Upload your Developer license file

---

## Enable Log Receiving (Port 9997)

1. Go to **Settings → Forwarding and Receiving**
2. Under **Receive Data** column → **Configure Receiving**
3. Click **New Receiving Port** → enter `9997` → Save

Splunk is now ready to receive logs from Windows forwarders.

---

## Install Splunk Apps

Install the following apps via **Apps → Find More Apps**:

| Order | App | Splunkbase ID | Purpose |
|---|---|---|---|
| 1 | Splunk Add-on for Sysmon | [5709](https://splunkbase.splunk.com/app/5709) | CIM field mapping for Sysmon data |
| 2 | Splunk Security Essentials | [3435](https://splunkbase.splunk.com/app/3435) | 100+ detection rules with MITRE mapping |
| 3 | MITRE ATT&CK App for Splunk | [4617](https://splunkbase.splunk.com/app/4617) | ATT&CK matrix heatmap dashboard |

> Install in order 1 → 2 → 3. App 5709 is the CIM foundation that the others depend on.

> ⚠️ The old Sysmon App (ID 3544) is archived — do not use it.
