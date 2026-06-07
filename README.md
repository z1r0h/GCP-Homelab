# GCP Active Directory & Splunk SIEM Threat Detection Lab

A secure, cloud-based network security homelab deployed on Google Cloud Platform (GCP). This project demonstrates the implementation of Active Directory (AD) Domain Services, secure log forwarding via Splunk Universal Forwarder, Sysmon configuration, and an isolated Kali Linux attacker node, all managed securely through GCP Identity-Aware Proxy (IAP) tunnels without exposing public IP addresses.

---

## 📐 Network Topology & Architecture

All instances are situated within a custom virtual network (`10.0.10.0/24`) with outbound internet access enabled via a Cloud NAT gateway, keeping the lab completely invisible to external public scans.

```mermaid
graph TD
    subgraph Custom VPC (10.0.10.0/24)
        DC[win-dc: 10.0.10.10 AD Domain Controller]
        Client[win-client: 10.0.10.20 Workstation]
        SIEM[splunk-server: 10.0.10.50 SIEM Console]
        Kali[kali-attacker: 10.0.10.100 GUI Desktop]
    end

    User((Collaborators / Owners)) -->|gcloud IAP Tunnel| Firewall{GCP Firewall Rules}
    Firewall -->|Port 3389/8000/5901| Custom_VPC
    
    Client -->|Logs via Port 9997| SIEM
    DC -->|Logs via Port 9997| SIEM
    Kali -.->|Intrusive Testing| Client
