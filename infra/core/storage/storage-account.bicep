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
param sku object = { name: 'Standard_LRS' }

@description('Flag indicating whether to create a private endpoint for the storage account.')
param enablePrivateEndpoint bool = false

@description('The resource ID of the subnet to deploy the private endpoint into.')
param privateEndpointSubnetId string = ''

@description('The name of the private endpoint resource.')
param privateEndpointName string = '${name}-pe'

@description('The name of the private DNS zone group for the private endpoint.')
param privateDnsZoneGroupName string = 'default'

@description('The resource IDs of the private DNS zones to link to the private endpoint.')
param privateDnsZoneIds array = []

resource storage 'Microsoft.Storage/storageAccounts@2023-01-01' = {
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

  resource blobServices 'blobServices' = if (!empty(containers)) {
    name: 'default'
    properties: {
      cors: {
        corsRules: corsRules
      }
      deleteRetentionPolicy: deleteRetentionPolicy
    }
    resource container 'containers' = [for container in containers: {
      name: container.name
      properties: {
        publicAccess: container.?publicAccess ?? 'None'
      }
    }]
  }

  resource fileServices 'fileServices' = if (!empty(files)) {
    name: 'default'
    properties: {
      cors: {
        corsRules: corsRules
      }
      shareDeleteRetentionPolicy: shareDeleteRetentionPolicy
    }
  }

  resource queueServices 'queueServices' = if (!empty(queues)) {
    name: 'default'
    properties: {

    }
    resource queue 'queues' = [for queue in queues: {
      name: queue.name
      properties: {
        metadata: {}
      }
    }]
  }

  resource tableServices 'tableServices' = if (!empty(tables)) {
    name: 'default'
    properties: {}
  }
}

resource storagePrivateEndpoint 'Microsoft.Network/privateEndpoints@2023-04-01' = if (enablePrivateEndpoint) {
  name: privateEndpointName
  location: location
  tags: tags
  properties: {
    subnet: {
      id: privateEndpointSubnetId
    }
    privateLinkServiceConnections: [
      {
        name: '${name}-plsc'
        properties: {
          privateLinkServiceId: storage.id
          groupIds: [
            'blob'
            'file'
            'queue'
            'table'
          ]
        }
      }
    ]
  }

  resource privateDnsZoneGroup 'privateDnsZoneGroups' = if (!empty(privateDnsZoneIds)) {
    name: privateDnsZoneGroupName
    properties: {
      privateDnsZoneConfigs: [for dnsZoneId in privateDnsZoneIds: {
        name: last(split(dnsZoneId, '/'))
        properties: {
          privateDnsZoneId: dnsZoneId
        }
      }]
    }
  }
}

output id string = storage.id
output name string = storage.name
output primaryEndpoints object = storage.properties.primaryEndpoints
