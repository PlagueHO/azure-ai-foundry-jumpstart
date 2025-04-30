# Azure AI Foundry Secure Hub – Architecture

This document describes the Azure resources deployed by [infra/main.bicep](infra/main.bicep), the Azure Verified Modules (AVM) used, and the network topology.

## High‑Level Architecture

| Layer | Resource | AVM Reference |
|-------|----------|---------------|
| Management & Monitoring | Log Analytics Workspace | [avm/res/operational-insights/workspace](https://github.com/Azure/bicep-registry-modules/tree/main/modules/operational-insights/workspace) |
|  | Application Insights | [avm/res/insights/component](https://github.com/Azure/bicep-registry-modules/tree/main/modules/insights/component) |
| Core Networking | Virtual Network | [avm/res/network/virtual-network](https://github.com/Azure/bicep-registry-modules/tree/main/modules/network/virtual-network) |
|  | Private DNS Zones (Key Vault, Storage, ACR, Search, Cognitive Services, ML) | [avm/res/network/private-dns-zone](https://github.com/Azure/bicep-registry-modules/tree/main/modules/network/private-dns-zone) |
| Security | Azure Key Vault (PE) | [avm/res/key-vault/vault](https://github.com/Azure/bicep-registry-modules/tree/main/modules/key-vault/vault) |
| Data | Storage Account (PE) | [avm/res/storage/storage-account](https://github.com/Azure/bicep-registry-modules/tree/main/modules/storage/storage-account) |
|  | Azure AI Search (PE) | [avm/res/search/search-service](https://github.com/Azure/bicep-registry-modules/tree/main/modules/search/search-service) |
| AI Services | Azure AI Services (Cognitive) (PE) | [avm/res/cognitive-services/account](https://github.com/Azure/bicep-registry-modules/tree/main/modules/cognitive-services/account) |
|  | Azure AI Foundry Hub (ML Workspace) (PE) | [avm/res/machine-learning-services/workspace](https://github.com/Azure/bicep-registry-modules/tree/main/modules/machine-learning-services/workspace) |
| Containers | Azure Container Registry (PE) | [avm/res/container-registry/registry](https://github.com/Azure/bicep-registry-modules/tree/main/modules/container-registry/registry) |
| Access (optional) | Azure Bastion Host | [avm/res/network/bastion-host](https://github.com/Azure/bicep-registry-modules/tree/main/modules/network/bastion-host) |

> **PE** – deployed with a private endpoint; public network access disabled where supported.

## Virtual Network

| Subnet | Address‑Prefix | Purpose |
|--------|----------------|---------|
| `Default` | 10.0.0.0/24 | Reserved |
| `AiServices` | 10.0.1.0/24 | AI Search & Cognitive Services private endpoints |
| `FoundryHubs` | 10.0.2.0/24 | Azure AI Foundry Hub private endpoint |
| `SharedServices` | 10.0.3.0/24 | Key Vault, Storage, ACR private endpoints |
| `AzureBastionSubnet` | 10.0.255.0/27 | Bastion gateway (optional) |

All private endpoints are placed in their dedicated subnets, isolating traffic and enabling granular NSG rules if required.

### Logical Network Topology

The following diagram illustrates the logical network topology of the deployed resources. The `azd-env-name` tag is applied to all resources for traceability.

```mermaid
flowchart TB
    subgraph RG["Resource Group"]
        subgraph VNet["10.0.0.0/16 – Virtual Network"]
            direction TB
            subgraph S1["AiServices (10.0.1.0/24)"]
                PE_Search["PE: AI Search"]
                PE_Cog["PE: Cognitive Services"]
            end
            subgraph S2["FoundryHubs (10.0.2.0/24)"]
                PE_Hub["PE: AI Foundry Hub"]
            end
            subgraph S3["SharedServices (10.0.3.0/24)"]
                PE_KV["PE: Key Vault"]
                PE_Storage["PE: Storage"]
                PE_ACR["PE: ACR"]
            end
            subgraph S4["AzureBastionSubnet (10.0.255.0/27)"]
                Bastion["Azure Bastion (opt)"]
            end
        end
        LA["Log Analytics"]
        AI["App Insights"]
    end

    LA ---|Diagnostic Settings| PE_Search
    LA --- PE_Cog
    LA --- PE_Hub
    LA --- PE_Storage
    LA --- PE_ACR
    LA --- Bastion
```

## Security & Best Practices

1. **Private Endpoints & DNS** – All PaaS services use private endpoints; matching Private DNS Zones are linked to the VNet.
2. **Public Network Access** – Disabled for Search, Cognitive Services, Storage, ACR, ML Workspace.
3. **RBAC & Purge Protection** – Key Vault enforces RBAC and purge protection.
4. **Centralised Logging** – Diagnostic settings forward metrics/logs to Log Analytics.
5. **Tagging** – Every resource inherits the `azd-env-name` tag for traceability.
