using './main.bicep'

// Required parameters
param environmentName = readEnvironmentVariable('AZURE_ENV_NAME', 'azdtemp')
param location = readEnvironmentVariable('AZURE_LOCATION', 'EastUS2')

// User or service principal deploying the resources
param principalId = readEnvironmentVariable('AZURE_PRINCIPAL_ID', '')
param principalIdType = toLower(readEnvironmentVariable('AZURE_PRINCIPAL_ID_TYPE', 'user')) == 'serviceprincipal' ? 'ServicePrincipal' : 'User'

// Networking parameters
param azureNetworkIsolation = toLower(readEnvironmentVariable('AZURE_NETWORK_ISOLATION', 'true')) == 'true'

// AI resources parameters
param azureAiSearchSku = toLower(readEnvironmentVariable('AZURE_AI_SEARCH_SKU', 'standard'))
param azureAiSearchDeploy = toLower(readEnvironmentVariable('AZURE_AI_SEARCH_DEPLOY', 'true')) == 'true'

// Storage account toggle and override
param azureStorageAccountDeploy = toLower(readEnvironmentVariable('AZURE_STORAGE_ACCOUNT_DEPLOY', 'true')) == 'true'
param azureStorageAccountName = readEnvironmentVariable('AZURE_STORAGE_ACCOUNT_NAME', 'default')

// AI Foundry project parameters
param aiFoundryProjectDeploy = toLower(readEnvironmentVariable('AZURE_AI_FOUNDRY_PROJECT_DEPLOY', 'true')) == 'true'
param aiFoundryProjectName = readEnvironmentVariable('AZURE_AI_FOUNDRY_PROJECT_NAME', 'sample-project') 
param aiFoundryProjectDisplayName = readEnvironmentVariable('AZURE_AI_FOUNDRY_PROJECT_DISPLAY_NAME', 'Sample Project')
param aiFoundryProjectDescription = readEnvironmentVariable('AZURE_AI_FOUNDRY_PROJECT_DESCRIPTION', 'A sample project for Azure AI Foundry')
param aiFoundryProjectsFromJson = toLower(readEnvironmentVariable('AZURE_AI_FOUNDRY_PROJECTS_FROM_JSON', 'false')) == 'true'

// Sample data parameters
param sampleOpenAiModelsDeploy = toLower(readEnvironmentVariable('SAMPLE_OPENAI_MODELS_DEPLOY', 'true')) == 'true'
param sampleDataDeploy = toLower(readEnvironmentVariable('SAMPLE_DATA_DEPLOY', 'false')) == 'true'

// Bastion host parameters
param bastionHostDeploy = toLower(readEnvironmentVariable('AZURE_BASTION_HOST_DEPLOY', 'false')) == 'true'

// Security parameters
param disableApiKeys = toLower(readEnvironmentVariable('AZURE_DISABLE_API_KEYS', 'false')) == 'true'
