# Architecture

This document describes the Azure resources deployed by [infra/main.bicep](../infra/main.bicep), the Azure Verified Modules (AVM) used, and the network topology options.

The solution accelerator supports two primary architectural approaches:

1. **With Network Isolation**: All resources deployed with private endpoints and network isolation
2. **Without Network Isolation**: All resources deployed with public endpoints

Both architectural approaches can optionally include an Azure AI Foundry Hub for enhanced ML workspace capabilities. See [Project Modes](PROJECT_MODES.md) for detailed configuration options and use cases.

## Core Architecture Components

### Always Deployed Resources

These resources are deployed in both architectural approaches:

| Resource | Purpose | AVM Reference |
|----------|---------|---------------|
| Azure AI Foundry (AI Services) | Core AI capabilities and project management | [avm/res/cognitive-services/account](https://github.com/Azure/bicep-registry-modules/tree/main/modules/cognitive-services/account) |
| Log Analytics Workspace | Centralized monitoring and diagnostics | [avm/res/operational-insights/workspace](https://github.com/Azure/bicep-registry-modules/tree/main/modules/operational-insights/workspace) |
| Application Insights | Application monitoring and telemetry | [avm/res/insights/component](https://github.com/Azure/bicep-registry-modules/tree/main/modules/insights/component) |

### Optional Resources

These resources are deployed based on configuration:

| Resource | When Deployed | Purpose | AVM Reference |
|----------|---------------|---------|---------------|
| Azure AI Foundry Hub | `AZURE_AI_FOUNDRY_HUB_DEPLOY=true` | Enhanced ML workspace capabilities | [avm/res/machine-learning-services/workspace](https://github.com/Azure/bicep-registry-modules/tree/main/modules/machine-learning-services/workspace) |
| Azure Storage Account | Hub deployment | Required for ML workspace functionality | [avm/res/storage/storage-account](https://github.com/Azure/bicep-registry-modules/tree/main/modules/storage/storage-account) |
| Azure Key Vault | Hub deployment | Secure secret management for ML workspaces | [avm/res/key-vault/vault](https://github.com/Azure/bicep-registry-modules/tree/main/modules/key-vault/vault) |
| Azure AI Search | `AZURE_AI_SEARCH_DEPLOY=true` | Search and indexing capabilities | [avm/res/search/search-service](https://github.com/Azure/bicep-registry-modules/tree/main/modules/search/search-service) |
| Azure Container Registry | `AZURE_CONTAINER_REGISTRY_DEPLOY=true` | Container image management | [avm/res/container-registry/registry](https://github.com/Azure/bicep-registry-modules/tree/main/modules/container-registry/registry) |
| Sample Data Storage | `DEPLOY_SAMPLE_DATA=true` | Dedicated storage for sample data | [avm/res/storage/storage-account](https://github.com/Azure/bicep-registry-modules/tree/main/modules/storage/storage-account) |

## Architecture with Network Isolation

When network isolation is enabled (`AZURE_NETWORK_ISOLATION=true`), all resources are deployed with private endpoints and public access is disabled.

### Network Isolation Architecture Diagram

The following diagram illustrates the architecture when network isolation is enabled:

[![Azure AI Foundry Jumpstart with Network Isolation](images/azure-ai-foundry-jumpstart-zero-trust.svg)](images/azure-ai-foundry-jumpstart-zero-trust.svg)

### Network Isolation Components

#### Core Resources (Always Deployed)

| Resource | Deployment Details | AVM Reference |
|----------|-------------------|---------------|
| Azure AI Foundry (AI Services) | Deployed with private endpoint (PE) | [avm/res/cognitive-services/account](https://github.com/Azure/bicep-registry-modules/tree/main/modules/cognitive-services/account) |
| Log Analytics Workspace | Public endpoint (monitoring services) | [avm/res/operational-insights/workspace](https://github.com/Azure/bicep-registry-modules/tree/main/modules/operational-insights/workspace) |
| Application Insights | Public endpoint (monitoring services) | [avm/res/insights/component](https://github.com/Azure/bicep-registry-modules/tree/main/modules/insights/component) |
| Virtual Network | 10.0.0.0/16 with multiple subnets | [avm/res/network/virtual-network](https://github.com/Azure/bicep-registry-modules/tree/main/modules/network/virtual-network) |
| Private DNS Zones | AI Services, OpenAI, and AI domains | [avm/res/network/private-dns-zone](https://github.com/Azure/bicep-registry-modules/tree/main/modules/network/private-dns-zone) |

#### Optional Resources (Based on Configuration)

| Resource | Condition | Deployment Details | AVM Reference |
|----------|-----------|-------------------|---------------|
| Azure AI Foundry Hub | `AZURE_AI_FOUNDRY_HUB_DEPLOY=true` | Deployed with private endpoint (PE) | [avm/res/machine-learning-services/workspace](https://github.com/Azure/bicep-registry-modules/tree/main/modules/machine-learning-services/workspace) |
| Azure Storage Account | Hub deployment | Deployed with private endpoint (PE) | [avm/res/storage/storage-account](https://github.com/Azure/bicep-registry-modules/tree/main/modules/storage/storage-account) |
| Azure Key Vault | Hub deployment | Deployed with private endpoint (PE) | [avm/res/key-vault/vault](https://github.com/Azure/bicep-registry-modules/tree/main/modules/key-vault/vault) |
| Azure AI Search | `AZURE_AI_SEARCH_DEPLOY=true` | Deployed with private endpoint (PE) | [avm/res/search/search-service](https://github.com/Azure/bicep-registry-modules/tree/main/modules/search/search-service) |
| Azure Container Registry | `AZURE_CONTAINER_REGISTRY_DEPLOY=true` | Deployed with private endpoint (PE) | [avm/res/container-registry/registry](https://github.com/Azure/bicep-registry-modules/tree/main/modules/container-registry/registry) |
| Sample Data Storage | `DEPLOY_SAMPLE_DATA=true` | Deployed with private endpoint (PE) | [avm/res/storage/storage-account](https://github.com/Azure/bicep-registry-modules/tree/main/modules/storage/storage-account) |
| Azure Bastion Host | `AZURE_BASTION_HOST_DEPLOY=true` | Required for private endpoint access | [avm/res/network/bastion-host](https://github.com/Azure/bicep-registry-modules/tree/main/modules/network/bastion-host) |

> **PE** – deployed with a private endpoint; public network access disabled where supported.

## Architecture without Network Isolation

When network isolation is disabled (`AZURE_NETWORK_ISOLATION=false`), all resources are deployed with public endpoints and no networking resources are created.

### Public Access Architecture Diagram

The following diagram illustrates the architecture when network isolation is disabled:

[![Azure AI Foundry Jumpstart without Network Isolation](images/azure-ai-foundry-jumpstart-public.svg)](images/azure-ai-foundry-jumpstart-public.svg)

### Public Access Components

#### Core Resources (Public Endpoints)

| Resource | Deployment Details | AVM Reference |
|----------|-------------------|---------------|
| Azure AI Foundry (AI Services) | Public endpoint enabled | [avm/res/cognitive-services/account](https://github.com/Azure/bicep-registry-modules/tree/main/modules/cognitive-services/account) |
| Log Analytics Workspace | Public endpoint (monitoring services) | [avm/res/operational-insights/workspace](https://github.com/Azure/bicep-registry-modules/tree/main/modules/operational-insights/workspace) |
| Application Insights | Public endpoint (monitoring services) | [avm/res/insights/component](https://github.com/Azure/bicep-registry-modules/tree/main/modules/insights/component) |

#### Optional Resources (Public Configuration)

| Resource | Condition | Deployment Details | AVM Reference |
|----------|-----------|-------------------|---------------|
| Azure AI Foundry Hub | `AZURE_AI_FOUNDRY_HUB_DEPLOY=true` | Public endpoint enabled | [avm/res/machine-learning-services/workspace](https://github.com/Azure/bicep-registry-modules/tree/main/modules/machine-learning-services/workspace) |
| Azure Storage Account | Hub deployment | Public endpoint enabled | [avm/res/storage/storage-account](https://github.com/Azure/bicep-registry-modules/tree/main/modules/storage/storage-account) |
| Azure Key Vault | Hub deployment | Public endpoint enabled | [avm/res/key-vault/vault](https://github.com/Azure/bicep-registry-modules/tree/main/modules/key-vault/vault) |
| Azure AI Search | `AZURE_AI_SEARCH_DEPLOY=true` | Public endpoint enabled | [avm/res/search/search-service](https://github.com/Azure/bicep-registry-modules/tree/main/modules/search/search-service) |
| Azure Container Registry | `AZURE_CONTAINER_REGISTRY_DEPLOY=true` | Public endpoint enabled | [avm/res/container-registry/registry](https://github.com/Azure/bicep-registry-modules/tree/main/modules/container-registry/registry) |
| Sample Data Storage | `DEPLOY_SAMPLE_DATA=true` | Public endpoint enabled | [avm/res/storage/storage-account](https://github.com/Azure/bicep-registry-modules/tree/main/modules/storage/storage-account) |

## Network Topology (Network Isolation Mode)

When network isolation is enabled (`AZURE_NETWORK_ISOLATION=true`), all resources are deployed within a virtual network with private endpoints.

### Virtual Network Subnets

The virtual network is segmented into multiple subnets to enable granular network security and future scalability:

| Subnet              | Address‑Prefix    | Purpose                                                    |
|---------------------|------------------|-------------------------------------------------------------|
| `Default`           | 10.0.0.0/24      | Reserved for future use (not used)                          |
| `AiServices`        | 10.0.1.0/24      | AI Foundry Hub, AI Search & AI Services private endpoints   |
| `Data`              | 10.0.2.0/24      | Key Vault, Storage private endpoints (when Hub is deployed) |
| `Management`        | 10.0.3.0/24      | Reserved for future management endpoints (currently unused) |
| `AzureBastionSubnet`| 10.0.255.0/27    | Bastion gateway (optional)                                  |

> **Note:** The `Management` subnet is currently empty and reserved for future use (e.g., private endpoints for monitoring or management).
> The `Data` subnet is only used when the Hub is deployed since Key Vault and Storage Account are Hub dependencies.

All private endpoints are placed in their dedicated subnets, isolating traffic and enabling granular NSG rules if required.

### Logical Network Topology

The following diagram illustrates the logical network topology of the deployed resources. The `azd-env-name` tag is applied to all resources for traceability.

```mermaid
flowchart RL
    subgraph RG["Resource Group"]
        subgraph VNet["10.0.0.0/16 – Virtual Network"]
            direction RL
            subgraph S1["AiServices (10.0.1.0/24)"]
                PE_Hub["PE: AI Foundry Hub (Optional)"]    
                PE_Services["PE: AI Services"]
                PE_Search["PE: AI Search (Optional)"]
            end
            subgraph S2["Data (10.0.2.0/24) - Hub dependencies"]
                PE_AKV["PE: Key Vault (Hub only)"]
                PE_Storage["PE: Storage (Hub only)"]
                PE_SampleStorage["PE: Sample Storage (Optional)"]
            end
            subgraph S3["Management (10.0.3.0/24)"]
                EmptyMgmt["(reserved for future use)"]
            end
            subgraph S4["AzureBastionSubnet (10.0.255.0/27)"]
                Bastion["Azure Bastion (Optional)"]
            end
        end
        LA["Log Analytics"]
        AI["App Insights"]
    end

    LA ---|Diagnostic Settings| PE_Search
    LA ---|Diagnostic Settings| PE_Services
    LA ---|Diagnostic Settings| PE_Hub
    LA ---|Diagnostic Settings| PE_Storage
    LA ---|Diagnostic Settings| PE_SampleStorage
    LA ---|Diagnostic Settings| Bastion
    AI --- LA
```

## Hub vs. AI Services Projects

The solution supports deploying projects to either the AI Foundry resource directly or to the optional Hub:

| Aspect | Hub Projects | AI Services Projects |
|--------|--------------|---------------------|
| **Resource Type** | `Microsoft.MachineLearningServices/workspaces` with `kind: 'Project'` | `Microsoft.CognitiveServices/accounts/projects` |
| **Dependencies** | Requires Hub, Storage, Key Vault | Only requires AI Services resource |
| **Capabilities** | Full ML workspace features | AI Foundry focused capabilities |
| **Network Complexity** | Higher (Hub + dependencies) | Lower (AI Services only) |
| **Cost** | Higher due to Hub dependencies | Lower, optimized resource count |
| **Configuration** | `AZURE_AI_FOUNDRY_HUB_PROJECT_DEPLOY=true` | `AZURE_AI_FOUNDRY_PROJECT_DEPLOY=true` (with Hub disabled) |

## Configuration Examples

### Minimal AI Services Only

```bash
azd env set AZURE_AI_FOUNDRY_HUB_DEPLOY false
azd env set AZURE_AI_FOUNDRY_PROJECT_DEPLOY true
azd env set AZURE_NETWORK_ISOLATION false
```

**Result**: AI Services with projects, no Hub, public endpoints.

### Full Hub with Network Isolation

```bash
azd env set AZURE_AI_FOUNDRY_HUB_DEPLOY true
azd env set AZURE_AI_FOUNDRY_HUB_PROJECT_DEPLOY true
azd env set AZURE_NETWORK_ISOLATION true
```

**Result**: AI Services + Hub + Hub projects, private endpoints, full ML capabilities.

### Hybrid Configuration

```bash
azd env set AZURE_AI_FOUNDRY_HUB_DEPLOY true
azd env set AZURE_AI_FOUNDRY_HUB_PROJECT_DEPLOY false
azd env set AZURE_AI_FOUNDRY_PROJECT_DEPLOY true
azd env set AZURE_NETWORK_ISOLATION true
```

**Result**: AI Services + Hub + AI Services projects, private endpoints.

## Security & Best Practices

1. **Managed Identities** – API key authentication can be disabled. All resources use managed identities to authenticate to other Azure services.
2. **Centralized Logging** – Diagnostic settings forward metrics/logs to Log Analytics.
3. **Tagging** – Every resource inherits the `azd-env-name` tag for traceability.
4. **Azure Verified Modules** – All resources are deployed using [Azure Verified Modules (AVM)](https://aka.ms/avm).
5. **Network Isolation** – When enabled, all PaaS services use private endpoints and disable public access.
6. **Zero Trust** – Network isolation deployment follows Microsoft's Zero Trust security model and Secure Future Initiative.
7. **Flexible Architecture** – Choose between simple AI Services-only deployment or full Hub capabilities based on requirements.
