#!/usr/bin/env bash
# verify_health.sh - Pre-flight health check (GCP / Linux edition).
# Run on the lab VM:  bash scripts/verify_health.sh
# Splunk HEC is same-VPC: export SPLUNK_HEC_URL=https://<splunk-internal-ip>:8088 to test it.
set -uo pipefail

echo "========================================"
echo "  AI Security Lab - Health Check (GCP)"
echo "========================================"

echo "[1/3] Ollama (http://localhost:11434)..."
if curl -fsS -m 5 http://localhost:11434 >/dev/null 2>&1; then
  echo "  [OK] Ollama is running"
else
  echo "  [FAIL] Ollama unreachable. Is the ollama systemd service up? (systemctl status ollama)"
fi

echo "[2/3] Splunk HEC (${SPLUNK_HEC_URL:-<not set>})..."
if [ -n "${SPLUNK_HEC_URL:-}" ]; then
  if curl -fsSk -m 5 "${SPLUNK_HEC_URL%/}/services/collector/health" >/dev/null 2>&1; then
    echo "  [OK] Splunk HEC reachable"
  else
    echo "  [FAIL] HEC unreachable. Same VPC: check Splunk internal IP + firewall allows :8088."
  fi
else
  echo "  [SKIP] export SPLUNK_HEC_URL=https://<splunk-internal-ip>:8088 to test"
fi

echo "[3/3] Docker containers..."
if docker ps --format '{{.Names}} | {{.Status}}' 2>/dev/null | grep -q .; then
  docker ps --format '  {{.Names}} | {{.Status}}'
else
  echo "  [INFO] No running containers. Run start_lab.sh first."
fi

echo "Health check complete."
