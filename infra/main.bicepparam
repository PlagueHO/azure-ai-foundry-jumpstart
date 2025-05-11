using './main.bicep'

// Required parameters
param environmentName = readEnvironmentVariable('AZURE_ENV_NAME', 'env_name')
param location = readEnvironmentVariable('AZURE_LOCATION', 'EastUS2')

// Networking parameters
param azureNetworkIsolation = toLower(readEnvironmentVariable('AZURE_NETWORK_ISOLATION', 'true')) == 'true'

// Optional parameters
param keyVaultEnablePurgeProtection = toLower(readEnvironmentVariable('AZURE_KEYVAULT_ENABLE_PURGE_PROTECTION', 'false')) == 'true'
param aiFoundryHubFriendlyName = readEnvironmentVariable('AZURE_AI_FOUNDRY_HUB_FRIENDLY_NAME', '')
param aiFoundryHubDescription = readEnvironmentVariable('AZURE_AI_FOUNDRY_HUB_DESCRIPTION', '')
param aiFoundryHubIpAllowList = empty(readEnvironmentVariable('AZURE_AI_FOUNDRY_HUB_IP_ALLOW_LIST', '')) ? [] : split(readEnvironmentVariable('AZURE_AI_FOUNDRY_HUB_IP_ALLOW_LIST',''), ',')
param aiSearchSku = toLower(readEnvironmentVariable('AZURE_AI_SEARCH_SKU', 'standard'))
param aiFoundryProjectName = readEnvironmentVariable('AZURE_AI_FOUNDRY_PROJECT_NAME', '') 
param aiFoundryProjectDescription = readEnvironmentVariable('AZURE_AI_FOUNDRY_PROJECT_DESCRIPTION', '')
param aiFoundryProjectFriendlyName = readEnvironmentVariable('AZURE_AI_FOUNDRY_PROJECT_FRIENDLY_NAME', '')
// Sample data parameters
param deploySampleOpenAiModels = toLower(readEnvironmentVariable('DEPLOY_SAMPLE_OPENAI_MODELS', 'false')) == 'true'
param deploySampleData = toLower(readEnvironmentVariable('DEPLOY_SAMPLE_DATA', 'false')) == 'true'

// Bastion host parameters
param createBastionHost = toLower(readEnvironmentVariable('AZURE_CREATE_BASTION_HOST', 'false')) == 'true'

// Security parameters
param disableApiKeys = toLower(readEnvironmentVariable('AZURE_DISABLE_API_KEYS', 'false')) == 'true'
param principalId = readEnvironmentVariable('AZURE_PRINCIPAL_ID', '')
param principalIdType = toLower(readEnvironmentVariable('AZURE_PRINCIPAL_ID_TYPE', 'user')) == 'serviceprincipal' ? 'ServicePrincipal' : 'User'

// Container registry parameters
param containerRegistryResourceId = readEnvironmentVariable('AZURE_CONTAINER_REGISTRY_RESOURCE_ID', '')
param containerRegistryDisabled = toLower(readEnvironmentVariable('AZURE_CONTAINER_REGISTRY_DISABLED', 'false')) == 'true'
