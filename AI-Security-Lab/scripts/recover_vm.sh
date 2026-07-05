#!/usr/bin/env bash
# recover_vm.sh - One-command recovery of a lab VM from its baseline machine image.
#
# Rebuilds a VM entirely from machine image `baseline-<vm>` (taken in docs/setup/12).
# Machine type, GPU accelerator, Spot/provisioning model, network, subnet, tags, and
# disk contents are all captured in the machine image and restored automatically —
# no per-VM hardware profile to maintain here (that used to drift out of sync with
# the actual `create` commands in docs/setup/03-05).
# Run wherever gcloud is authenticated (Cloud Shell or your laptop) — NOT on the VM.
#
# Usage:  bash scripts/recover_vm.sh <vm-name> [zone]
#   bash scripts/recover_vm.sh cyber-ai-lab-vm asia-southeast1-a
set -euo pipefail

VM="${1:-}"
ZONE="${2:-$(gcloud config get-value compute/zone 2>/dev/null || true)}"
IMAGE="baseline-${VM}"

[ -z "$VM" ]   && { echo "Usage: $0 <vm-name> [zone]"; exit 1; }
[ -z "$ZONE" ] && { echo "[!] No zone. Pass it: $0 $VM <zone>  (or: gcloud config set compute/zone ...)"; exit 1; }

# Confirm the baseline machine image exists before touching anything.
if ! gcloud compute machine-images describe "$IMAGE" >/dev/null 2>&1; then
  echo "[!] Machine image '$IMAGE' not found. Take a baseline first (docs/setup/12 §12.2)."; exit 1
fi

echo "[*] Recovering '$VM' from machine image '$IMAGE' (zone $ZONE)"

# 1) Delete the broken instance if it still exists.
if gcloud compute instances describe "$VM" --zone="$ZONE" >/dev/null 2>&1; then
  read -rp "    Instance '$VM' exists. Delete and rebuild from baseline? (y/N): " ans
  [ "${ans,,}" = "y" ] || { echo "[i] Aborted."; exit 1; }
  gcloud compute instances delete "$VM" --zone="$ZONE" --quiet
fi

# 2) Recreate the instance straight from the machine image - machine type, GPU,
#    Spot config, network/subnet, tags, and no-address are all inherited.
gcloud compute instances create "$VM" --zone="$ZONE" --source-machine-image="$IMAGE"

echo "[+] '$VM' recovered from '$IMAGE'. Reconnect via IAP (docs/setup/06), then:"
echo "    lab VM -> bash scripts/start_lab.sh   |   Splunk -> sudo /opt/splunk/bin/splunk status"
