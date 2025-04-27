metadata description = 'Creates an Azure Container Registry.'

@description('Name of the Azure Container Registry.')
param name string

@description('Location where the Azure Container Registry should be deployed.')
param location string = resourceGroup().location

@description('Tags to apply to the Azure Container Registry.')
param tags object = {}

@description('Indicates whether admin user is enabled.')
param adminUserEnabled bool = false

@description('Indicates whether anonymous pull is enabled.')
param anonymousPullEnabled bool = false

@description('Azure AD authentication as ARM policy settings.')
param azureADAuthenticationAsArmPolicy object = {
  status: 'enabled'
}

@description('Indicates whether data endpoint is enabled.')
param dataEndpointEnabled bool = false

@description('Encryption settings.')
param encryption object = {
  status: 'disabled'
}

@description('Export policy settings.')
param exportPolicy object = {
  status: 'enabled'
}

@description('Metadata search settings.')
param metadataSearch string = 'Disabled'

@description('Options for bypassing network rules.')
param networkRuleBypassOptions string = 'AzureServices'

@description('Public network access setting.')
param publicNetworkAccess string = 'Enabled'

@description('Quarantine policy settings.')
param quarantinePolicy object = {
  status: 'disabled'
}

@description('Retention policy settings.')
param retentionPolicy object = {
  days: 7
  status: 'disabled'
}

@description('Scope maps setting.')
param scopeMaps array = []

@description('SKU settings.')
param sku object = {
  name: 'Basic'
}

@description('Soft delete policy settings.')
param softDeletePolicy object = {
  retentionDays: 7
  status: 'disabled'
}

@description('Trust policy settings.')
param trustPolicy object = {
  type: 'Notary'
  status: 'disabled'
}

@description('Zone redundancy setting.')
param zoneRedundancy string = 'Disabled'

@description('The log analytics workspace ID used for logging and monitoring.')
param workspaceId string = ''

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-11-01-preview' = {
  name: name
  location: location
  tags: tags
  sku: sku
  properties: {
    adminUserEnabled: adminUserEnabled
    anonymousPullEnabled: anonymousPullEnabled
    dataEndpointEnabled: dataEndpointEnabled
    encryption: encryption
    metadataSearch: metadataSearch
    networkRuleBypassOptions: networkRuleBypassOptions
    policies: {
      quarantinePolicy: quarantinePolicy
      trustPolicy: trustPolicy
      retentionPolicy: retentionPolicy
      exportPolicy: exportPolicy
      azureADAuthenticationAsArmPolicy: azureADAuthenticationAsArmPolicy
      softDeletePolicy: softDeletePolicy
    }
    publicNetworkAccess: publicNetworkAccess
    zoneRedundancy: zoneRedundancy
  }

  resource scopeMap 'scopeMaps' = [for scopeMap in scopeMaps: {
    name: scopeMap.name
    properties: scopeMap.properties
  }]
}

// Diagnostic settings for container registry
var diagnosticSettingsName = 'registry-diagnostics'
var logCategories = [
  'ContainerRegistryRepositoryEvents'
  'ContainerRegistryLoginEvents'
]
var metricCategories = [
  'AllMetrics'
]
var logs = [for category in logCategories: {
  category: category
  enabled: true
}]
var metrics = [for category in metricCategories: {
  category: category
  enabled: true
  timeGrain: 'PT1M'
}]

resource diagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = if (!empty(workspaceId)) {
  name: diagnosticSettingsName
  scope: containerRegistry
  properties: {
    workspaceId: workspaceId
    logs: logs
    metrics: metrics
  }
}

@description('The resource ID of the Azure Container Registry.')
output id string = containerRegistry.id

@description('The login server URI of the Azure Container Registry.')
output loginServer string = containerRegistry.properties.loginServer

@description('The name of the Azure Container Registry.')
output name string = containerRegistry.name
