# 13 — Cost Control & Spot Recovery

> 现在有 4 台 VM + Cloud NAT + 磁盘在跑,24/7 都计费。养成习惯别烧钱。

---

## 13.1 做完就停机(全部 VM)

```bash
# lab VM(Spot,停机磁盘保留)
gcloud compute instances stop cyber-ai-lab-vm --zone=asia-southeast1-a
# 不做实验时 Splunk / Windows 也停(Splunk 停了就收不到日志,按需停)
gcloud compute instances stop splunk-vm ad-dc-vm win-client-vm --zone=asia-southeast1-a
```
> 一条命令停多台:`gcloud compute instances stop A B C --zone=asia-southeast1-a`。
> Spot 停机后磁盘保留,下次 `start` 即恢复(不用重建)。

## 13.2 lab VM 自动关机(防忘关机)

```bash
# ⚠️ 若用 tmux/screen 挂后台长任务再断开 SSH,who 会变 0,5 分钟后会关机并杀掉任务。
#    跑长任务时先注释掉 crontab 这行。
cat << 'EOF' | sudo tee /usr/local/bin/auto-shutdown.sh
#!/bin/bash
if [ $(who | wc -l) -eq 0 ]; then
  up=$(awk '{print int($1/60)}' /proc/uptime)
  if [ $up -gt 30 ]; then sudo shutdown -h now "Auto-shutdown: no SSH sessions"; fi
fi
EOF
sudo chmod +x /usr/local/bin/auto-shutdown.sh
echo "*/5 * * * * /usr/local/bin/auto-shutdown.sh" | sudo crontab -
```

## 13.3 预算提醒
GCP Console → Billing → Budgets & alerts → 设 **$80/月**,在 50%/80%/100% 发邮件。

## 13.4 Spot 被抢占后恢复(仅 lab VM)

```bash
# 被抢占后实例处于 TERMINATED/STOPPED,磁盘还在。重新启动:
gcloud compute instances start cyber-ai-lab-vm --zone=asia-southeast1-a
# Spot 资源紧张时启动可能失败,等几分钟再试;或临时改 on-demand:
#   去掉 --provisioning-model=SPOT 重建(贵 ~2x,零抢占)
```

## 13.5 成本粗估(asia-southeast1, ~2-3hr/天)
> ⚠️ `asia-southeast1`(新加坡)价格通常比 `us-central1` 高 ~10-20%,下表是粗略量级,请以 [GCP 官方计算器](https://cloud.google.com/products/calculator) 为准。

| 资源 | 计费方式 | 粗估 |
|------|---------|------|
| `cyber-ai-lab-vm`(Spot n1-std-8+T4) | 用时计费 | ~$35-40/月 |
| `splunk-vm`(e2-std-4) | 用时计费 | 看常驻时长 |
| `ad-dc-vm` + `win-client-vm`(e2-std-2 ×2,含 Windows license) | 用时计费 | 仅做 17/18 时开,用完即停 |
| 4 块 pd-balanced 磁盘(lab 150GB + Splunk 100GB + Windows 80GB×2) | **常驻**计费 | ~$40-45/月(停机也算) |
| Cloud NAT | 网关 + 流量 | 几美元/月 |

> 💡 省钱关键:**磁盘是常驻成本**,长期不用的 VM 可以删(先 `gcloud compute images create` 留个镜像或导出),只留磁盘也要钱。Windows 两台用完务必停。

---

🎉 **全部 setup 完成(从空项目到 4 台 VM 全链路打通)。**
- 索引导航:[`00 — Overview`](<00 — Overview.md>)
- 理解整个 lab:`LAB_MANUAL_PRIVATE.md`、`walkthrough.md`
- 开始实验:`docs/SCENARIOS_GUIDE.md`
