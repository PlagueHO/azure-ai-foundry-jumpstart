# Configuration Options

The following environment variables control the deployment behaviour of the Azure AI Foundry Jumpstart Solution Accelerator. They can be set via standard methods of configuring environment variables or by using `azd env set <NAME> <VALUE>`.

> Example:
>
> ```powershell
> azd env set LOCATION eastus
> ```

The configuration options are grouped into the following categories:

- [Create Sample Data](#create-sample-data)
- [Networking & Isolation](#networking--isolation)
- [Azure AI Foundry Hub Configuration](#azure-ai-foundry-hub-configuration)
- [Azure AI Search Service](#azure-ai-search-service)
- [Identity & Access](#identity--access)
- [Optional Infrastructure](#optional-infrastructure)
- [Security](#security)

## Create Sample Data

These options control the creation of sample data and configuration in the Azure AI Foundry hub.

### DEPLOY_SAMPLE_OPENAI_MODELS

Deploy seme common OpenAI models into the Azure OpenAI Service connected to the Azure AI Foundry Hub.
Default: `false`.

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

The list of models, versions, quota and TPM are defined in the [infra/sample-openai-models.json](../infra/sample-openai-models.json) file. If you wish to define an alternate models, you can edit this file or alternatively set the [AZURE_OPENAI_MODELS](#azure-openai-models) environment variable.

```powershell
azd env set DEPLOY_SAMPLE_OPENAI_MODELS true
```


### DEPLOY_SAMPLE_DATA

Upload sample data into the Azure Storage account connected to the Azure AI Foundry Hub.
Default: `false`.

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

### AZURE_AI_FOUNDRY_HUB_FRIENDLY_NAME

Friendly display name for the AI Foundry hub.  
Default: `''` - the friendly name is automatically generated from the environment name.

```powershell
azd env set AZURE_AI_FOUNDRY_HUB_FRIENDLY_NAME "My AI Hub"
```

### AZURE_AI_FOUNDRY_HUB_DESCRIPTION

Optional description shown in the Azure portal.  
Default: `''` - the friendly name is automatically generated from the environment name.

```powershell
azd env set AZURE_AI_FOUNDRY_HUB_DESCRIPTION "Sandbox hub for PoC work"
```

## Azure AI Search Service

### AZURE_AI_SEARCH_SKU

SKU tier for the Azure AI Search service.  
Allowed: `standard` (default) | `standard2` | `standard3` | `storage_optimized_l1` | `storage_optimized_l2`.

```powershell
azd env set AZURE_AI_SEARCH_SKU standard2
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
Allowed: `user` (default) | `serviceprincipal`.

```powershell
azd env set AZURE_PRINCIPAL_ID_TYPE serviceprincipal
```

## Optional Infrastructure

### AZURE_CREATE_BASTION_HOST

Deploy an Azure Bastion host for secure RDP/SSH access (`true`).  
Default: `false`.

```powershell
azd env set AZURE_CREATE_BASTION_HOST true
```

### AZURE_CONTAINER_REGISTRY_RESOURCE_ID

Provide the full resource-id of an existing Azure Container Registry to associate with the deployment.  
When set, the accelerator **does not** create a new registry.  
If `AZURE_NETWORK_ISOLATION` is `true`, ensure the registry already has the required private endpoints and DNS zones.

```powershell
azd env set AZURE_CONTAINER_REGISTRY_RESOURCE_ID "/subscriptions/<subId>/resourceGroups/rg-xyz/providers/Microsoft.ContainerRegistry/registries/acrExisting"
```

### AZURE_CONTAINER_REGISTRY_DISABLED

Skip deploying **and** associating any Azure Container Registry.  
When `true`, `AZURE_CONTAINER_REGISTRY_RESOURCE_ID` is ignored and the AI Foundry Hub is created without an attached registry.

Default: `false`.

```powershell
azd env set AZURE_CONTAINER_REGISTRY_DISABLED true
```

## Security

### AZURE_KEYVAULT_ENABLE_PURGE_PROTECTION

Enable purge protection on the Key Vault (`true`). When enabled, the vault cannot be permanently deleted until purge protection is disabled.  
Default: `false`.

```powershell
azd env set AZURE_KEYVAULT_ENABLE_PURGE_PROTECTION true
```
