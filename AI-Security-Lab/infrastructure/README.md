# 🏗️ Infrastructure Definitions

This folder contains the core infrastructure definitions for the AI Security Lab.

## docker-compose.yml

Uses **Docker Profiles** to manage memory on a 32GB machine:

| Profile | Command | What starts |
|---|---|---|
| `defense` | `docker compose --profile defense up -d` | Wazuh Manager |
| `targets` | `docker compose --profile targets up -d` | llm-vuln-app, rag-vuln-app, agent-vuln-app, target-ml-api, DVWA, Juice Shop |
| `offense` | `docker compose --profile offense up -d` | Kali (built with tools†), GoPhish, CALDERA* |
| `ml` | `docker compose --profile ml up -d` | `jupyter-ml-lab` (Jupyter Lab → http://localhost:8889, token `cyberlab`) |
| `all` | `docker compose --profile all up -d` | Everything |

> *CALDERA has no official Docker image — clone & build it first:
> `git clone https://github.com/mitre/caldera.git --recursive ../external/caldera`
> (the `offense`/`all` profiles build from `external/caldera`).
>
> †Kali is built from `infrastructure/kali/Dockerfile` (stock `kali-rolling` ships no tools);
> the image bakes in nmap/sqlmap/hydra/netcat-traditional/iodine/dnsutils/whatweb/python3.
>
> The `jupyter-ml-lab` service mounts `apps/ml-notebooks` at `/home/jovyan/work` (port 8889,
> since 8888 is CALDERA). Used by scenarios 11/13/16/23.

### Volume Mounts (Critical)
The Wazuh Manager container mounts:
- `configs/wazuh/ossec.conf` → `/var/ossec/etc/ossec.conf` (Splunk HEC forwarding config)
- `detection-rules/wazuh/custom_ai_rules.xml` → `/var/ossec/etc/rules/local_rules.xml` (AI detection rules)
- `ai-logs` shared named volume → `/var/log/ai-lab` (read-only) for collecting target app JSON logs

### Log Pipeline (GCP edition)
Each target app writes **single-layer structured JSON** to the shared `ai-logs` volume
(`/var/log/ai-lab/*.json`) — and also to stdout for `docker logs` debugging. Wazuh
reads the clean JSON files directly from that volume (bypassing Docker's double-JSON
wrapping) and forwards Level 5+ alerts to Splunk HEC **directly over the VPC-internal IP**
(same VPC as the Splunk VM — no IAP tunnel needed for log forwarding).

## configs/
- `wazuh/ossec.conf`: **Replace `YOUR_SPLUNK_HEC_TOKEN` and `YOUR_SPLUNK_INTERNAL_IP`** before first launch.
- `sysmon/`: no config is vendored here — we deploy [olafhartong/sysmon-modular](https://github.com/olafhartong/sysmon-modular)'s
  balanced config, fetched live from GitHub on each Windows VM (see `docs/setup/09` §9.3). Requires a matching
  ingest-time filter on the Splunk side (`docs/setup/08` §8.1a) to avoid blowing the 10GB/day license on EventID 7 (ImageLoad).
