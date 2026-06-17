# 01 — VPC Network & Firewall Rules

## 1. Create VPC Network

1. Login to [Google Cloud Console](https://console.cloud.google.com/)
2. Search for **VPC Network** and click **Create VPC network**
3. Fill in the following:
   - Name: `security-lab-vpc`
   - Subnet creation mode: **Custom**
   - Subnet name: `lab-subnet`
   - Region: `asia-southeast1`
   - IPv4 range: `10.0.10.0/24`
4. Leave the rest as default and click **Create**

---

## 2. Create Firewall Rules

Go to **VPC Network → Firewall** and create 2 rules:

### Rule 1 — Allow Google IAP Tunnel

| Field | Value |
|---|---|
| Name | `allow-iap-ingress` |
| Network | `security-lab-vpc` |
| Direction | Ingress |
| Targets | All instances in the network |
| Source filter | IPv4 ranges |
| Source IPv4 ranges | `35.235.240.0/20` |
| Protocols and ports | TCP: `22, 3389, 5901, 8000` |

### Rule 2 — Allow Internal Traffic

| Field | Value |
|---|---|
| Name | `allow-internal-traffic` |
| Network | `security-lab-vpc` |
| Direction | Ingress |
| Targets | All instances in the network |
| Source filter | IPv4 ranges |
| Source IPv4 ranges | `10.0.10.0/24` |
| Protocols and ports | Allow all |

---

## 3. Create Cloud NAT Gateway

Cloud NAT allows VMs without public IPs to download software from the internet.

1. Search for **Cloud NAT** in the console
2. Click **Create Cloud NAT gateway**
3. Fill in:
   - Gateway name: `lab-nat-gateway`
   - Network: `security-lab-vpc`
   - Region: `asia-southeast1`
   - Cloud Router: click **Create new router** → name: `nat-router`
   - Cloud NAT IP addresses: **Automatic**
4. Click **Create**

## 4. GCP Shell automation
```shell
# 1. Create the Custom VPC Network
gcloud compute networks create security-lab-vpc --subnet-mode=custom

# 2. Create the Subnet
gcloud compute networks subnets create lab-subnet \
    --network=security-lab-vpc \
    --region=asia-southeast1 \
    --range=10.0.10.0/24

# 3. Create Firewall Rule 1: Allow Google IAP Tunnel
gcloud compute firewall-rules create allow-iap-ingress \
    --network=security-lab-vpc \
    --direction=INGRESS \
    --action=ALLOW \
    --rules=tcp:22,tcp:3389,tcp:5901,tcp:8000 \
    --source-ranges=35.235.240.0/20

# 4. Create Firewall Rule 2: Allow Internal Traffic
gcloud compute firewall-rules create allow-internal-traffic \
    --network=security-lab-vpc \
    --direction=INGRESS \
    --action=ALLOW \
    --rules=all \
    --source-ranges=10.0.10.0/24

# 5. Create the Cloud Router (Required for NAT)
gcloud compute routers create nat-router \
    --network=security-lab-vpc \
    --region=asia-southeast1

# 6. Create the Cloud NAT Gateway
gcloud compute routers nats create lab-nat-gateway \
    --router=nat-router \
    --region=asia-southeast1 \
    --auto-allocate-nat-external-ips \
    --nat-all-subnet-ip-ranges

echo "✅ VPC, Firewall Rules, and NAT Gateway created successfully!"
```
