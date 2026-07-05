# 12 — VM Backup & Recovery

> 整个环境装好、配好、`11` 验证闭环通过之后,**给每台 VM 的启动盘拍一张 baseline 快照**。
> 这张快照 = "出厂镜像":以后任何 VM 被搞坏 / 被抢占丢失 / 为省钱删掉,都能用**一条命令**从 baseline 复原,
> 不用重走 `01`-`10` 的安装配置。

---

## 12.1 为什么用 baseline 快照

| 场景 | 没有 baseline | 有 baseline |
|------|--------------|------------|
| lab VM 被玩坏(靶机 RCE 污染了系统) | 重装 Docker/Ollama/克隆代码…重来 | `recover_vm.sh` 一键回到干净态 |
| 想省钱**彻底删掉** idle VM(磁盘也不留) | 不敢删,磁盘 24/7 烧钱 | 放心删,要用时一键重建 |
| Spot 磁盘损坏 / 误删 | 全部重做 | 从快照恢复 |

> 快照是**增量、压缩、全局**资源,很便宜(只存变化块)。删掉源 VM 后快照仍在。

## 12.2 拍 baseline 快照(`11` 通过后做)

为拿到一致的磁盘状态,**先停机再拍**(crash-consistent,最稳):

```bash
# 1) 停掉要拍的 VM(磁盘名默认 == 实例名)
gcloud compute instances stop cyber-ai-lab-vm splunk-vm --zone=asia-southeast1-a

# 2) 给每个启动盘拍 baseline 快照(命名规范 baseline-<vm>,recover 脚本依赖这个名字)
gcloud compute disks snapshot cyber-ai-lab-vm --zone=asia-southeast1-a \
  --snapshot-names=baseline-cyber-ai-lab-vm \
  --description="Fully configured lab VM baseline"
gcloud compute disks snapshot splunk-vm --zone=asia-southeast1-a \
  --snapshot-names=baseline-splunk-vm \
  --description="Configured Splunk VM baseline"

# 3) (做了第 05/09 步才有)两台 Windows VM 也拍
gcloud compute instances stop ad-dc-vm win-client-vm --zone=asia-southeast1-a
gcloud compute disks snapshot ad-dc-vm     --zone=asia-southeast1-a --snapshot-names=baseline-ad-dc-vm
gcloud compute disks snapshot win-client-vm --zone=asia-southeast1-a --snapshot-names=baseline-win-client-vm
```

> ⚠️ **命名很重要**:快照必须叫 `baseline-<实例名>`,`scripts/recover_vm.sh` 按这个规则找快照。
> 重新拍新基线时,先删旧的同名快照,或换个名字并改脚本里的 `SNAP` 规则。

## 12.3 (可选)每日自动快照

给磁盘挂一个快照计划(resource policy),自动滚动备份、保留 7 天:

```bash
gcloud compute resource-policies create snapshot-schedule daily-lab-snap \
  --region=asia-southeast1 --max-retention-days=7 \
  --daily-schedule --start-time=18:00 \
  --on-source-disk-delete=keep-auto-snapshots

gcloud compute disks add-resource-policies cyber-ai-lab-vm \
  --zone=asia-southeast1-a --resource-policies=daily-lab-snap
```
> baseline(手动、长期保留)和 daily(自动、滚动 7 天)互补:baseline 是"已知好状态",daily 是"最近的进度"。

## 12.4 ⚡ One-Command Recovery

本仓库自带 [`scripts/recover_vm.sh`](../../scripts/recover_vm.sh):给它一个 VM 名,它会从 `baseline-<vm>` 快照
**重建启动盘 + 重建实例**(自动套用正确的机型 / GPU / Spot / 网络 / tag,与 setup 创建命令一致)。

```bash
# 在任何 gcloud 已登录的地方运行(Cloud Shell 或你的电脑):
bash scripts/recover_vm.sh cyber-ai-lab-vm asia-southeast1-a
# 其它:
bash scripts/recover_vm.sh splunk-vm     asia-southeast1-a
bash scripts/recover_vm.sh ad-dc-vm      asia-southeast1-a
bash scripts/recover_vm.sh win-client-vm asia-southeast1-a
```
脚本做的事:① 若实例还在 → 询问后删除;② 删掉残留同名磁盘;③ 从 `baseline-<vm>` 建盘;④ 用该盘重建实例(`--no-address`、同 VPC/子网、原 tag)。完成后照常经 IAP(`06`)连进去即可。

> 恢复后:lab VM 的 NVIDIA 驱动 / Docker / Ollama / 代码都在快照里,**无需重装**;直接 `bash scripts/start_lab.sh` 点火。

## 12.5 省钱玩法:删掉 → 需要时恢复

因为有 baseline,长期不用的 VM 可以**整台删掉**(连磁盘),省下常驻磁盘费:

```bash
gcloud compute instances delete win-client-vm ad-dc-vm --zone=asia-southeast1-a --quiet   # 磁盘一起删
# 下次做紫队场景(17/18)时:
bash scripts/recover_vm.sh ad-dc-vm asia-southeast1-a
bash scripts/recover_vm.sh win-client-vm asia-southeast1-a
```
> 快照存储费远低于常驻 SSD/balanced 磁盘费——idle 期间删 VM 留快照是最省的姿势。详见 `13`。

## 12.6 验证

```bash
gcloud compute snapshots list --filter="name~baseline-"
```
应列出每台 VM 的 `baseline-*` 快照。

---

➡️ 下一步:**[`13 — Cost Control & Spot Recovery`](<13 — Cost Control & Spot Recovery.md>)**
