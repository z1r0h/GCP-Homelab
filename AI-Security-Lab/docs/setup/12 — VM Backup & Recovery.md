# 12 — VM Backup & Recovery

> 整个环境装好、配好、`11` 验证闭环通过之后,**给每台 VM 拍一张 baseline machine image**。
> 这张 image = "出厂镜像":以后任何 VM 被搞坏 / 被抢占丢失 / 为省钱删掉,都能用**一条命令**从 baseline 完整复原
> (机型、GPU、网络、tag 全部自动带回来,不用重走 `01`-`11` 的安装配置)。

---

## 12.1 为什么用 machine image,不用 disk snapshot

| | Disk Snapshot | Machine Image |
|---|---|---|
| 存的内容 | 只有磁盘数据 | 磁盘数据 **+ 机型/GPU/网络/tag/服务账号等整机配置** |
| 恢复方式 | 建盘 → 还要手动重新指定机型/GPU/网络/tag 建实例,容易跟当初 `create` 用的参数对不上 | **一条命令** `gcloud compute instances create --source-machine-image=...` 整机复原 |
| 定时自动备份 | ✅ 支持(`resource-policies snapshot-schedule`) | ❌ 不支持定时,只能手动建 |

结论:**baseline(本页主角)用 machine image**——一次配好、以后一条命令整机复原,尤其省心的是 lab VM 那个
Spot + T4 GPU 实例,机型/加速器这些参数不用再手动对一遍。**日常自动滚动备份(12.3)继续用 disk snapshot**,
因为 machine image 没有定时功能,这块没法替代。

| 场景 | 没有 baseline | 有 baseline |
|------|--------------|------------|
| lab VM 被玩坏(靶机 RCE 污染了系统) | 重装 Docker/Ollama/克隆代码…重来 | `recover_vm.sh` 一键回到干净态 |
| 想省钱**彻底删掉** idle VM(磁盘也不留) | 不敢删,磁盘 24/7 烧钱 | 放心删,要用时一键重建 |
| Spot 磁盘损坏 / 误删 | 全部重做 | 从 image 恢复 |

## 12.2 拍 baseline machine image(`11` 通过后做)

为拿到一致的磁盘状态,**先停机再拍**(crash-consistent,最稳):

```bash
# 1) 停掉要拍的 VM
gcloud compute instances stop cyber-ai-lab-vm splunk-server --zone=asia-southeast1-a

# 2) 给每台 VM 建 baseline machine image(命名规范 baseline-<vm>,recover 脚本依赖这个名字)
gcloud compute machine-images create baseline-cyber-ai-lab-vm \
  --source-instance=cyber-ai-lab-vm --source-instance-zone=asia-southeast1-a \
  --description="Fully configured lab VM baseline"
gcloud compute machine-images create baseline-splunk-server \
  --source-instance=splunk-server --source-instance-zone=asia-southeast1-a \
  --description="Configured Splunk VM baseline"

# 3) (做了第 05/09 步才有)两台 Windows VM 也拍
gcloud compute instances stop win-dc win-client --zone=asia-southeast1-a
gcloud compute machine-images create baseline-win-dc \
  --source-instance=win-dc --source-instance-zone=asia-southeast1-a
gcloud compute machine-images create baseline-win-client \
  --source-instance=win-client --source-instance-zone=asia-southeast1-a
```

> ⚠️ **命名很重要**:image 必须叫 `baseline-<实例名>`,`scripts/recover_vm.sh` 按这个规则找 image。
> 重新拍新基线时,先删旧的同名 image(`gcloud compute machine-images delete baseline-<vm>`),
> 或换个名字并改脚本里的 `IMAGE` 规则。

## 12.3 (可选)每日自动磁盘快照

Machine image 没有定时功能,日常"最近进度"的滚动备份还是用 disk snapshot + resource policy:

```bash
gcloud compute resource-policies create snapshot-schedule daily-lab-snap \
  --region=asia-southeast1 --max-retention-days=7 \
  --daily-schedule --start-time=18:00 \
  --on-source-disk-delete=keep-auto-snapshots

gcloud compute disks add-resource-policies cyber-ai-lab-vm \
  --zone=asia-southeast1-a --resource-policies=daily-lab-snap
```
> baseline(手动、machine image、长期保留)和 daily(自动、disk snapshot、滚动 7 天)互补:
> baseline 是"已知好状态",daily 是"最近的进度"。

## 12.4 ⚡ One-Command Recovery

本仓库自带 [`scripts/recover_vm.sh`](../../scripts/recover_vm.sh):给它一个 VM 名,它会直接用
`baseline-<vm>` machine image **一条命令重建整台实例**——机型、GPU、网络、tag 全部从 image 里自动带回来,
不用像以前维护 disk snapshot 那样单独记一份"每台 VM 的机型/GPU 对照表"。

```bash
# 在任何 gcloud 已登录的地方运行(Cloud Shell 或你的电脑):
bash scripts/recover_vm.sh cyber-ai-lab-vm asia-southeast1-a
# 其它:
bash scripts/recover_vm.sh splunk-server     asia-southeast1-a
bash scripts/recover_vm.sh win-dc      asia-southeast1-a
bash scripts/recover_vm.sh win-client asia-southeast1-a
```
脚本做的事:① 若实例还在 → 询问后删除;② 从 `baseline-<vm>` machine image 一条命令重建实例
(机型/GPU/网络/tag/no-address 全部继承自 image,无需再指定)。完成后照常经 IAP(`06`)连进去即可。

> 恢复后:lab VM 的 NVIDIA 驱动 / Docker / Ollama / 代码都在 image 里,**无需重装**;直接 `bash scripts/start_lab.sh` 点火。

## 12.5 省钱玩法:删掉 → 需要时恢复

因为有 baseline machine image,长期不用的 VM 可以**整台删掉**(连磁盘),省下常驻磁盘费——
machine image 是独立资源,不依赖原磁盘/实例是否还存在:

```bash
gcloud compute instances delete win-client win-dc --zone=asia-southeast1-a --quiet   # 磁盘一起删
# 下次做紫队场景(17/18)时:
bash scripts/recover_vm.sh win-dc asia-southeast1-a
bash scripts/recover_vm.sh win-client asia-southeast1-a
```
> Machine image 存储费跟 snapshot 同一量级、远低于常驻 SSD/balanced 磁盘费——idle 期间删 VM 留 image 是最省的姿势。详见 `13`。

## 12.6 验证

```bash
gcloud compute machine-images list --filter="name~baseline-"
```
应列出每台 VM 的 `baseline-*` machine image。

---

➡️ 下一步:**[`13 — Cost Control & Spot Recovery`](<13 — Cost Control & Spot Recovery.md>)**
