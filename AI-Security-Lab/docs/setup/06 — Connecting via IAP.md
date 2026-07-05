# 06 — Connecting via IAP

> 4 台 VM 都没有公网 IP。你从公司电脑用 **GCP IAP**(零信任入口)连进去:Linux 走 SSH、Windows 走 RDP、Splunk Web 走隧道。
> **日志转发(Wazuh→Splunk HEC、UF→Splunk)走 VPC 内网,不经 IAP**——IAP 只给你「人」用。

---

## 6.1 SSH 进 Linux VM(lab + Splunk)

```bash
gcloud compute ssh cyber-ai-lab-vm --zone=asia-southeast1-a --tunnel-through-iap
gcloud compute ssh splunk-server       --zone=asia-southeast1-a --tunnel-through-iap
```


## 6.2 RDP 进 Windows VM(AD + Client,仅做了第 05 步才有)

```bash
# 开一条到 3389 的 IAP 隧道并保持运行:
gcloud compute start-iap-tunnel win-dc 3389 --local-host-port=localhost:13389 --zone=asia-southeast1-a
# 另开一个终端连客户端(换本地端口避免冲突):
gcloud compute start-iap-tunnel win-client 3389 --local-host-port=localhost:13390 --zone=asia-southeast1-a
```
然后用 Windows「远程桌面连接(mstsc)」连 `localhost:3389` / `localhost:3390`,账号 `labadmin` + 第 05 步的密码。


## 6.3 看 Splunk Web 面板

在公司电脑开一条隧道并保持运行:
```bash
gcloud compute start-iap-tunnel splunk-server 8000 --local-host-port=localhost:8000 --zone=asia-southeast1-a
# 浏览器开 https://localhost:8000
```

## 6.4 (可选)在浏览器看靶机

比如看 Juice Shop(靶机端口不对外开放,用 IAP 转发到 lab VM):
```bash
gcloud compute start-iap-tunnel cyber-ai-lab-vm 3000 --local-host-port=localhost:3000 --zone=asia-southeast1-a
```

---

## ⚠️ 关键区别(相对本地 Windows 版)
- **HEC(8088)/ UF(9997)不用隧道**:VM 之间同 VPC,直接走内网 IP。
- 因此**没有** `host.docker.internal:8088` / `0.0.0.0:8088` 绑定那些坑。
- IAP 仅用于:① SSH 进 Linux ② RDP 进 Windows ③ 看 Splunk Web ④ 偶尔转发靶机端口到浏览器。

➡️ 下一步:**[`07 — Lab VM Init`](<07 — Lab VM Init (Docker, GPU, Ollama).md>)** — 配置 lab VM。
