#!/usr/bin/env bash
# recover_vm.sh - One-command recovery of a lab VM from its baseline snapshot.
#
# Rebuilds a VM's boot disk from snapshot `baseline-<vm>` (taken in docs/setup/12),
# then recreates the instance with the SAME hardware/network profile used at setup.
# Run wherever gcloud is authenticated (Cloud Shell or your laptop) — NOT on the VM.
#
# Usage:  bash scripts/recover_vm.sh <vm-name> [zone]
#   bash scripts/recover_vm.sh cyber-ai-lab-vm asia-southeast1-a
set -euo pipefail

VM="${1:-}"
ZONE="${2:-$(gcloud config get-value compute/zone 2>/dev/null || true)}"
NETWORK="security-lab-vpc"
SUBNET="lab-subnet"
SNAP="baseline-${VM}"

[ -z "$VM" ]   && { echo "Usage: $0 <vm-name> [zone]"; exit 1; }
[ -z "$ZONE" ] && { echo "[!] No zone. Pass it: $0 $VM <zone>  (or: gcloud config set compute/zone ...)"; exit 1; }

# Per-VM hardware profile — must match the create commands in docs/setup/03-05.
case "$VM" in
  cyber-ai-lab-vm)
    EXTRA=(--machine-type=n1-standard-8 --provisioning-model=SPOT
           --instance-termination-action=STOP --maintenance-policy=TERMINATE
           --accelerator=type=nvidia-tesla-t4,count=1)
    TAGS="ai-lab" ;;
  splunk-vm)
    EXTRA=(--machine-type=e2-standard-4)
    TAGS="splunk" ;;
  ad-dc-vm|win-client-vm)
    EXTRA=(--machine-type=e2-standard-2)
    TAGS="windows" ;;
  *)
    echo "[!] Unknown VM '$VM'. Add its profile to recover_vm.sh."; exit 1 ;;
esac

# Confirm the baseline snapshot exists before touching anything.
if ! gcloud compute snapshots describe "$SNAP" >/dev/null 2>&1; then
  echo "[!] Snapshot '$SNAP' not found. Take a baseline first (docs/setup/12 §12.2)."; exit 1
fi

echo "[*] Recovering '$VM' from snapshot '$SNAP' (zone $ZONE)"

# 1) Delete the broken instance if it still exists.
if gcloud compute instances describe "$VM" --zone="$ZONE" >/dev/null 2>&1; then
  read -rp "    Instance '$VM' exists. Delete and rebuild from baseline? (y/N): " ans
  [ "${ans,,}" = "y" ] || { echo "[i] Aborted."; exit 1; }
  gcloud compute instances delete "$VM" --zone="$ZONE" --quiet
fi

# 2) Remove any leftover boot disk with the same name (so we can recreate it).
if gcloud compute disks describe "$VM" --zone="$ZONE" >/dev/null 2>&1; then
  gcloud compute disks delete "$VM" --zone="$ZONE" --quiet
fi

# 3) Recreate the boot disk from the baseline snapshot.
gcloud compute disks create "$VM" --zone="$ZONE" \
  --source-snapshot="$SNAP" --type=pd-balanced

# 4) Recreate the instance on that disk — no public IP, same VPC/subnet/tags.
gcloud compute instances create "$VM" --zone="$ZONE" \
  --disk=name="$VM",boot=yes,auto-delete=yes \
  --network="$NETWORK" --subnet="$SUBNET" --no-address --tags="$TAGS" \
  "${EXTRA[@]}"

echo "[+] '$VM' recovered from '$SNAP'. Reconnect via IAP (docs/setup/06), then:"
echo "    lab VM -> bash scripts/start_lab.sh   |   Splunk -> sudo /opt/splunk/bin/splunk status"
