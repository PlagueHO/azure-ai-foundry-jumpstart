using './main.bicep'

// Required parameters
param environmentName = readEnvironmentVariable('AZURE_ENV_NAME', 'azdtemp')
param location = readEnvironmentVariable('AZURE_LOCATION', 'EastUS2')

// User or service principal deploying the resources
param principalId = readEnvironmentVariable('AZURE_PRINCIPAL_ID', '')
param principalIdType = toLower(readEnvironmentVariable('AZURE_PRINCIPAL_ID_TYPE', 'user')) == 'serviceprincipal' ? 'ServicePrincipal' : 'User'

// Networking parameters
param azureNetworkIsolation = toLower(readEnvironmentVariable('AZURE_NETWORK_ISOLATION', 'true')) == 'true'
param aiFoundryIpAllowList = empty(readEnvironmentVariable('AZURE_AI_FOUNDRY_IP_ALLOW_LIST', '')) ? [] : split(readEnvironmentVariable('AZURE_AI_FOUNDRY_IP_ALLOW_LIST',''), ',')

// Supporting resources parameters
param keyVaultEnablePurgeProtection = toLower(readEnvironmentVariable('AZURE_KEYVAULT_ENABLE_PURGE_PROTECTION', 'false')) == 'true'

// AI resources parameters
param azureAiSearchSku = toLower(readEnvironmentVariable('AZURE_AI_SEARCH_SKU', 'standard'))
param azureAiSearchDeploy = toLower(readEnvironmentVariable('AZURE_AI_SEARCH_DEPLOY', 'true')) == 'true'
param azureAiSearchReplicaCount = int(readEnvironmentVariable('AZURE_AI_SEARCH_REPLICA_COUNT', '1'))
param azureAiSearchPartitionCount = int(readEnvironmentVariable('AZURE_AI_SEARCH_PARTITION_COUNT', '1'))

// Storage account override (use 'default' to keep the generated name)
param azureStorageAccountName = readEnvironmentVariable('AZURE_STORAGE_ACCOUNT_NAME', '') == '' ? 'default' : readEnvironmentVariable('AZURE_STORAGE_ACCOUNT_NAME', '')

// Azure AI Foundry Hub parameters
param aiFoundryHubDeploy = toLower(readEnvironmentVariable('AZURE_AI_FOUNDRY_HUB_DEPLOY', 'false')) == 'true'
param aiFoundryHubFriendlyName = readEnvironmentVariable('AZURE_AI_FOUNDRY_HUB_FRIENDLY_NAME', '')
param aiFoundryHubDescription = readEnvironmentVariable('AZURE_AI_FOUNDRY_HUB_DESCRIPTION', '')
param aiFoundryHubProjectDeploy = toLower(readEnvironmentVariable('AZURE_AI_FOUNDRY_HUB_PROJECT_DEPLOY', 'false')) == 'true'

// AI Foundry project parameters
param aiFoundryProjectDeploy = toLower(readEnvironmentVariable('AZURE_AI_FOUNDRY_PROJECT_DEPLOY', 'true')) == 'true'
param aiFoundryProjectName = readEnvironmentVariable('AZURE_AI_FOUNDRY_PROJECT_NAME', 'sample-project') 
param aiFoundryProjectDescription = readEnvironmentVariable('AZURE_AI_FOUNDRY_PROJECT_DESCRIPTION', 'A sample project for Azure AI Foundry')
param aiFoundryProjectFriendlyName = readEnvironmentVariable('AZURE_AI_FOUNDRY_PROJECT_FRIENDLY_NAME', 'Sample Project')
param aiFoundryProjectsFromJson = toLower(readEnvironmentVariable('AZURE_AI_FOUNDRY_PROJECTS_FROM_JSON', 'false')) == 'true'

// Sample data parameters
param deploySampleOpenAiModels = toLower(readEnvironmentVariable('DEPLOY_SAMPLE_OPENAI_MODELS', 'true')) == 'true'
param deploySampleData = toLower(readEnvironmentVariable('DEPLOY_SAMPLE_DATA', 'false')) == 'true'

// Bastion host parameters
param bastionHostDeploy = toLower(readEnvironmentVariable('AZURE_BASTION_HOST_DEPLOY', 'false')) == 'true'

// Security parameters
param disableApiKeys = toLower(readEnvironmentVariable('AZURE_DISABLE_API_KEYS', 'false')) == 'true'

// Container registry parameters
param containerRegistryDeploy   = toLower(readEnvironmentVariable('AZURE_CONTAINER_REGISTRY_DEPLOY', 'false')) == 'true'
param containerRegistryResourceId = readEnvironmentVariable('AZURE_CONTAINER_REGISTRY_RESOURCE_ID', '')
