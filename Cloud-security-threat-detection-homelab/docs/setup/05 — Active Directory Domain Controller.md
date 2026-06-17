# 05 — Active Directory Domain Controller

Connect to `win-dc` via RDP, then open **PowerShell as Administrator**.

## Promote win-dc to Domain Controller

```powershell
# 1. Reset local Administrator password
net user Administrator TryHackMe123!

# 2. Install AD Domain Services
Install-WindowsFeature -Name AD-Domain-Services -IncludeManagementTools

# 3. Create new AD forest
Import-Module ADDSDeployment
Install-ADDSForest `
    -CreateDnsDelegation:$false `
    -DatabasePath "C:\Windows\NTDS" `
    -DomainMode "WinThreshold" `
    -DomainName "200teamok.local" `
    -DomainNetbiosName "200TEAMOK" `
    -ForestMode "WinThreshold" `
    -InstallDns:$true `
    -LogPath "C:\Windows\NTDS" `
    -NoRebootOnCompletion:$false `
    -SysvolPath "C:\Windows\SYSVOL" `
    -Force:$true
```

When prompted for `SafeModeAdministratorPassword`, enter a secure password.

The system will reboot automatically. After reboot, login with:
- Username: `200TEAMOK\Administrator`
- Password: the password set above

---

## Create Test Accounts (used by attack scenarios)

After reboot, RDP back into win-dc and create the accounts that later scenarios rely on:

```powershell
# Regular user (used in Kerberoasting request, lateral movement, etc.)
New-ADUser -Name "jsmith" -SamAccountName "jsmith" `
  -UserPrincipalName "jsmith@200teamok.local" `
  -AccountPassword (ConvertTo-SecureString "Passw0rd123!" -AsPlainText -Force) `
  -Enabled $true

# Service account with SPN (target for Kerberoasting — scenario 10)
New-ADUser -Name "svc-sql" -SamAccountName "svc-sql" `
  -UserPrincipalName "svc-sql@200teamok.local" `
  -AccountPassword (ConvertTo-SecureString "Service123!" -AsPlainText -Force) `
  -Enabled $true
setspn -A MSSQLSvc/sql.200teamok.local:1433 svc-sql
```

---

## Join win-client to Domain

Connect to `win-client` via RDP, open **PowerShell as Administrator**:

```powershell
# 1. Set DNS to point to win-dc
$Adapter = Get-NetAdapter | Where-Object {$_.Status -eq "Up"} | Select-Object -First 1
Set-DnsClientServerAddress -InterfaceIndex $Adapter.InterfaceIndex -ServerAddresses "10.0.10.10"

# 2. Verify DNS resolves correctly (should return 10.0.10.10)
nslookup 200teamok.local

# 3. Join the domain (will prompt for domain admin credentials)
Add-Computer -DomainName "200teamok.local" -Restart -Force
```

When prompted:
- Username: `200TEAMOK\Administrator`
- Password: domain admin password

System reboots automatically after joining.

> **GCP DNS note:** GCP pushes its own DNS server via DHCP, which can overwrite the manual DNS setting on reboot and break domain login. To make it stick, the robust fix is to set win-dc (`10.0.10.10`) as the DNS server for the **subnet/VPC** — or, simpler for a lab, re-run the `Set-DnsClientServerAddress` command if the client ever loses the domain after a reboot. If domain join fails at step 3 with a DNS error, confirm `nslookup 200teamok.local` returns `10.0.10.10` first.


## Adding a Team Member

### 1. Grant GCP IAM access

Go to **IAM & Admin → Grant Access** and assign these two roles to their Gmail:
- `IAP-secured Tunnel User`
- `Compute OS Admin Login`

### 2. Create AD user on win-dc (PowerShell as admin)

```powershell
New-ADUser -Name "username" `
  -SamAccountName "username" `
  -UserPrincipalName "username@200teamok.local" `
  -Enabled $true `
  -AccountPassword (ConvertTo-SecureString "Password123!" -AsPlainText -Force)
```

### 3. Add to Remote Desktop Users on win-client

```powershell
Add-LocalGroupMember -Group "Remote Desktop Users" -Member "200TEAMOK\username"
```
