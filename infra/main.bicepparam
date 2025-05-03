using './main.bicep'

// Required parameters
param environmentName = readEnvironmentVariable('AZURE_ENV_NAME', 'env_name')
param location = readEnvironmentVariable('AZURE_LOCATION', 'EastUS2')

// Networking parameters
param azureNetworkIsolation = toLower(readEnvironmentVariable('AZURE_NETWORK_ISOLATION', 'true')) == 'true'

// Optional parameters
param aiFoundryHubFriendlyName = readEnvironmentVariable('AZURE_AI_FOUNDRY_HUB_FRIENDLY_NAME', '')
param aiFoundryHubDescription = readEnvironmentVariable('AZURE_AI_FOUNDRY_HUB_DESCRIPTION', '')
param aiFoundryHubIpAllowList = empty(readEnvironmentVariable('AZURE_AI_FOUNDRY_HUB_IP_ALLOW_LIST', '')) ? [] : split(readEnvironmentVariable('AZURE_AI_FOUNDRY_HUB_IP_ALLOW_LIST',''), ',')
param principalId = readEnvironmentVariable('AZURE_PRINCIPAL_ID', '')
param principalIdType = toLower(readEnvironmentVariable('AZURE_PRINCIPAL_ID_TYPE', 'user')) == 'serviceprincipal' ? 'ServicePrincipal' : 'User'

// Bastion host parameters
param createBastionHost = toLower(readEnvironmentVariable('AZURE_CREATE_BASTION_HOST', 'false')) == 'true'

// Security parameters
param disableApiKeys = toLower(readEnvironmentVariable('AZURE_DISABLE_API_KEYS', 'false')) == 'true'
param keyVaultEnablePurgeProtection = toLower(readEnvironmentVariable('AZURE_KEYVAULT_ENABLE_PURGE_PROTECTION', 'false')) == 'true'
