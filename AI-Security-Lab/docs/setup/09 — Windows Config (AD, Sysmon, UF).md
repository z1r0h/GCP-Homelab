# 09 — Windows Config (AD, Sysmon, UF)

> **可选 / 紫队专用**(场景 17/18)。RDP 进 `05` 建的两台 Windows VM,提升域控、客户端入域、
> 装 Sysmon + Universal Forwarder 把日志推到 Splunk。RDP 方法见 `06`。
> 没做 `05` 的话跳过本页。

---

## 9.1 提升域控(在 win-dc 上,PowerShell 管理员)

```powershell
# 1. Reset local Administrator password (Optional)
net user labadmin YOUR_LABADMIN_PASSWORD
# 安装 AD 角色并提升为新林的域控
Install-WindowsFeature AD-Domain-Services -IncludeManagementTools
Import-Module ADDSDeployment
Install-ADDSForest -DomainName "200teamok.local" -InstallDns `
  -SafeModeAdministratorPassword (ConvertTo-SecureString "YOUR_DSRM_PASSWORD" -AsPlainText -Force) -Force
# 自动重启后,本机即域控,DNS 也起来了
```

```powershell
#**先在 DC(`win-dc`)上建一个普通域用户,专门用来入域**
New-ADUser -Name "joinuser" -SamAccountName "joinuser" `
  -AccountPassword (ConvertTo-SecureString "YOUR_JOINUSER_PASSWORD" -AsPlainText -Force) `
  -Enabled $true
```


## 9.2 客户端入域(在 win-client 上)

```powershell
# 把 DNS 指向域控内网 IP(否则找不到域)
Set-DnsClientServerAddress -InterfaceAlias "Ethernet" -ServerAddresses "10.0.10.20"
# 加入域并重启，避免使用admin acc来加入以免被mimikatz dump出
Add-Computer -DomainName "200teamok.local" `
  -Credential (Get-Credential cyberlab\joinuser) -Restart
```

## 9.3 装 Sysmon(两台都装,用 sysmon-modular 的 balanced 配置)

我们用 **[olafhartong/sysmon-modular](https://github.com/olafhartong/sysmon-modular)** ——业界标准、按 MITRE ATT&CK 技术打标签的社区维护配置,比自己写的精简版详细得多。不用手动拷文件,VM 上直接下载最新版:

```powershell
# 1) 下载最新 Sysmon(Sysinternals 官方)
Invoke-WebRequest -Uri "https://download.sysinternals.com/files/Sysmon.zip" -OutFile "$env:TEMP\Sysmon.zip"
Expand-Archive "$env:TEMP\Sysmon.zip" -DestinationPath "$env:TEMP\Sysmon" -Force

# 2) 拉 sysmon-modular 的 balanced 配置(schemaversion 4.90,官方标注"medium verbosity")
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/olafhartong/sysmon-modular/master/sysmonconfig.xml" -OutFile "$env:TEMP\sysmonconfig.xml"

# 3) 安装(以后更新配置用 -c,不用 -accepteula)
& "$env:TEMP\Sysmon\Sysmon64.exe" -accepteula -i "$env:TEMP\sysmonconfig.xml"
```

> ⚠️ **License 警告**:这个配置比精简版详细得多,尤其 EventID 7(ImageLoad,DLL 加载)通常占 Sysmon 总日志量的 60-80%,
> 在 10GB/天配额上很容易爆量。**装完 UF(下面 9.4)后,务必去 `08` 的 8.1a 做 ingest-time 过滤**,零 License 代价丢掉这类高量低价值事件。

## 9.4 装 Universal Forwarder 并指向 Splunk(两台都装)

```powershell
# 1) 下载 UF(跟 04 装的 Splunk Enterprise 同版本 10.4.0,forwarder/indexer 版本对齐)
Invoke-WebRequest -Uri "https://download.splunk.com/products/universalforwarder/releases/10.4.0/windows/splunkforwarder-10.4.0-f798d4d49089-windows-x64.msi" -OutFile "$env:TEMP\splunkforwarder.msi"

# 2) 静默装,并检查退出码(0 = 成功)
Start-Process msiexec.exe -ArgumentList "/i `"$env:TEMP\splunkforwarder.msi`" AGREETOLICENSE=Yes RECEIVING_INDEXER=`"10.0.10.10:9997`" /quiet" -Wait -PassThru | Select-Object ExitCode

# 3) 配置采集 Sysmon + 安全日志
# ⚠️ WinEventLog 没有 `splunk add monitor` 这种 CLI 命令(那是给文件监控用的),
#    只能直接写 inputs.conf,写完重启生效。
$inputs = "C:\Program Files\SplunkUniversalForwarder\etc\system\local\inputs.conf"
Add-Content -Path $inputs -Value @"

[WinEventLog://Microsoft-Windows-Sysmon/Operational]
disabled = false
renderXml = true
source = XmlWinEventLog:Microsoft-Windows-Sysmon/Operational
index = sysmon

[WinEventLog://Security]
disabled = false
index = wineventlog

[WinEventLog://Microsoft-Windows-PowerShell/Operational]
disabled = false
renderXml = true
index = wineventlog
"@
```
> `10.0.10.10:9997` = Splunk VM 内网 IP + `08` 开的接收口。`02` 的 `allow-internal` 已放行 9997。
> `renderXml = true` 让 Sysmon 事件以结构化 XML 转发,`source` 显式写死方便 `08` 的过滤规则精确匹配。

## 9.5 — Enable Windows Advanced Audit Policy

Windows does not log most security events by default. Enable everything the attack scenarios need:

> ⚠️ **Critical first step — force subcategory override.** `auditpol` subcategory settings are silently ignored unless this registry value is set. Without it, the legacy category policy overrides your subcategory settings and events like 4698 (scheduled task) never appear, even though `auditpol /get` shows them enabled. Run this **before** the auditpol commands:


```powershell
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Lsa" /v SCENoApplyLegacyAuditPolicy /t REG_DWORD /d 1 /f
# Account Logon
auditpol /set /subcategory:"Credential Validation" /success:enable /failure:enable
auditpol /set /subcategory:"Kerberos Authentication Service" /success:enable /failure:enable
auditpol /set /subcategory:"Kerberos Service Ticket Operations" /success:enable /failure:enable

# Logon/Logoff
auditpol /set /subcategory:"Logon" /success:enable /failure:enable
auditpol /set /subcategory:"Logoff" /success:enable /failure:enable
auditpol /set /subcategory:"Special Logon" /success:enable /failure:enable

# Account Management
auditpol /set /subcategory:"User Account Management" /success:enable /failure:enable
auditpol /set /subcategory:"Security Group Management" /success:enable /failure:enable
auditpol /set /subcategory:"Computer Account Management" /success:enable /failure:enable

# Detailed Tracking
auditpol /set /subcategory:"Process Creation" /success:enable /failure:enable
auditpol /set /subcategory:"Process Termination" /success:enable /failure:enable

# Object Access (SMB share enumeration)
auditpol /set /subcategory:"File Share" /success:enable /failure:enable
auditpol /set /subcategory:"Detailed File Share" /success:enable /failure:enable

# DS Access (DCSync detection — mainly DC, safe on both)
auditpol /set /subcategory:"Directory Service Access" /success:enable /failure:enable

# Policy Change
auditpol /set /subcategory:"Audit Policy Change" /success:enable /failure:enable
```

By default Event 4688 omits the command line. Enable it so you can see what commands ran:

```powershell
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Audit" /v ProcessCreationIncludeCmdLine_Enabled /t REG_DWORD /d 1 /f
```

Captures all PowerShell code executed (Event 4104), even if obfuscated:

```powershell
# Script Block Logging
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging" /v EnableScriptBlockLogging /t REG_DWORD /d 1 /f

# Module Logging
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ModuleLogging" /v EnableModuleLogging /t REG_DWORD /d 1 /f
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ModuleLogging\ModuleNames" /v "*" /t REG_SZ /d "*" /f

# Restart forwarder to apply everything
Restart-Service SplunkForwarder
```

## 9.5 验证(在 Splunk Web)

```spl
index=sysmon OR index=wineventlog | stats count by host
```
两台 Windows 主机名出现即接通。

➡️ 下一步:**[`10 — Wazuh & Log Pipeline`](<10 — Wazuh & Log Pipeline.md>)**
