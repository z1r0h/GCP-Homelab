# 06 — Sysmon, Forwarder & Full Logging Setup

Run everything below on **both** `win-dc` and `win-client`, in order.
Open **PowerShell as Administrator** on each machine.

> **This is a one-time setup.** Once completed on both VMs (and baseline images taken in [07](07%20%E2%80%94%20VM%20Backup%20%26%20Recovery.md)), all 14 attack scenarios work without any further logging changes.

This configures four logging layers:
1. **Sysmon** — process, network, registry, file, DNS telemetry
2. **Splunk Universal Forwarder** — ships logs to splunk-server
3. **Windows Advanced Audit Policy** — security events (4625, 4720, 4698, 4769, 4662, 5140, etc.)
4. **PowerShell Script Block Logging** — full command capture (4104)

---

## Step 1 — Install Sysmon (full-logging config)

We use the **sysmon-modular** config by Olaf Hartong instead of SwiftOnSecurity. SwiftOnSecurity uses `include` rules that only log a fixed list of ports, which silently drops most port-scan traffic. sysmon-modular logs all events and only excludes known noise — required for the attack scenarios to work.

```powershell
# Download Sysmon
Invoke-WebRequest -Uri "https://download.sysinternals.com/files/Sysmon.zip" -OutFile "C:\Sysmon.zip"
Expand-Archive -Path "C:\Sysmon.zip" -DestinationPath "C:\Sysmon" -Force

# Download sysmon-modular config (logs all events, excludes noise only)
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/olafhartong/sysmon-modular/master/sysmonconfig.xml" -OutFile "C:\Sysmon\sysmonconfig.xml"

# Install Sysmon with the config
cd C:\Sysmon
.\Sysmon64.exe -accepteula -i sysmonconfig.xml
```

Verify network logging is enabled:

```powershell
.\Sysmon64.exe -c | Select-String "Network connection"
# Expected: Network connection: enabled
```

> If Sysmon is already installed, update the config instead of reinstalling:
> `C:\Sysmon\Sysmon64.exe -c C:\Sysmon\sysmonconfig.xml`

---

## Step 2 — Install Splunk Universal Forwarder

```powershell
# Download installer
Invoke-WebRequest -Uri "https://download.splunk.com/products/universalforwarder/releases/10.4.0/windows/splunkforwarder-10.4.0-652ec96167cf-windows-x64.msi" -OutFile "C:\splunkforwarder.msi"

# Silent install pointing at splunk-server
msiexec.exe /i C:\splunkforwarder.msi RECEIVING_INDEXER="10.0.10.50:9997" AGREETOLICENSE=Yes /quiet
```

Wait ~1 minute, then confirm the service is running:

```powershell
Get-Service SplunkForwarder
```

---

## Step 3 — Enable Windows Advanced Audit Policy

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

---

## Step 4 — Include Command Line in Process Creation (4688)

By default Event 4688 omits the command line. Enable it so you can see what commands ran:

```powershell
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Audit" /v ProcessCreationIncludeCmdLine_Enabled /t REG_DWORD /d 1 /f
```

---

## Step 5 — Enable PowerShell Logging

Captures all PowerShell code executed (Event 4104), even if obfuscated:

```powershell
# Script Block Logging
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging" /v EnableScriptBlockLogging /t REG_DWORD /d 1 /f

# Module Logging
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ModuleLogging" /v EnableModuleLogging /t REG_DWORD /d 1 /f
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ModuleLogging\ModuleNames" /v "*" /t REG_SZ /d "*" /f
```

---

## Step 6 — Configure Forwarder Inputs

Tell the forwarder which logs to ship. This single config sends Sysmon, Security, PowerShell, and System logs:

```powershell
$inputs = @"
[WinEventLog://Microsoft-Windows-Sysmon/Operational]
disabled = false
renderXml = 1
source = XmlWinEventLog:Microsoft-Windows-Sysmon/Operational
index = wineventlog

[WinEventLog://Security]
disabled = false
renderXml = 1
index = wineventlog

[WinEventLog://Microsoft-Windows-PowerShell/Operational]
disabled = false
renderXml = 1
index = wineventlog

[WinEventLog://System]
disabled = false
renderXml = 1
index = wineventlog
"@
$inputs | Set-Content "C:\Program Files\SplunkUniversalForwarder\etc\system\local\inputs.conf"

# Restart forwarder to apply everything
Restart-Service SplunkForwarder
```

---

## Step 7 — Verify in Splunk

From Kali, generate a quick test:

```bash
nmap -sT 10.0.10.10
```

In Splunk Web (`http://localhost:8000`), confirm Sysmon network events parse with many ports:

```spl
index=wineventlog source="XmlWinEventLog:Microsoft-Windows-Sysmon/Operational" EventCode=3 SourceIp="10.0.10.3"
| stats dc(DestinationPort) as unique_ports by SourceIp, DestinationIp
```

You should see **many** ports (53, 88, 135, 389, 445, 3389...), not just one.

### Verification checklist

| Check | SPL | Expected |
|---|---|---|
| Sysmon network | `EventCode=3` | Many connections |
| Sysmon process | `EventCode=1` | Process creations |
| Failed logon | `EventCode=4625` | After a bad RDP login |
| Cmdline in 4688 | `EventCode=4688` | CommandLine field present |
| PowerShell | `EventCode=4104` | Script blocks |

---

## ✅ Next

Logging is now fully configured. Proceed to [07 — VM Backup & Recovery](07%20%E2%80%94%20VM%20Backup%20%26%20Recovery.md) to snapshot the baseline. You will never need to repeat this logging setup — every attack scenario runs against this baseline.
