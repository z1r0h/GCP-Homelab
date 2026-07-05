# 🖥️ Lab VM Setup — 索引

> 本实验室运行在一台 **GCP Spot VM (n1-standard-8 + NVIDIA T4, 干净 Ubuntu 22.04 LTS,驱动手动装)**，
> 与 Splunk VM **同 VPC**。完整步骤见 **`docs/setup/`**：

- [`01 — GCP Project & VPC Network`](../docs/setup/<01 — GCP Project & VPC Network.md>) — 自定义 VPC + 子网
- [`02 — Firewall Rules & Cloud NAT`](../docs/setup/<02 — Firewall Rules & Cloud NAT.md>) — 最小化防火墙 + NAT 出网
- [`03 — GPU Quota & Lab Spot VM`](../docs/setup/<03 — GPU Quota & Lab Spot VM.md>) — 配额 + 创建 lab VM
- [`07 — Lab VM Init`](../docs/setup/<07 — Lab VM Init (Docker, GPU, Ollama).md>) — Docker / GPU / Ollama / 克隆代码
- [`11 — Igniting the Lab`](../docs/setup/<11 — Igniting the Lab.md>) — `start_lab.sh` 启动

## Docker 隔离网络（compose 自动创建，勿手动建）
| 网络 | 子网 | 谁在里面 |
|------|------|---------|
| `blue-net` | 10.10.10.0/24 | Wazuh |
| `red-net` | 10.10.20.0/24 | Kali, CALDERA, GoPhish |
| `target-net` | 10.10.30.0/24 | 全部靶机 + ml-api + DVWA + Juice Shop + Kali + Wazuh + CALDERA |
| `ai-net` | 10.10.40.0/24 | AI 靶机经 `host.docker.internal` 访问宿主机 Ollama |
