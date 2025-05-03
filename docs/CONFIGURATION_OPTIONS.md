# Configuration Options

The following environment variables control the deployment behaviour of the Azure AI Foundry Jumpstart Solution Accelerator. They can be set via standard methods of configuring environment variables or by using `azd env set <NAME> <VALUE>`.

> Example:
>
> ```powershell
> azd env set LOCATION eastus
> ```

The configuration options are grouped into the following categories:

- [Networking & Isolation](#networking--isolation)
- [Azure AI Foundry Hub Configuration](#azure-ai-foundry-hub-configuration)
- [Azure AI Search Service](#azure-ai-search-service)
- [Identity & Access](#identity--access)
- [Optional Infrastructure](#optional-infrastructure)
- [Security](#security)

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

## Security

### AZURE_KEYVAULT_ENABLE_PURGE_PROTECTION

Enable purge protection on the Key Vault (`true`). When enabled, the vault cannot be permanently deleted until purge protection is disabled.  
Default: `false`.

```powershell
azd env set AZURE_KEYVAULT_ENABLE_PURGE_PROTECTION true
```
