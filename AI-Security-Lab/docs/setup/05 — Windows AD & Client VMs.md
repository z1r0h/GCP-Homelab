# 05 — Windows AD & Client VMs

> **可选 / 紫队专用**:只有场景 **17(Purple Team AD)** 和 **18(MFA & 凭证攻击)** 需要这两台 Windows VM。
> 只做 AI 靶机场景(01–16、19–23)可以跳过本页,以后要做 AD 时再回来建。
> ⚠️ Windows 镜像带 **许可证费用**(比同规格 Linux 贵),做完记得停机(见 `12`)。

---

## 5.1 创建域控 VM(AD DC)

```bash
gcloud compute instances create win-dc \
  --project=splunk-threat-detection-lab \
  --zone=asia-southeast1-a \
  --machine-type=e2-standard-2 \
  --boot-disk-size=50GB \
  --boot-disk-type=pd-balanced \
  --image-family=windows-2022 \
  --image-project=windows-cloud \
  --network=security-lab-vpc \
  --subnet=lab-subnet \
  --no-address \
  --tags=windows \
  --private-network-ip=10.0.10.20 \
  --scopes=default
```

## 5.2 创建客户端 VM(域成员 + Sysmon)

```bash
gcloud compute instances create win-client \
  --project=splunk-threat-detection-lab \
  --zone=asia-southeast1-a \
  --machine-type=e2-standard-2 \
  --boot-disk-size=50GB \
  --boot-disk-type=pd-balanced \
  --image-family=windows-2022 \
  --image-project=windows-cloud \
  --network=security-lab-vpc \
  --subnet=lab-subnet \
  --no-address \
  --tags=windows \
  --private-network-ip=10.0.10.30 \
  --scopes=default
```

> 想用 Windows 10/11 客户端镜像也行(`--image-family=windows-11-...`,需对应 license)。Server 2022 当客户端最省事。

## 5.3 设置 Windows 管理员密码(用于 RDP)

```bash
gcloud compute reset-windows-password win-dc --zone=asia-southeast1-a --user=labadmin
gcloud compute reset-windows-password win-client --zone=asia-southeast1-a --user=labadmin
```
记下两台返回的密码。

## 5.4 记下两台的内网 IP

```bash
gcloud compute instances list --filter="tags.items=windows" \
  --format="table(name,networkInterfaces[0].networkIP)"
```
域控的内网 IP 后面要当客户端的 DNS。

## 5.5 验证

```bash
gcloud compute instances list --filter="tags.items=windows"
```
两台 `RUNNING`、无外网 IP 即对。

> **提升域控、客户端入域、装 Sysmon + Universal Forwarder 等系统内配置留到 [`09 — Windows Config`](<09 — Windows Config (AD, Sysmon, UF).md>)**(那时 Splunk 已配好 HEC/UF 接收,可一次接通)。

---

➡️ 下一步:**[`06 — Connecting via IAP`](<06 — Connecting via IAP.md>)** — 连进全部 VM 开始配置。
