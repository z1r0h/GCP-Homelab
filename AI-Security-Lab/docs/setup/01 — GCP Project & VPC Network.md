# 01 — GCP Project & VPC Network

> 从零开始的第一步:确定项目、启用 API、建一个**自定义 VPC + 子网**,后面所有 VM 都挂在它上面。
> 自定义 VPC(而非 default 网络)的好处:**没有任何自动开放的防火墙规则**,我们只加自己需要的(最小权限)。

---

## 1.1 选定项目并设为默认

```bash
gcloud config set project splunk-threat-detection-lab
gcloud config set compute/region asia-southeast1
gcloud config set compute/zone asia-southeast1-a
```
> Region 全系列固定为 `asia-southeast1`(新加坡),zone 固定为 `asia-southeast1-a`。
> 没有项目就先 `gcloud projects create splunk-threat-detection-lab` 并在 Console 关联结算账号(Billing)。

## 1.2 启用所需 API

```bash
gcloud services enable \
  compute.googleapis.com \
  iap.googleapis.com \
  oslogin.googleapis.com
```
| API | 用途 |
|-----|------|
| `compute` | 创建 VM / 网络 / 防火墙 |
| `iap` | Identity-Aware Proxy(零信任 SSH/RDP/隧道) |
| `oslogin` | 用 IAM 身份管理 SSH 登录(推荐) |

## 1.3 创建自定义 VPC 网络

```bash
gcloud compute networks create security-lab-vpc \
  --subnet-mode=custom \
  --bgp-routing-mode=regional
```
> `custom` 模式不会自动建子网,也**不带任何默认防火墙规则**——这正是我们要的干净起点。

## 1.4 创建子网

```bash
gcloud compute networks subnets create lab-subnet \
  --network=security-lab-vpc \
  --region=asia-southeast1 \
  --range=10.0.10.0/24 \
  --enable-private-ip-google-access
```
| 参数 | 为什么 |
|------|--------|
| `10.0.10.0/24` | 254 个可用内网 IP,4 台 VM + 扩展足够;全系列 HEC/UF 内网通信都在这一段 |
| `--enable-private-ip-google-access` | 让无公网 IP 的 VM 仍能访问 Google API(日志、镜像元数据等) |

## 1.5 验证

```bash
gcloud compute networks list
gcloud compute networks subnets list --filter="network:security-lab-vpc"
```
应看到 `security-lab-vpc` 和 `lab-subnet`(range `10.0.10.0/24`)。

---

➡️ 下一步:**[`02 — Firewall Rules & Cloud NAT`](<02 — Firewall Rules & Cloud NAT.md>)** — 加最小化防火墙 + 让 VM 能出网。
