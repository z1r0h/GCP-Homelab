#!/bin/bash
# Restore lab VMs to clean baseline images, preserving fixed internal IPs.
# Usage: ./restore.sh [win-client|win-dc|splunk-server|all]
#
# IMPORTANT: --private-network-ip MUST be specified, otherwise GCP assigns a
# random internal IP and breaks AD/DNS, domain membership, and log forwarding.

ZONE="asia-southeast1-a"
SUBNET="lab-subnet"

# VM -> fixed internal IP map
declare -A VM_IP=(
  ["win-dc"]="10.0.10.10"
  ["win-client"]="10.0.10.20"
  ["splunk-server"]="10.0.10.50"
)

# VM -> baseline machine image map
declare -A VM_IMAGE=(
  ["win-dc"]="windc-clean"
  ["win-client"]="winclient-clean"
  ["splunk-server"]="splunkserver-clean"
)

restore_vm () {
  local VM=$1
  local IMAGE=${VM_IMAGE[$VM]}
  local IP=${VM_IP[$VM]}

  echo "[*] Restoring $VM  (image: $IMAGE, ip: $IP) ..."
  gcloud compute instances delete "$VM" --zone="$ZONE" --quiet
  gcloud compute instances create "$VM" \
    --source-machine-image="$IMAGE" \
    --zone="$ZONE" \
    --subnet="$SUBNET" \
    --private-network-ip="$IP" \
    --no-address
  echo "[+] $VM restored at $IP."
}

case "$1" in
  win-client|win-dc|splunk-server)
    restore_vm "$1"
    ;;
  all)
    restore_vm win-client
    restore_vm win-dc
    restore_vm splunk-server
    ;;
  *)
    echo "Usage: $0 [win-client|win-dc|splunk-server|all]"
    exit 1
    ;;
esac
