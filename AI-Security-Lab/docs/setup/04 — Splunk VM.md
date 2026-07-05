# 04 — Splunk VM

> 中央 SIEM。创建一台普通 Ubuntu VM 并安装 **Splunk Enterprise(免费 Developer License,10GB/天)**。
> 它与 lab VM **同 VPC 同子网**,所以 Wazuh 后面走**内网直连**发 HEC,不需要任何隧道。

---

## 4.1 创建 Splunk VM

```bash
gcloud compute instances create splunk-server \
  --project=splunk-threat-detection-lab \
  --zone=asia-southeast1-a \
  --machine-type=e2-standard-4 \
  --boot-disk-size=50GB \
  --boot-disk-type=pd-balanced \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --network=security-lab-vpc \
  --subnet=lab-subnet \
  --no-address \
  --tags=splunk \
  --scopes=default \
  --private-network-ip=10.0.10.10
```

| 参数 | 为什么 |
|------|--------|
| `e2-standard-4` | 4 vCPU/16GB;**MLTK 机器学习 App 要求 ≥8GB RAM**,16GB 稳。预算紧可用 `e2-standard-2`(8GB),但 MLTK 场景就改在 lab VM 本地 Jupyter 跑 |
| `--no-address` + `--tags=splunk` | 无公网,经 IAP 访问;tag 匹配 `02` 的 `allow-iap-ssh` / `allow-iap-splunkweb` |
| 不要 Spot | Splunk 是常驻 SIEM,被抢占会丢采集;用按需(on-demand) |

## 4.2 记下 Splunk VM 的内网 IP(后面 Wazuh/UF 要用)

```bash
gcloud compute instances describe splunk-server --zone=asia-southeast1-a \
  --format="get(networkInterfaces[0].networkIP)"
# 输出形如 10.0.10.10 —— 这就是全系列的 YOUR_SPLUNK_INTERNAL_IP
```

## 4.3 安装 Splunk Enterprise

先经 IAP SSH 进去(详见 `06`,这里直接用):
```bash
gcloud compute ssh splunk-server --zone=asia-southeast1-a --tunnel-through-iap
```

VM 内执行:
```bash
# Download Splunk (check splunk.com for the current version/build string)
wget -O splunk.deb \
  "https://download.splunk.com/products/splunk/releases/10.4.0/linux/splunk-10.4.0-f798d4d49089-linux-amd64.deb"

# Install (extracts to /opt/splunk)
sudo dpkg -i splunk.deb

# Create the dedicated splunk user (best practice — do NOT run as root)
sudo useradd -m splunk
sudo chown -R splunk:splunk /opt/splunk

# First start as the splunk user — accepts license and creates the admin account
sudo -u splunk /opt/splunk/bin/splunk start --accept-license

# Stop it again so we can enable boot-start under systemd
sudo -u splunk /opt/splunk/bin/splunk stop

# Enable boot-start as a systemd service owned by the splunk user
sudo /opt/splunk/bin/splunk enable boot-start -user splunk -systemd-managed 1

# Start via systemd and check status
sudo systemctl start Splunkd
sudo systemctl status Splunkd
```

## 4.4 选择 Developer License(10GB/天)

1. 经 IAP 隧道开 Splunk Web(见 `06`):`https://localhost:8000`,用上面的管理员账号登录。
2. **Settings → Licensing → Change license group → Free / Developer**(或导入你的 Developer License 文件)。
3. 重启 Splunk 使生效:`sudo /opt/splunk/bin/splunk restart`。

> 索引、HEC Token、Add-ons 等**留到 `08 — Splunk Setup`** 统一配置(那时 lab VM 已就绪,可端到端验证)。

## 4.5 验证

```bash
sudo /opt/splunk/bin/splunk status     # 应显示 splunkd is running
```

---

➡️ 下一步:**[`05 — Windows AD & Client VMs`](<05 — Windows AD & Client VMs.md>)**
> 只跑 AI 靶机场景的话可**跳过 05**,直接去 [`06 — Connecting via IAP`](<06 — Connecting via IAP.md>)。
