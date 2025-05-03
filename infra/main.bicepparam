using './main.bicep'

// Required parameters
param environmentName = readEnvironmentVariable('AZURE_ENV_NAME', 'env_name')
param location = readEnvironmentVariable('AZURE_LOCATION', 'location')
param resourceGroupName = readEnvironmentVariable('AZURE_RESOURCE_GROUP_NAME', 'resource_group_name')

// Optional parameters
param aiFoundryHubFriendlyName = readEnvironmentVariable('AZURE_AI_FOUNDRY_HUB_FRIENDLY_NAME', 'ai_foundry_hub_friendly_name')
param aiFoundryHubDescription = readEnvironmentVariable('AZURE_AI_FOUNDRY_HUB_DESCRIPTION', 'ai_foundry_hub_description')
param principalId = readEnvironmentVariable('AZURE_PRINCIPAL_ID', 'principal_id')
param principalIdType = toLower(readEnvironmentVariable('AZURE_PRINCIPAL_ID_TYPE', 'user')) == 'serviceprincipal' ? 'ServicePrincipal' : 'User'

// Networking parameters
param azureNetworkIsolation = toLower(readEnvironmentVariable('AZURE_NETWORK_ISOLATION', 'true')) == 'true'
param createBastionHost = toLower(readEnvironmentVariable('AZURE_CREATE_BASTION_HOST', 'false')) == 'true'

// Security parameters
param disableApiKeys = toLower(readEnvironmentVariable('AZURE_DISABLE_API_KEYS', 'false')) == 'true'
