# 07 — VM Backup & Recovery

After completing the full setup, snapshot all 4 VMs as clean baseline images.  
This lets you reset the entire lab to a known-good state after any attack simulation.

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

After an attack simulation, restore any VM to its clean baseline:

```bash
# Restore win-client
gcloud compute instances delete win-client --zone=asia-southeast1-a --quiet && \
gcloud compute instances create win-client \
  --source-machine-image=winclient-clean \
  --zone=asia-southeast1-a

# Restore win-dc
gcloud compute instances delete win-dc --zone=asia-southeast1-a --quiet && \
gcloud compute instances create win-dc \
  --source-machine-image=windc-clean \
  --zone=asia-southeast1-a

# Restore splunk-server
gcloud compute instances delete splunk-server --zone=asia-southeast1-a --quiet && \
gcloud compute instances create splunk-server \
  --source-machine-image=splunkserver-clean \
  --zone=asia-southeast1-a

# Restore kali attacker
gcloud compute instances delete kali-linux-attacker-vm --zone=asia-southeast1-a --quiet && \
gcloud compute instances create kali-linux-attacker-vm \
  --source-machine-image=kali-linux-attacker-vm-clean \
  --zone=asia-southeast1-a
```

> 💡 Tip: Restore `win-client` after every attack simulation. Only restore `win-dc` or `splunk-server` if you need a full environment reset.
