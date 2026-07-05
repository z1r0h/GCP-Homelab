# 🛡️ Wazuh Configurations
- `ossec.conf`: The main Wazuh manager configuration. We added a custom `<integration>` block to forward alerts via HTTP Event Collector (HEC) to Splunk.
**Operation (GCP edition)**: Replace `YOUR_SPLUNK_INTERNAL_IP` (the Splunk VM's **VPC-internal IP** — same VPC, no IAP tunnel) and `YOUR_SPLUNK_HEC_TOKEN` (the `Wazuh_Token`, routes to `ai_logs`) before starting the Wazuh container. The `<localfile>` uses a wildcard `*.json` so all target apps (incl. ml-api) are collected automatically.
