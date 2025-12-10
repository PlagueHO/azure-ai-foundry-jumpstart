using './main.bicep'

// Required parameters
param environmentName = readEnvironmentVariable('AZURE_ENV_NAME', 'azdtemp')
param location = readEnvironmentVariable('AZURE_LOCATION', 'EastUS2')

// User or service principal deploying the resources
param principalId = readEnvironmentVariable('AZURE_PRINCIPAL_ID', '')
param principalIdType = toLower(readEnvironmentVariable('AZURE_PRINCIPAL_ID_TYPE', 'user')) == 'serviceprincipal' ? 'ServicePrincipal' : 'User'

// Networking parameters
param azureNetworkIsolation = toLower(readEnvironmentVariable('AZURE_NETWORK_ISOLATION', 'true')) == 'true'
param foundryIpAllowList = empty(readEnvironmentVariable('MICROSOFT_FOUNDRY_IP_ALLOW_LIST', '')) ? [] : split(readEnvironmentVariable('MICROSOFT_FOUNDRY_IP_ALLOW_LIST',''), ',')

// AI resources parameters
param azureAiSearchSku = toLower(readEnvironmentVariable('AZURE_AI_SEARCH_SKU', 'standard'))
param azureAiSearchDeploy = toLower(readEnvironmentVariable('AZURE_AI_SEARCH_DEPLOY', 'true')) == 'true'
param azureAiSearchReplicaCount = int(readEnvironmentVariable('AZURE_AI_SEARCH_REPLICA_COUNT', '1'))
param azureAiSearchPartitionCount = int(readEnvironmentVariable('AZURE_AI_SEARCH_PARTITION_COUNT', '1'))

// Storage account override (use 'default' to keep the generated name)
param azureStorageAccountName = readEnvironmentVariable('AZURE_STORAGE_ACCOUNT_NAME', '') == '' ? 'default' : readEnvironmentVariable('AZURE_STORAGE_ACCOUNT_NAME', '')

// Foundry project parameters
param foundryProjectDeploy = toLower(readEnvironmentVariable('MICROSOFT_FOUNDRY_PROJECT_DEPLOY', 'true')) == 'true'
param foundryProjectName = readEnvironmentVariable('MICROSOFT_FOUNDRY_PROJECT_NAME', 'sample-project') 
param foundryProjectDescription = readEnvironmentVariable('MICROSOFT_FOUNDRY_PROJECT_DESCRIPTION', 'A sample project for Microsoft Foundry')
param foundryProjectFriendlyName = readEnvironmentVariable('MICROSOFT_FOUNDRY_PROJECT_FRIENDLY_NAME', 'Sample Project')
param foundryProjectsFromJson = toLower(readEnvironmentVariable('MICROSOFT_FOUNDRY_PROJECTS_FROM_JSON', 'false')) == 'true'

// Sample data parameters
param deploySampleModels = toLower(readEnvironmentVariable('DEPLOY_SAMPLE_MODELS', 'true')) == 'true'
param deploySampleData = toLower(readEnvironmentVariable('DEPLOY_SAMPLE_DATA', 'false')) == 'true'

// Bastion host parameters
param bastionHostDeploy = toLower(readEnvironmentVariable('AZURE_BASTION_HOST_DEPLOY', 'false')) == 'true'

// Security parameters
param disableApiKeys = toLower(readEnvironmentVariable('AZURE_DISABLE_API_KEYS', 'false')) == 'true'
