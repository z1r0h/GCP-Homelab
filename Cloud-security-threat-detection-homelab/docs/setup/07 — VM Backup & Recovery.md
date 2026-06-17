# 07 — VM Backup & Recovery

After completing the full setup (especially [06 — full logging setup](06%20%E2%80%94%20Sysmon%2C%20Forwarder%20%26%20Full%20Logging%20Setup.md)), snapshot all 4 VMs as clean baseline images. This lets you reset the entire lab to a known-good, fully-logging state after any attack simulation.

---

## Create Baseline Snapshots

Run from your local machine (Google Cloud SDK Shell):

```bash
# win-dc
gcloud compute machine-images create windc-clean \
  --source-instance=win-dc \
  --source-instance-zone=asia-southeast1-a

# win-client
gcloud compute machine-images create winclient-clean \
  --source-instance=win-client \
  --source-instance-zone=asia-southeast1-a

# splunk-server
gcloud compute machine-images create splunkserver-clean \
  --source-instance=splunk-server \
  --source-instance-zone=asia-southeast1-a

# kali attacker
gcloud compute machine-images create kali-linux-attacker-vm-clean \
  --source-instance=kali-linux-attacker-vm \
  --source-instance-zone=asia-southeast1-a
```

---

## One-Command Recovery

> ⚠️ **You MUST specify the fixed internal IP.** Without `--private-network-ip`, GCP assigns a random IP and breaks AD/DNS (win-dc), domain membership (win-client), and log forwarding (splunk-server).

After an attack simulation, restore any VM to its clean baseline:

```bash
# Restore win-client (most common — restore after any attack that modifies it)
gcloud compute instances delete win-client --zone=asia-southeast1-a --quiet && \
gcloud compute instances create win-client \
  --source-machine-image=winclient-clean \
  --zone=asia-southeast1-a \
  --subnet=lab-subnet \
  --private-network-ip=10.0.10.20 \
  --no-address

# Restore win-dc
gcloud compute instances delete win-dc --zone=asia-southeast1-a --quiet && \
gcloud compute instances create win-dc \
  --source-machine-image=windc-clean \
  --zone=asia-southeast1-a \
  --subnet=lab-subnet \
  --private-network-ip=10.0.10.10 \
  --no-address

# Restore splunk-server (rarely needed — drop --no-address if you want an external IP)
gcloud compute instances delete splunk-server --zone=asia-southeast1-a --quiet && \
gcloud compute instances create splunk-server \
  --source-machine-image=splunkserver-clean \
  --zone=asia-southeast1-a \
  --subnet=lab-subnet \
  --private-network-ip=10.0.10.50
```

---

## Easier: Use the Recovery Script

Instead of typing the commands, use the helper script (it handles IPs automatically):

```bash
./scripts/recovery/restore.sh win-client     # restore just win-client
./scripts/recovery/restore.sh win-dc         # restore just win-dc
./scripts/recovery/restore.sh all            # restore all three
```

---

## When to Restore

| Attack type | Restore needed? |
|---|---|
| Port scan, enumeration (read-only) | No |
| New user, scheduled task, registry (persistence) | Yes — restore target VM |
| Credential dumping, DCSync | Restore target after |
| Full APT chain | Restore all |

> 💡 Tip: Restore `win-client` after every attack that modifies it. `splunk-server` almost never needs restoring — attacks don't touch it, and the logs it has already collected stay in the index regardless.
