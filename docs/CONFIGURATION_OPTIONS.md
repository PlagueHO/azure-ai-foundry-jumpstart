# Configuration Options

The following environment variables control the deployment behaviour of the Azure AI Foundry Jumpstart Solution accelerator.

The configuration options are grouped into the following categories:

- [Create Sample Data](#create-sample-data)
- [Networking & Isolation](#networking--isolation)
- [Azure AI Foundry Hub Configuration](#azure-ai-foundry-hub-configuration)
- [Azure AI Foundry Project](#azure-ai-foundry-project)
- [Azure AI Search Service](#azure-ai-search-service)
- [Identity & Access](#identity--access)
- [Optional Infrastructure](#optional-infrastructure)
- [Security](#security)

## Create Sample Data

These options control the creation of sample data and configuration in the Azure AI Foundry hub.

### DEPLOY_SAMPLE_OPENAI_MODELS

Deploy seme common OpenAI models into the Azure OpenAI Service connected to the Azure AI Foundry Hub.
Default: `true`.

This will deploy the following models into the Azure OpenAI Service. If the models aren't available in the selected region, or the quota is exceeded, the deployment will fail:

| Model Name             | Version    | Deployment Type | TPM  |
| ---------------------- | ---------- | --------------- | ---- |
| gpt-4.1                | 2025-04-14 | Global Standard | 50K  |
| gpt-4.1-mini           | 2025-04-14 | Global Standard | 100K |
| gpt-4.1-nano           | 2025-04-14 | Global Standard | 100K |
| gpt-4o                 | 2024-11-20 | Global Standard | 50K  |
| gpt-4o-transcribe      | 2025-03-20 | Global Standard | 100K |
| gpt-4o-mini            | 2024-07-18 | Global Standard | 100K |
| gpt-4o-transcribe      | 2025-03-20 | Global Standard | 100K |
| gpt-4o-mini-transcribe | 2025-03-20 | Global Standard | 100K |
| o4-mini                | 2025-04-16 | Global Standard | 50K  |
| text-embedding-3-large | 1          | Global Standard | 150K |
| model-router           | 2025-05-19 | Global Standard | 150K |

The list of models, versions, quota and TPM are defined in the [infra/sample-openai-models.json](../infra/sample-openai-models.json) file. If you wish to define an alternate models, you can edit this file or alternatively set the [AZURE_OPENAI_MODELS](#azure-openai-models) environment variable.

```powershell
azd env set DEPLOY_SAMPLE_OPENAI_MODELS false
```

### DEPLOY_SAMPLE_DATA

Create a dedicated Azure Storage Account for sample data with separation of concerns from the Azure AI Foundry Hub operational storage.
When enabled, sample data containers will be created in the dedicated storage account and datastores will be created in the Azure AI Foundry projects to connect to each container.

> [!IMPORTANT]
> When being deployed from a Windows machine, a PowerShell script is used to upload the sample data to the containers. This script will require the [PowerShell script execution policy](https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_execution_policies) to be set to `RemoteSigned` or `Unrestricted`, otherwise an execution error will occur.

Default: `false`.

When set to `true`:

- A dedicated sample data storage account will be deployed (named with 'sample' postfix)
- The following containers will be created in the sample data storage account:

- `tech-support`
- `retail-products`
- `healthcare-records`
- `financial-transactions`
- `insurance-claims`

```powershell
azd env set DEPLOY_SAMPLE_DATA true
```

## Networking & Isolation

### AZURE_NETWORK_ISOLATION

Deploy resources into a virtual network (`true`) or expose public endpoints (`false`).  
Default: `true`.

```powershell
azd env set AZURE_NETWORK_ISOLATION false
```

### AZURE_AI_FOUNDRY_HUB_IP_ALLOW_LIST

Comma‑separated list of IPv4 addresses / CIDR ranges permitted when network isolation is enabled.  
Default: `''` - no public IP addresses are allowed to access the AI Foundry hub.

> Note: This setting is only relevant when `AZURE_NETWORK_ISOLATION` is set to `true`.

```powershell
azd env set AZURE_AI_FOUNDRY_HUB_IP_ALLOW_LIST "203.0.113.10/32,198.51.100.0/24"
```

### AZURE_DISABLE_API_KEYS

Disable API keys on Azure AI services (`true`) and enforce Entra ID authentication only.  
Default: `false`.

```powershell
azd env set AZURE_DISABLE_API_KEYS true
```

## Azure AI Foundry Hub Configuration

### AZURE_AI_FOUNDRY_HUB_DEPLOY

Deploy Azure AI Foundry Hub (Machine Learning workspace) and supporting resources (Key Vault, Storage Account, Container Registry).
When set to `false`, only Azure AI Services with project management is deployed.
Default: `false`.

```powershell
azd env set AZURE_AI_FOUNDRY_HUB_DEPLOY true
```

### AZURE_AI_FOUNDRY_HUB_FRIENDLY_NAME

Friendly display name for the AI Foundry hub.
Only applies when `AZURE_AI_FOUNDRY_HUB_DEPLOY` is set to `true`.
Default: `''` - the friendly name is automatically generated from the environment name.

```powershell
azd env set AZURE_AI_FOUNDRY_HUB_FRIENDLY_NAME "My AI Hub"
```

### AZURE_AI_FOUNDRY_HUB_DESCRIPTION

Optional description shown in the Azure portal.  
Only applies when `AZURE_AI_FOUNDRY_HUB_DEPLOY` is set to `true`.
Default: `''` - the friendly name is automatically generated from the environment name.

```powershell
azd env set AZURE_AI_FOUNDRY_HUB_DESCRIPTION "Sandbox hub for PoC work"
```

## Azure AI Foundry Project

The Azure AI Foundry Jumpstart supports multiple project deployment scenarios based on your architecture preferences:

### Project Deployment Scenarios

1. **No Projects**: Set `AZURE_AI_FOUNDRY_PROJECT_DEPLOY=false` and `AZURE_AI_FOUNDRY_HUB_PROJECT_DEPLOY=false` to deploy only the AI Foundry/AI Services and/or Azure AI Foundry Hub without any projects
2. **Projects to AI Foundry/AI Services**: Set `AZURE_AI_FOUNDRY_PROJECT_DEPLOY=true` to deploy projects directly to the AI Foundry/AIServices resource.
3. **Projects to AI Foundry Hub**: Set `AZURE_AI_FOUNDRY_HUB_PROJECT_DEPLOY=true` to deploy projects as child workspaces under the AI Foundry Hub.

### Project Sources

The projects that will be deployed can be defined in two ways:

- **Single Project**: Use the `AZURE_AI_FOUNDRY_PROJECT_*` parameters to define a single project
- **Multiple Projects**: Set `AZURE_AI_FOUNDRY_PROJECTS_FROM_JSON=true` to load project definitions from the `infra/sample-ai-foundry-projects.json` file

### AZURE_AI_FOUNDRY_PROJECT_DEPLOY

Enable deployment of Projects into the Azure AI Foundry/AI Services resource.
When set to `false`, no project resources are created in the Azure AI Foundry/AI Services resource.

Default: `true`.

```powershell
azd env set AZURE_AI_FOUNDRY_PROJECT_DEPLOY false
```

### AZURE_AI_FOUNDRY_HUB_PROJECT_DEPLOY

Enable deployment of Projects to the Azure AI Hub resource if it was deployed.
When set to `true`, projects are deployed as child workspaces under the AI Foundry Hub.
Only applies when `AZURE_AI_FOUNDRY_HUB_DEPLOY` is set to `true`.
Default: `false`.

> **Note**: Projects deployed to the Hub have different capabilities compared to projects deployed directly to AI Services. Hub-based projects provide full ML workspace functionality including compute instances, data assets, and model management.

```powershell
azd env set AZURE_AI_FOUNDRY_HUB_DEPLOY true
```

### AZURE_AI_FOUNDRY_PROJECT_NAME

The name of the sample Azure AI Foundry Project. This is used in the resource name, so can not contain spaces or special characters.
Default: `sample-project`.

```powershell
azd env set AZURE_AI_FOUNDRY_PROJECT_NAME "my-ai-project"
```

### AZURE_AI_FOUNDRY_PROJECT_FRIENDLY_NAME

Friendly display name for the sample Azure AI Foundry Project.
Default: `Sample Project`.

```powershell
azd env set AZURE_AI_FOUNDRY_PROJECT_FRIENDLY_NAME "My AI Project"
```

### AZURE_AI_FOUNDRY_PROJECT_DESCRIPTION

Optional description for the sample Azure AI Foundry Project shown in the Azure portal.
Default: `A sample project for Azure AI Foundry`.

```powershell
azd env set AZURE_AI_FOUNDRY_PROJECT_DESCRIPTION "This is my first AI project."
```

### AZURE_AI_FOUNDRY_PROJECTS_FROM_JSON

Use projects defined in infra/sample-ai-foundry-projects.json file instead of the single project parameters.
When set to `true`, the `AZURE_AI_FOUNDRY_PROJECT_NAME`, `AZURE_AI_FOUNDRY_PROJECT_FRIENDLY_NAME`, and `AZURE_AI_FOUNDRY_PROJECT_DESCRIPTION` parameters are ignored.
Default: `false`.

```powershell
azd env set AZURE_AI_FOUNDRY_PROJECTS_FROM_JSON true
```

The `infra/sample-ai-foundry-projects.json` file contains an array of project definitions. Each project definition includes the following properties:

| Property     | Description                                               |
| ------------ | --------------------------------------------------------- |
| Name         | The name of the AI Foundry project (used in resource name)|
| FriendlyName | Display name shown in the Azure portal                    |
| Description  | Optional description shown in the Azure portal            |

Example JSON structure:

```json
[
  {
    "Name": "contoso-retail-analytics",
    "FriendlyName": "Contoso Retail Analytics",
    "Description": "Sample project demonstrating AI-driven product recommendations."
  },
  {
    "Name": "fabrikam-health-insights",
    "FriendlyName": "Fabrikam Health Insights",
    "Description": "Sample healthcare project showcasing patient-note summarisation."
  }
]
```

You can modify this file to define your own set of projects to be created during deployment.

## Azure AI Search Service

### AZURE_AI_SEARCH_SKU

SKU tier for the Azure AI Search service.  
Allowed: `standard` | `standard2` | `standard3` | `storage_optimized_l1` | `storage_optimized_l2`.
Default: `standard`.

```powershell
azd env set AZURE_AI_SEARCH_SKU standard2
```

### AZURE_AI_SEARCH_DEPLOY

Deploy the Azure AI Search service **and** all related role assignments / connections (`true`).  
When set to `false`, no Search resources or privileges are created.

Default: `true`.

```powershell
azd env set AZURE_AI_SEARCH_DEPLOY false
```

## Identity & Access

### AZURE_PRINCIPAL_ID

Object ID (GUID) of the user or service principal to grant access to the AI Foundry hub.
Default: current Azure CLI principal.

```powershell
azd env set AZURE_PRINCIPAL_ID "00000000-0000-0000-0000-000000000000"
```

### AZURE_PRINCIPAL_ID_TYPE

The type of identity in `AZURE_PRINCIPAL_ID`.
Allowed: `user` | `serviceprincipal`.
Default: `user`.

```powershell
azd env set AZURE_PRINCIPAL_ID_TYPE serviceprincipal
```

## Optional Infrastructure

### AZURE_BASTION_HOST_DEPLOY

Deploy an Azure Bastion host for secure RDP/SSH access (`true`).  

Default: `false`.

```powershell
azd env set AZURE_BASTION_HOST_DEPLOY true
```

### AZURE_CONTAINER_REGISTRY_RESOURCE_ID

Provide the full resource-id of an existing Azure Container Registry to associate with the deployment.  
When set, the accelerator **does not** create a new registry.
If `AZURE_NETWORK_ISOLATION` is `true`, ensure the registry already has the required private endpoints and DNS zones.
If `AZURE_CONTAINER_REGISTRY_DEPLOY` is set to `true`, this setting is ignored.

```powershell
azd env set AZURE_CONTAINER_REGISTRY_RESOURCE_ID "/subscriptions/<subId>/resourceGroups/rg-xyz/providers/Microsoft.ContainerRegistry/registries/acrExisting"
```

### AZURE_CONTAINER_REGISTRY_DEPLOY

Deploy a new Azure Container Registry **or** attach an existing one (`true`).  
When set to `true`, `AZURE_CONTAINER_REGISTRY_RESOURCE_ID` is ignored and the AI Foundry Hub is created without an attached registry.

Default: `false`.

```powershell
azd env set AZURE_CONTAINER_REGISTRY_DEPLOY true
```

### AZURE_STORAGE_ACCOUNT_NAME

Override the default storage account name, which is automatically generated from the environment name.
Default: `environment-name`.

```powershell
azd env set AZURE_STORAGE_ACCOUNT_NAME mycustomstorage
```

## Security

### AZURE_KEYVAULT_ENABLE_PURGE_PROTECTION

Enable purge protection on the Key Vault (`true`). When enabled, the vault cannot be permanently deleted until purge protection is disabled.  
Default: `false`.

```powershell
azd env set AZURE_KEYVAULT_ENABLE_PURGE_PROTECTION true
```
