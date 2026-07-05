# 00 — Setup Overview

> 全 GCP 版 AI 攻防实验室的搭建导航。**本系列假设你从一个空的 GCP 项目开始,什么 VM 都还没有**——
> 从 VPC 网络 → 防火墙 → Cloud NAT → 4 台 VM → 接入 → 逐机配置 → 点火,一步步建起来。
> 整个 lab 的核心计算跑在一台 **GCP Spot VM (NVIDIA T4)**,与 **Splunk VM 同 VPC**——日志走内网直连,无 IAP HEC 隧道。

## 🗺️ 全局拓扑(建完后长这样)

| VM | 机型 | 角色 | 外网 IP | Tag |
|----|------|------|:------:|-----|
| `cyber-ai-lab-vm` | n1-standard-8 + T4 (Spot) | Docker 全栈 + Ollama(靶机/红队/蓝队容器都在这) | ❌ | `ai-lab` |
| `splunk-vm` | e2-standard-4 | Splunk Enterprise(中央 SIEM + HEC) | ❌ | `splunk` |
| `ad-dc-vm` | e2-standard-2 (Windows) | Active Directory 域控(场景 17/18) | ❌ | `windows` |
| `win-client-vm` | e2-standard-2 (Windows) | 域内客户端 + Sysmon(场景 17/18) | ❌ | `windows` |

> 全部 **无公网 IP**,纯靠 IAP(人)+ Cloud NAT(出网)+ VPC 内网(机器互联)。

## 📋 按顺序走这 13 步

| # | 步骤 | 做什么 |
|---|------|--------|
| [01](<01 — GCP Project & VPC Network.md>) | GCP Project & VPC Network | 选项目、启 API、建自定义 VPC + 子网 |
| [02](<02 — Firewall Rules & Cloud NAT.md>) | Firewall Rules & Cloud NAT | 最小化防火墙(IAP/内网)+ Cloud NAT 出网 |
| [03](<03 — GPU Quota & Lab Spot VM.md>) | GPU Quota & Lab Spot VM | 申请抢占式 T4 配额 + 创建 lab VM |
| [04](<04 — Splunk VM.md>) | Splunk VM | 创建 Splunk VM + 安装 Splunk Enterprise |
| [05](<05 — Windows AD & Client VMs.md>) | Windows AD & Client VMs | 创建域控 + 客户端两台 Windows VM |
| [06](<06 — Connecting via IAP.md>) | Connecting via IAP | SSH / RDP / 看 Splunk Web,全经 IAP |
| [07](<07 — Lab VM Init (Docker, GPU, Ollama).md>) | Lab VM Init | 装 Docker / NVIDIA Toolkit / Ollama、拉模型、克隆代码 |
| [08](<08 — Splunk Setup (Indexes, HEC, Add-ons).md>) | Splunk Setup | 7 个规范索引、HEC Token、Add-ons |
| [09](<09 — Windows Config (AD, Sysmon, UF).md>) | Windows Config | 提升域控、客户端入域、装 Sysmon + Universal Forwarder |
| [10](<10 — Wazuh & Log Pipeline.md>) | Wazuh & Log Pipeline | ossec 填内网 IP+Token、共享卷管道 |
| [11](<11 — Igniting the Lab.md>) | Igniting the Lab | `start_lab.sh` 点火 + wazuh-logtest 验证闭环 |
| [12](<12 — VM Backup & Recovery.md>) | VM Backup & Recovery | 配好后拍 baseline 快照 + 一键恢复(`recover_vm.sh`) |
| [13](<13 — Cost Control & Spot Recovery.md>) | Cost Control & Spot Recovery | 停机、自动关机、预算、抢占恢复 |

> 💡 **最短路径**:只想跑 AI 靶机 + Splunk 检测(场景 01–16、19–23)的话,**01→04、06→08、10→13** 即可,
> 第 05、09 步(两台 Windows VM)只有 AD/MFA 紫队场景(17/18)才需要,可以以后再建。

## 数据流一句话
```
红队/Kali 打靶机 → 靶机写 /var/log/ai-lab/*.json → Wazuh 读 → 同 VPC 内网直发 Splunk HEC (index=ai_logs)
Windows(AD/Client)→ Sysmon/WinEventLog → Universal Forwarder → Splunk (9997)
你经 IAP:SSH 进 Linux VM / RDP 进 Windows VM / 浏览器看 Splunk Web
```

## 占位符约定(全系列统一)
| 占位符 | 含义 | 示例 |
|--------|------|------|
| `YOUR_SPLUNK_INTERNAL_IP` | Splunk VM 的 VPC 内网 IP | `10.0.10.4` |
| `YOUR_SPLUNK_HEC_TOKEN` | Splunk HEC Token | `Wazuh_Token` 的值 |

> 全系列固定使用:项目 `splunk-threat-detection-lab`、region `asia-southeast1`、zone `asia-southeast1-a`、
> VPC `security-lab-vpc`、子网 `lab-subnet`(`10.0.10.0/24`)。

## 相关文档
- **理解整个 lab**:根目录 `walkthrough.md`(白话图解)、`LAB_MANUAL_PRIVATE.md`(百科全书)
- **23 个实验场景**:`docs/SCENARIOS_GUIDE.md`
