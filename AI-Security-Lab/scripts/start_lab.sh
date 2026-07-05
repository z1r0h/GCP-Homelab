#!/usr/bin/env bash
# start_lab.sh - Interactive menu to start Docker compose profiles (GCP / Linux edition).
# Run on the lab VM:  bash scripts/start_lab.sh
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE="$SCRIPT_DIR/../infrastructure/docker-compose.yml"
CALDERA_DIR="$SCRIPT_DIR/../external/caldera"

assert_caldera() {
  # offense/all build CALDERA from source (no official image). Offer to clone if missing.
  [ -f "$CALDERA_DIR/Dockerfile" ] && return 0
  echo "[!] CALDERA source not found at external/caldera." >&2
  read -rp "    Clone it now? (y=clone / n=continue without / a=abort): " ans
  case "${ans,,}" in
    y) git clone https://github.com/mitre/caldera.git --recursive "$CALDERA_DIR" && return 0 || return 1 ;;
    n) echo "[i] Continuing - caldera will fail to build; other services unaffected."; return 0 ;;
    *) echo "[i] Aborted."; return 1 ;;
  esac
}

echo "========================================"
echo "  AI Security Lab - Launcher (GCP/Linux)"
echo "========================================"
echo "  1. Defense Only (Wazuh)"
echo "  2. Target Apps (vuln LLMs + DVWA/Juice Shop/ml-api)"
echo "  3. Offense (Kali, GoPhish, CALDERA)"
echo "  4. ML Workbench (Jupyter Lab -> http://localhost:8889 , token 'cyberlab')"
echo "  5. Start ALL"
echo "  6. Stop ALL"
read -rp "Enter choice (1-6): " choice

case "$choice" in
  1) docker compose -f "$COMPOSE" --profile defense up -d ;;
  2) docker compose -f "$COMPOSE" --profile targets up -d ;;
  3) assert_caldera && docker compose -f "$COMPOSE" --profile offense up -d ;;
  4) docker compose -f "$COMPOSE" --profile ml up -d ;;
  5) assert_caldera && docker compose -f "$COMPOSE" --profile all up -d ;;
  6) docker compose -f "$COMPOSE" down ;;
  *) echo "Invalid choice." ;;
esac
