# 06 — Sysmon & Splunk Universal Forwarder

Run the following on **both** `win-dc` and `win-client`.  
Open **PowerShell as Administrator** on each machine.

---

## Step 1 — Install Sysmon

```powershell
# Download Sysmon
Invoke-WebRequest -Uri "https://download.sysinternals.com/files/Sysmon.zip" -OutFile "C:\Sysmon.zip"
Expand-Archive -Path "C:\Sysmon.zip" -DestinationPath "C:\Sysmon"

# Download SwiftOnSecurity config (community best-practice ruleset)
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/SwiftOnSecurity/sysmon-config/master/sysmonconfig-export.xml" -OutFile "C:\Sysmon\sysmonconfig.xml"

# Install Sysmon with the config
cd C:\Sysmon
.\Sysmon64.exe -i sysmonconfig.xml -accepteula
```

---

## Step 2 — Install Splunk Universal Forwarder

```powershell
# Download installer
wget -O splunkforwarder.msi "https://download.splunk.com/products/universalforwarder/releases/10.4.0/windows/splunkforwarder-10.4.0-652ec96167cf-windows-x86.msi"
```

Run the `.msi` installer with these settings:
- **Logon Information**: Local System
- **Receiving Indexer**: `10.0.10.50` (splunk-server IP), port `9997`

---

## Step 3 — Configure Sysmon Log Forwarding

Create or edit the file:
`C:\Program Files\SplunkUniversalForwarder\etc\system\local\inputs.conf`

```ini
[WinEventLog://Microsoft-Windows-Sysmon/Operational]
disabled = false
renderXml = true
index = wineventlog
```

---

## Step 4 — Restart Forwarder

```powershell
Restart-Service SplunkForwarder
```

---

## Step 5 — Verify in Splunk

In Splunk Web, run:

```spl
index=wineventlog sourcetype="XmlWinEventLog:Microsoft-Windows-Sysmon/Operational"
| stats count by EventCode
| sort -count
```

You should see Sysmon event codes like `1` (process create), `3` (network connection), `11` (file create), etc.
