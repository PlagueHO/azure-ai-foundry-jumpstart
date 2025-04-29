metadata name = 'AI Foundry Hub'
metadata description = 'This module deploys an Azure AI Foundry Hub workspace with associated resources and connections.'

@description('Azure region of the deployment.')
param location string = resourceGroup().location

@description('Tags to add to the resources.')
param tags object = {}

@description('Name of the AI Foundry Hub workspace.')
param name string

@description('Friendly display name of the AI Foundry Hub workspace.')
param aiHubFriendlyName string = name

@description('Description of the AI Foundry Hub workspace.')
param aiHubDescription string = name

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

import { diagnosticSettingFullType } from 'br/public:avm/utl/types/avm-common-types:0.5.1'

@description('Optional. Diagnostic settings configuration for the AI Foundry Hub workspace.')
param diagnosticSettings diagnosticSettingFullType[]?

import { privateEndpointSingleServiceType } from 'br/public:avm/utl/types/avm-common-types:0.5.1'

@description('Optional. Configuration details for private endpoints. For security reasons, it is recommended to use private endpoints whenever possible.')
param privateEndpoints privateEndpointSingleServiceType[]?

var enableReferencedModulesTelemetry = false

resource aiHub 'Microsoft.MachineLearningServices/workspaces@2025-01-01-preview' = {
  name: name
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
    name: '${name}-connection-AzureOpenAI'
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

// Diagnostic settings for AI Foundry Hub workspace
resource aiHubDiagnosticSettings 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = [for (diagnosticSetting, index) in (diagnosticSettings ?? []): {
  name: diagnosticSetting.?name ?? '${name}-diagnosticSettings-${index}'
  scope: aiHub
  properties: {
    storageAccountId: diagnosticSetting.?storageAccountResourceId
    workspaceId: diagnosticSetting.?workspaceResourceId
    eventHubAuthorizationRuleId: diagnosticSetting.?eventHubAuthorizationRuleId
    eventHubName: diagnosticSetting.?eventHubName
    logs: [for log in (diagnosticSetting.?logCategoriesAndGroups ?? []): {
      categoryGroup: log.?categoryGroup
      enabled: log.?enabled ?? true
    }]
    metrics: [for metric in (diagnosticSetting.?metricCategories ?? []): {
      category: metric.category
      enabled: metric.?enabled ?? true
    }]
  }
}]

module aiHubPrivateEndpoints 'br/public:avm/res/network/private-endpoint:0.10.1' = [
  for (privateEndpoint, index) in (privateEndpoints ?? []): {
    name: '${uniqueString(deployment().name, location)}-aiHub-PrivateEndpoint-${index}'
    scope: resourceGroup(
      split(privateEndpoint.?resourceGroupResourceId ?? resourceGroup().id, '/')[2],
      split(privateEndpoint.?resourceGroupResourceId ?? resourceGroup().id, '/')[4]
    )
    params: {
      name: privateEndpoint.?name ?? 'pep-${last(split(aiHub.id, '/'))}-${privateEndpoint.?service ?? 'amlworkspace'}-${index}'
      privateLinkServiceConnections: privateEndpoint.?isManualConnection != true
        ? [
            {
              name: privateEndpoint.?privateLinkServiceConnectionName ?? '${last(split(aiHub.id, '/'))}-${privateEndpoint.?service ?? 'amlworkspace'}-${index}'
              properties: {
                privateLinkServiceId: aiHub.id
                groupIds: [
                  privateEndpoint.?service ?? 'amlworkspace'
                ]
              }
            }
          ]
        : null
      manualPrivateLinkServiceConnections: privateEndpoint.?isManualConnection == true
        ? [
            {
              name: privateEndpoint.?privateLinkServiceConnectionName ?? '${last(split(aiHub.id, '/'))}-${privateEndpoint.?service ?? 'amlworkspace'}-${index}'
              properties: {
                privateLinkServiceId: aiHub.id
                groupIds: [
                  privateEndpoint.?service ?? 'amlworkspace'
                ]
                requestMessage: privateEndpoint.?manualConnectionRequestMessage ?? 'Manual approval required.'
              }
            }
          ]
        : null
      subnetResourceId: privateEndpoint.subnetResourceId
      enableTelemetry: enableReferencedModulesTelemetry
      location: privateEndpoint.?location ?? reference(
        split(privateEndpoint.subnetResourceId, '/subnets/')[0],
        '2020-06-01',
        'Full'
      ).location
      lock: privateEndpoint.?lock
      privateDnsZoneGroup: privateEndpoint.?privateDnsZoneGroup
      roleAssignments: privateEndpoint.?roleAssignments
      tags: privateEndpoint.?tags ?? tags
      customDnsConfigs: privateEndpoint.?customDnsConfigs
      ipConfigurations: privateEndpoint.?ipConfigurations
      applicationSecurityGroupResourceIds: privateEndpoint.?applicationSecurityGroupResourceIds
      customNetworkInterfaceName: privateEndpoint.?customNetworkInterfaceName
    }
  }
]

// Outputs moved to the end of the file for improved readability and consistency
@description('Resource ID of the deployed AI Foundry Hub workspace.')
output aiHubID string = aiHub.id

@description('Principal ID of the system-assigned identity for the AI Foundry Hub workspace.')
output aiHubPrincipalId string = aiHub.identity.principalId

@description('The private endpoints of the AI Foundry Hub workspace.')
output privateEndpoints array = [
  for (pe, index) in (privateEndpoints ?? []): {
    name: aiHubPrivateEndpoints[index].outputs.name
    resourceId: aiHubPrivateEndpoints[index].outputs.resourceId
    groupId: aiHubPrivateEndpoints[index].outputs.?groupId!
    customDnsConfigs: aiHubPrivateEndpoints[index].outputs.customDnsConfigs
    networkInterfaceResourceIds: aiHubPrivateEndpoints[index].outputs.networkInterfaceResourceIds
  }
]
