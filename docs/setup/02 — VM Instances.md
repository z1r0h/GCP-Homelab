# 02 — VM Instances

All VMs are in region `asia-southeast1`, zone `asia-southeast1-a`, on the `security-lab-vpc` / `lab-subnet` network.

## Network Map

| VM | IP | OS | Role |
|---|---|---|---|
| `win-dc` | `10.0.10.10` | Windows Server 2022 | AD Domain Controller |
| `win-client` | `10.0.10.20` | Windows Server 2022 | Employee Workstation |
| `splunk-server` | `10.0.10.50` | Ubuntu 22.04 | Splunk SIEM |
| `kali-linux-attacker-vm` | `10.0.10.3` | Kali Linux | Attack Machine |

---

## 1. win-dc (AD Domain Controller)

- Machine type: `e2-standard-2` (2 vCPU, 8 GB RAM)
- OS: Windows Server 2022 Datacenter (Desktop Experience)
- Boot disk: Balanced persistent disk, 50 GB
- Networking:
  - Network / Subnet: `security-lab-vpc` / `lab-subnet`
  - Primary internal IP: `10.0.10.10` (custom)
  - External IP: **None**

---

## 2. win-client (Employee Workstation)

- Machine type: `e2-standard-2` (2 vCPU, 8 GB RAM)
- OS: Windows Server 2022 Datacenter (Desktop Experience)
- Boot disk: Balanced persistent disk, 50 GB
- Networking:
  - Network / Subnet: `security-lab-vpc` / `lab-subnet`
  - Primary internal IP: `10.0.10.20` (custom)
  - External IP: **None**

---

## 3. splunk-server (Splunk SIEM)

- Machine type: `e2-standard-2` (2 vCPU, 8 GB RAM)
- OS: Ubuntu 22.04 LTS
- Boot disk: Balanced persistent disk, 30 GB
- Networking:
  - Network / Subnet: `security-lab-vpc` / `lab-subnet`
  - Primary internal IP: `10.0.10.50` (custom)
  - External IP: **Ephemeral** (needed to download Splunk; inbound blocked by firewall)

---

## 4. kali-linux-attacker-vm (Attack Machine)

- Machine type: `e2-standard-2` (2 vCPU, 8 GB RAM)
- OS: Kali Linux with XFCE4 Desktop GUI (from GCP Marketplace)
- Networking:
  - Network / Subnet: `security-lab-vpc` / `lab-subnet`
  - Primary internal IP: `10.0.10.100` (custom)
  - External IP: **Ephemeral** (for downloading attack tools)

### Auto-start VNC on boot

SSH into Kali and run:

```bash
sudo tee /etc/systemd/system/vncserver.service <<EOF
[Unit]
Description=Start TightVNC server at startup
After=syslog.target network.target

[Service]
Type=forking
User=$USER
Group=$USER
WorkingDirectory=$HOME
PIDFile=$HOME/.vnc/%H:1.pid
ExecStartPre=-/usr/bin/vncserver -kill :1 > /dev/null 2>&1
ExecStart=/usr/bin/vncserver -depth 24 -geometry 1920x1080 :1
ExecStop=/usr/bin/vncserver -kill :1

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable vncserver.service
sudo systemctl start vncserver.service
sudo systemctl status vncserver.service
```
