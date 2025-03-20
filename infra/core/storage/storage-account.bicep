metadata description = 'Creates an Azure storage account.'

@description('Name of the Azure storage account.')
param name string

@description('Location where the Azure storage account should be deployed.')
param location string = resourceGroup().location

@description('Tags to apply to the Azure storage account.')
param tags object = {}

@description('The access tier for the storage account.')
@allowed([
  'Cool'
  'Hot'
  'Premium'
])
param accessTier string = 'Hot'

@description('Allow or disallow public access to blobs.')
param allowBlobPublicAccess bool = true

@description('Allow or disallow cross-tenant replication.')
param allowCrossTenantReplication bool = true

@description('Allow or disallow shared key access.')
param allowSharedKeyAccess bool = true

@description('List of blob containers to create in the storage account.')
param containers array = []

@description('CORS rules to apply to blob and file services.')
param corsRules array = []

@description('Default to OAuth authentication when accessing storage account.')
param defaultToOAuthAuthentication bool = false

@description('Delete retention policy settings for blob service.')
param deleteRetentionPolicy object = {}

@description('The type of DNS endpoint to use.')
@allowed([
  'AzureDnsZone'
  'Standard'
])
param dnsEndpointType string = 'Standard'

@description('List of file shares to create in the storage account.')
param files array = []

@description('Enable or disable hierarchical namespace (HNS) for Data Lake Storage Gen2.')
param isHnsEnabled bool = false

@description('The kind of storage account to create.')
param kind string = 'StorageV2'

@description('Minimum TLS version required for requests to the storage account.')
param minimumTlsVersion string = 'TLS1_2'

@description('List of queues to create in the storage account.')
param queues array = []

@description('Delete retention policy settings for file service.')
param shareDeleteRetentionPolicy object = {}

@description('Allow only HTTPS traffic to the storage account.')
param supportsHttpsTrafficOnly bool = true

@description('List of tables to create in the storage account.')
param tables array = []

@description('Network ACLs configuration for the storage account.')
param networkAcls object = {
  bypass: 'AzureServices'
  defaultAction: 'Allow'
}

@description('Enable or disable public network access to the storage account.')
@allowed([
  'Enabled'
  'Disabled'
])
param publicNetworkAccess string = 'Enabled'

@description('The SKU of the storage account.')
param sku object = {
  name: 'Standard_LRS'
}

@description('Flag indicating whether to create a private endpoint for the storage account.')
param enablePrivateEndpoint bool = false

@description('The name of the virtual netork where the private endpoint will be created.')
param privateEndpointVnetName string = ''

@description('The name of the subnet where the private endpoint will be created.')
param privateEndpointSubnetName string = ''

@description('The name of the private endpoint resource.')
param privateEndpointName string = '${name}-pe'

@description('The ID of the Log Analytics workspace to send diagnostic logs to.')
param logAnalyticsWorkspaceId string = ''

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: name
  location: location
  tags: tags
  kind: kind
  sku: sku
  properties: {
    accessTier: accessTier
    allowBlobPublicAccess: allowBlobPublicAccess
    allowCrossTenantReplication: allowCrossTenantReplication
    allowSharedKeyAccess: allowSharedKeyAccess
    defaultToOAuthAuthentication: defaultToOAuthAuthentication
    dnsEndpointType: dnsEndpointType
    isHnsEnabled: isHnsEnabled
    minimumTlsVersion: minimumTlsVersion
    networkAcls: networkAcls
    publicNetworkAccess: publicNetworkAccess
    supportsHttpsTrafficOnly: supportsHttpsTrafficOnly
  }

  resource blobServices 'blobServices@2023-05-01' = if (!empty(containers)) {
    name: 'default'
    properties: {
      cors: {
        corsRules: corsRules
      }
      deleteRetentionPolicy: deleteRetentionPolicy
    }

    resource container 'containers@2023-05-01' = [for container in containers: {
      name: container.name
      properties: {
        publicAccess: container.?publicAccess ?? 'None'
      }
    }]
  }

  resource fileServices 'fileServices@2023-05-01' = if (!empty(files)) {
    name: 'default'
    properties: {
      cors: {
        corsRules: corsRules
      }
      shareDeleteRetentionPolicy: shareDeleteRetentionPolicy
    }
  }

  resource queueServices 'queueServices@2023-05-01' = if (!empty(queues)) {
    name: 'default'
    properties: {}

    resource queue 'queues' = [for queue in queues: {
      name: queue.name
      properties: {
        metadata: {}
      }
    }]
  }

  resource tableServices 'tableServices@2023-05-01' = if (!empty(tables)) {
    name: 'default'
    properties: {}
  }
}

// Diagnostic settings for storage account blob service
var blobServiceDiagnosticSettingsName = 'blobServiceDiagnosticSettings'
var blobServiceLogCategories = [
  'StorageRead'
  'StorageWrite'
  'StorageDelete'
]
var blobServiceMetricCategories = [
  'Transaction'
]
var blobServiceLogs = [for category in blobServiceLogCategories: {
  category: category
  enabled: true
}]
var blobServiceMetrics = [for category in blobServiceMetricCategories: {
  category: category
  enabled: true
}]

resource blobServiceDiagnosticSettings 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = if (!empty(logAnalyticsWorkspaceId)) {
  name: blobServiceDiagnosticSettingsName
  scope: storageAccount::blobServices
  properties: {
    workspaceId: logAnalyticsWorkspaceId
    logs: blobServiceLogs
    metrics: blobServiceMetrics
  }
}

// Enable Storage Account blob service private endpoint if specified
module blobServicePrivateEndpoint 'storage-account-private-endpoint.bicep' = if (enablePrivateEndpoint) {
  name: privateEndpointName
  scope: resourceGroup()
  params: {
    virtualNetworkName: privateEndpointVnetName
    subnetName: privateEndpointSubnetName
    storageAccountPrivateEndpointName: privateEndpointName
    storageAccountId: storageAccount.id
    location: location
    tags: tags
  }
}

output id string = storageAccount.id
output name string = storageAccount.name
output primaryEndpoints object = storageAccount.properties.primaryEndpoints
