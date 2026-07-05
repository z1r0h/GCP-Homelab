# 02 — Firewall Rules & Cloud NAT

> 自定义 VPC 现在**一条防火墙规则都没有**(全部默认拒绝)。本页加上恰好够用的几条:
> ① IAP 给「人」进(SSH/RDP/Splunk Web),② VPC 内网让「机器」互联(HEC/UF/AD),③ Cloud NAT 让无公网 IP 的 VM 能出网装东西。
> 所有 VM 都 **不挂公网 IP**——这台 lab 装满漏洞靶机,绝不能暴露。

---

## 2.1 允许 IAP 入站(SSH / RDP / Splunk Web)

IAP 的流量都来自固定段 **`35.235.240.0/20`**。

```bash
# SSH(Linux:lab VM + Splunk VM)
gcloud compute firewall-rules create allow-iap-ssh \
  --network=security-lab-vpc --direction=INGRESS --action=ALLOW \
  --rules=tcp:22 --source-ranges=35.235.240.0/20 \
  --target-tags=ai-lab,splunk

# RDP(Windows:AD + Client)
gcloud compute firewall-rules create allow-iap-rdp \
  --network=security-lab-vpc --direction=INGRESS --action=ALLOW \
  --rules=tcp:3389 --source-ranges=35.235.240.0/20 \
  --target-tags=windows

# Splunk Web(经 IAP 隧道到 8000)
gcloud compute firewall-rules create allow-iap-splunkweb \
  --network=security-lab-vpc --direction=INGRESS --action=ALLOW \
  --rules=tcp:8000 --source-ranges=35.235.240.0/20 \
  --target-tags=splunk
```

## 2.2 允许 VPC 内网互联(机器对机器)

这条让同子网的 VM 互相通信:**Wazuh→Splunk HEC(8088)、Windows UF→Splunk(9997)、AD 域通信**等全靠它。

```bash
gcloud compute firewall-rules create allow-internal \
  --network=security-lab-vpc --direction=INGRESS --action=ALLOW \
  --rules=tcp:0-65535,udp:0-65535,icmp \
  --source-ranges=10.0.10.0/24
```
> 想更严格可拆成单端口规则(只放 8088/9997/53/88/389/445 等),但 lab 内网全放行更省事。**关键是 source 限定在子网段,绝不对 `0.0.0.0/0` 开放。**

## 2.3 Cloud NAT(无公网 IP 的 VM 靠它出网)

因为所有 VM 都 `--no-address`,装包 / 拉 Docker 镜像 / 下 Ollama 模型 / Windows 更新都需要 NAT 出网。

```bash
# 1) 建 Cloud Router
gcloud compute routers create security-lab-router \
  --network=security-lab-vpc --region=asia-southeast1

# 2) 在 Router 上建 NAT(自动分配出口 IP,覆盖全子网)
gcloud compute routers nats create security-lab-nat \
  --router=security-lab-router --region=asia-southeast1 \
  --auto-allocate-nat-external-ips --nat-all-subnet-ip-ranges
```

## 2.4 验证

```bash
gcloud compute firewall-rules list --filter="network:security-lab-vpc"
gcloud compute routers nats list --router=security-lab-router --region=asia-southeast1
```
应看到 3 条 IAP 规则 + 1 条 internal 规则 + 1 个 NAT。

> 🔒 **安全检查**:此时**没有任何规则**对 `0.0.0.0/0` 开放入站。靶机端口(5001-5005/3000/8081/8888/3333)既不在防火墙里、VM 也无公网 IP——只能从 VM 内 `localhost` 或经 IAP 端口转发访问。

---

➡️ 下一步:**[`03 — GPU Quota & Lab Spot VM`](<03 — GPU Quota & Lab Spot VM.md>)** — 申请 T4 配额并创建第一台 VM。
