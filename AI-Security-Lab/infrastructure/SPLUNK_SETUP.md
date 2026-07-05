# ☁️ Splunk Setup — 索引

> Splunk VM 与 lab VM **同 VPC**、内网直连（10GB Developer License）。**从零创建**也已纳入 setup 系列。
> 完整步骤见 **`docs/setup/`**：

- [`04 — Splunk VM`](../docs/setup/<04 — Splunk VM.md>)
  — 创建 Splunk VM + 安装 Splunk Enterprise + 记内网 IP
- [`08 — Splunk Setup (Indexes, HEC, Add-ons)`](../docs/setup/<08 — Splunk Setup (Indexes, HEC, Add-ons).md>)
  — License 省量、Add-ons、**7 个规范索引**、HEC Tokens（`Wazuh_Token`→`ai_logs` / `ML_Token`→`ml_alerts`）、UF 接收口
- [`10 — Wazuh & Log Pipeline`](../docs/setup/<10 — Wazuh & Log Pipeline.md>)
  — ossec `hook_url` 填 Splunk **内网 IP** + Token、VPC 防火墙放行 8088、日志管道
- [`06 — Connecting via IAP`](../docs/setup/<06 — Connecting via IAP.md>) — 从公司电脑看 Splunk Web

> **关键**：HEC 走 VPC 内网直连，**不用 IAP 隧道**；hook_url 填内网 IP（不是公网、不是 host.docker.internal）。
