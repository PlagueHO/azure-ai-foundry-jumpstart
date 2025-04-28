metadata name = 'AI Foundry Hub'
metadata description = 'This module deploys an Azure AI Foundry Hub workspace with associated resources and connections.'

@description('Azure region of the deployment.')
param location string = resourceGroup().location

@description('Tags to add to the resources.')
param tags object = {}

@description('Name of the AI Foundry Hub workspace.')
param aiHubName string

@description('Friendly display name of the AI Foundry Hub workspace.')
param aiHubFriendlyName string = aiHubName

@description('Description of the AI Foundry Hub workspace.')
param aiHubDescription string

@description('Resource ID of the Application Insights instance for diagnostics logging.')
param applicationInsightsId string

@description('Resource ID of the Azure Container Registry for Docker images.')
param containerRegistryId string

@description('Resource ID of the Azure Key Vault for secure storage of secrets and connection strings.')
param keyVaultId string

@description('Resource ID of the Azure Storage Account for storing experimentation outputs.')
param storageAccountId string

@description('Resource ID of the Azure AI Services instance.')
param aiServicesId string

@description('Resource ID of the Azure AI Services endpoint.')
param aiServicesTarget string

@description('Optional. Enable or disable public network access. Recommended to disable for security.')
@allowed([
  'Enabled'
  'Disabled'
])
param publicNetworkAccess string = 'Disabled'

resource aiHub 'Microsoft.MachineLearningServices/workspaces@2023-08-01-preview' = {
  name: aiHubName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  kind: 'hub'
  properties: {
    friendlyName: aiHubFriendlyName
    description: aiHubDescription
    keyVault: keyVaultId
    storageAccount: storageAccountId
    applicationInsights: applicationInsightsId
    containerRegistry: containerRegistryId
    publicNetworkAccess: publicNetworkAccess
  }

  resource aiServicesConnection 'connections@2024-01-01-preview' = {
    name: '${aiHubName}-connection-AzureOpenAI'
    properties: {
      category: 'AzureOpenAI'
      target: aiServicesTarget
      authType: 'ApiKey'
      isSharedToAll: true
      credentials: {
        key: '${listKeys(aiServicesId, '2021-10-01').key1}'
      }
      metadata: {
        ApiType: 'Azure'
        ResourceId: aiServicesId
      }
    }
  }
}

@description('Resource ID of the deployed AI Foundry Hub workspace.')
output aiHubID string = aiHub.id

@description('Principal ID of the system-assigned identity for the AI Foundry Hub workspace.')
output aiHubPrincipalId string = aiHub.identity.principalId
