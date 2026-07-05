# 03 — GPU Quota & Lab Spot VM

> 创建实验室的核心:一台 **Spot VM (NVIDIA T4)**,跑整个 Docker 栈 + Ollama。先申请配额,再建 VM。
> 网络/防火墙/NAT 已在 `01`-`02` 建好,这里 VM 直接挂到 `security-lab-vpc`。

---

## 3.1 申请 GPU 配额(最关键,可能等 1-2 天)

GCP 新账号默认 GPU 配额 = 0。

> ⚠️ **Spot 用的是「抢占式 GPU」配额,和按需的是两个不同配额。**
> 跑 Spot 必须申请 **`PREEMPTIBLE_NVIDIA_T4_GPUS`**(不是 `NVIDIA_T4_GPUS`)。两个都申请最稳。

1. GCP Console → **IAM & Admin → Quotas & System Limits**
2. Filter 搜 `PREEMPTIBLE_NVIDIA_T4_GPUS`,选 `asia-southeast1` 条目
3. **EDIT QUOTAS** → New limit `1` → 描述写 *"Personal AI/ML security lab, 1x T4 for local LLM inference on a Spot VM"*
4. Submit,等邮件(几分钟到 2 个工作日)

## 3.2 确认 Spot + T4 在你的 Region 可用

```bash
gcloud compute accelerator-types list --filter="name=nvidia-tesla-t4" --format="table(zone,name)"
```
确认 `asia-southeast1-a` 在列表里(T4 在新加坡区通常 a/b/c 都有)。

## 3.3 创建 Spot VM

```bash
gcloud compute instances create cyber-ai-lab-vm \
  --project=splunk-threat-detection-lab \
  --zone=asia-southeast1-a \
  --machine-type=n1-standard-8 \
  --provisioning-model=SPOT \
  --instance-termination-action=STOP \
  --accelerator=type=nvidia-tesla-t4,count=1 \
  --maintenance-policy=TERMINATE \
  --boot-disk-size=150GB \
  --boot-disk-type=pd-balanced \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --network=security-lab-vpc \
  --subnet=lab-subnet \
  --no-address \
  --tags=ai-lab \
  --scopes=default
```

| 参数 | 为什么 |
|------|--------|
| `n1-standard-8` | 8 vCPU/30GB;更省可先试 `n1-standard-4` |
| `SPOT` + `STOP` | 便宜 60-70%;被抢占=停机不删,磁盘保留,start 即恢复 |
| `pd-balanced 150GB` | 比 pd-ssd 便宜 ~40%(磁盘 24/7 计费);150GB 给镜像/模型/构建缓存留足余量(+50GB ≈ +$5/月) |
| 干净 `ubuntu-2204-lts` | 镜像小、启动快;NVIDIA 驱动在 `07` 手动装(stock 镜像不会自动装驱动,DL 镜像那一堆 ML 框架我们用不到) |
| `--network/--subnet` | 挂到 `01` 建的自定义 VPC |
| `--no-address` | ⚠️ 安全关键:这机器装满漏洞靶机,**绝不挂公网**,纯 IAP 访问;出网靠 `02` 的 Cloud NAT |
| `--tags=ai-lab` | 匹配 `02` 的 `allow-iap-ssh` 规则 |

> 💡 **想省去手动装驱动**?也可改用预装驱动的 Deep Learning VM 镜像——但 family 名会随版本变,先查最新再填:
> ```bash
> gcloud compute images list --project=deeplearning-platform-release \
>   --filter="family:common-cu* AND name:ubuntu-2204" --sort-by=~creationTimestamp --limit=3
> ```
> 把第一个结果的 `family` 填进 `--image-family`、`--image-project=deeplearning-platform-release`,
> 并加 `--metadata=install-nvidia-driver=True`(**仅 DL 镜像会读这个 metadata**;stock Ubuntu 上它无效)。
> 代价:镜像大、启动慢、占盘多。本 lab 推荐上面的干净 Ubuntu。

## 3.4 验证

```bash
gcloud compute instances list --filter="name=cyber-ai-lab-vm"
```
状态 `RUNNING`、`EXTERNAL_IP` 为空即正确。**先别急着配置**——其余 VM 一起建完再统一接入(见 `06`)。

---

➡️ 下一步:**[`04 — Splunk VM`](<04 — Splunk VM.md>)** — 创建并安装 Splunk Enterprise。
