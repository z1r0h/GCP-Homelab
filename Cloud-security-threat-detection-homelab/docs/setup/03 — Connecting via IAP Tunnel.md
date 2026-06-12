# 03 — Connecting via IAP Tunnel

All VMs have no public IP. Access is through Google Identity-Aware Proxy (IAP) tunnel only.

## Prerequisites
Download and install [VNC](https://www.realvnc.com/en/connect/download/viewer/windows/) for Kali GUI access

Download and install [Google Cloud SDK](https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe), then authenticate:

```bash
gcloud auth login
gcloud config set project splunk-threat-detection-lab
```

---

## Connect to Windows VMs (RDP)

### Step 1 — Open IAP tunnel

```bash
# win-dc
gcloud compute start-iap-tunnel win-dc 3389 --local-host-port=127.0.0.1:13389 --zone=asia-southeast1-a

# win-client
gcloud compute start-iap-tunnel win-client 3389 --local-host-port=127.0.0.2:13388 --zone=asia-southeast1-a
```

Keep the terminal window open.

### Step 2 — Connect via RDP

| VM | RDP Host | Username |
|---|---|---|
| win-dc | `127.0.0.1:13389` | `200TEAMOK\Administrator` |
| win-client | `127.0.0.2:13388` | `200TEAMOK\Administrator` |

> ⚠️ Use lab credentials only. Never reuse these passwords in production.

---

## Connect to Linux VMs (SSH)

```bash
# splunk-server
gcloud compute ssh splunk-server --zone=asia-southeast1-a --tunnel-through-iap

# kali attacker
gcloud compute ssh kali-linux-attacker-vm --zone=asia-southeast1-a --tunnel-through-iap
```

---

## Connect to Splunk Web UI

```bash
gcloud compute start-iap-tunnel splunk-server 8000 --local-host-port=127.0.0.1:8000 --zone=asia-southeast1-a
```

Then open browser: `http://localhost:8000`

---

## Connect to Kali GUI (VNC)

```bash
gcloud compute start-iap-tunnel kali-linux-attacker-vm 5901 --local-host-port=127.0.0.1:5901 --zone=asia-southeast1-a
```

Then connect with any VNC client to `127.0.0.1:5901`.
