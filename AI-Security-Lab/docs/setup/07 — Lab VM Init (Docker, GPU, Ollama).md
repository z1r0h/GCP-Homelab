# 07 — Lab VM Init (Docker, GPU, Ollama)

> SSH 进 **cyber-ai-lab-vm** 后**执行一次**。我们用的是干净 `ubuntu-2204-lts`,所以 NVIDIA 驱动和 Docker 都要自己装(下面命令幂等,缺啥补啥)。
> SSH 方法见 `06 — Connecting via IAP`。

---

## 7.1 装 NVIDIA 驱动 + 验证 GPU

stock Ubuntu 不带 GPU 驱动(这是选干净镜像的代价,换来小体积 / 快启动)。装驱动:

```bash
sudo apt-get update
sudo apt-get install -y ubuntu-drivers-common
sudo ubuntu-drivers install     # 自动选匹配 T4 的驱动版本
sudo reboot                     # 装完重启使驱动加载
```
重启后重新 SSH 进来验证:
```bash
nvidia-smi          # 应看到 Tesla T4, 16GB
```
> Ollama 只需要**驱动**(它自带 CUDA 运行时),**不用**单独装 CUDA Toolkit。

## 7.2 Docker(stock Ubuntu 需自己装)
```bash
# --- Docker 安装 --- 
# 原因：apt 默认源没有 docker-compose-plugin，改用官方脚本
# 1. 先清理可能存在的旧包（保险起见）
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do
  sudo apt-get remove -y $pkg 2>/dev/null
done

# 2. 官方一键脚本
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 3. 加入 docker 组
sudo usermod -aG docker $USER
newgrp docker
# 免 sudo 跑 docker

# 4. 验证（注意 compose 命令是空格,不是连字符）
docker --version
docker compose version
docker run hello-world
```

## 7.3 NVIDIA Container Toolkit(让 Docker 用 GPU)

```bash
# --- NVIDIA Container Toolkit --- 
# 目的：让 Docker 容器能用宿主机的 T4 GPU 
# 前提：nvidia-smi 先确认驱动已装好（本机 595.71.05, CUDA 13.2） 
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \ | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg 

curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \ | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \ 
| sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list sudo apt-get update 
# ⚠️ 卡点：一定要看输出，确认 nvidia 那两行是 Hit/Get 不是 Err 

sudo apt-get install -y nvidia-container-toolkit 
# 只装这个包，不装 nvidia-docker2（旧包，功能已整合进 toolkit） 

sudo nvidia-ctk runtime configure --runtime=docker 
# 改 /etc/docker/daemon.json 注册 nvidia runtime 
sudo systemctl restart docker 

docker run --rm --gpus all nvidia/cuda:12.2.2-base-ubuntu22.04 nvidia-smi 
# 验证：容器内输出应与宿主机 nvidia-smi 完全一致（型号/显存/驱动版本）
```
> 注:Ollama 是装在**宿主机**上跑 GPU(下一步),靶机容器经 `host.docker.internal` 访问它;
> 上面这条只是确认 Docker 本身能拿到 GPU(给 ML notebook 等留用)。

## 7.4 Ollama + 监听所有网卡

```bash
# 1. 安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. systemd override，监听所有网卡（带端口号）
sudo mkdir -p /etc/systemd/system/ollama.service.d
sudo tee /etc/systemd/system/ollama.service.d/override.conf << 'EOF'
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
EOF

sudo systemctl daemon-reload
sudo systemctl restart ollama

ss -tlnp | grep 11434 # 应该看到 0.0.0.0:11434，而不是 127.0.0.1:11434
```

## 7.5 拉模型

```bash
ollama pull llama3.1:8b     # 核心对抗模型 (~4.7GB),多数 LLM 场景
ollama pull codellama:7b    # 代码生成/分析 (~3.8GB),场景 09
ollama list
```
> rag-app 是文件型知识库,**不需要** `nomic-embed-text` 向量模型。

## 7.6 克隆代码

```bash
### ① 本地电脑(不是 VM):打包
cd C:/Users/jerem/Desktop/gcp-cyber-ai-lab   # 进项目文件夹
git archive --format=tar -o lab.tar HEAD     # 把已 commit 的文件打包成 lab.tar（私密文件不会被打包）

### ② 本地电脑：传到 VM
gcloud compute scp lab.tar cyber-ai-lab-vm:lab.tar --zone=asia-southeast1-a --tunnel-through-iap

⚠️ 目标路径**不要**写成 `cyber-ai-lab-vm:~/lab.tar`——Windows 上 `gcloud compute scp`
底层用的 `pscp` 对 `~`（波浪号，代表家目录）处理有 bug，会报错"打不开文件"。
不写路径、只写文件名，默认就落在家目录，效果一样。

### ③ SSH 进 VM，解压（以下命令在 **VM 里面**跑）

gcloud compute ssh cyber-ai-lab-vm --zone=asia-southeast1-a --tunnel-through-iap   # 远程登录进 VM
mkdir -p ~/cyber-ai-lab                        # 建一个空文件夹装项目
tar -xf ~/lab.tar -C ~/cyber-ai-lab            # 把包解开放进这个文件夹
rm ~/lab.tar                                   # 包用完了，删掉省空间
cd ~/cyber-ai-lab                              # 进项目文件夹，后面步骤都在这里执行
git clone https://github.com/mitre/caldera.git --recursive external/caldera   # CALDERA 是别人公开源码，直接从网上拉，跟上面打包传输无关；仅 offense/all profile 才需要
```

## 7.7 验证就绪

```bash
nvidia-smi && ollama list && docker ps
```

➡️ 下一步:**[`08 — Splunk Setup`](<08 — Splunk Setup (Indexes, HEC, Add-ons).md>)**(先把云端 SIEM 配好,再点火)
