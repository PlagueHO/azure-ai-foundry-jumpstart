targetScope = 'subscription'

// The main bicep module to provision Azure resources.
// For a more complete walkthrough to understand how this file works with azd,
// see https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/make-azd-compatible?pivots=azd-create

@minLength(1)
@maxLength(64)
@description('Name of the the environment which is used to generate a short unique hash used in all resources.')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

// Optional parameters to override the default azd resource naming conventions.
// Add the following to main.parameters.json to provide values:
// "resourceGroupName": {
//      "value": "myGroupName"
// }
@description('Name of the resource group to create.')
param resourceGroupName string = ''

// Should an Azure Bastion be created?
@description('Should an Azure Bastion be created?')
param createBastionHost bool = true

var abbrs = loadJsonContent('./abbreviations.json')

// tags that should be applied to all resources.
var tags = {
  // Tag all resources with the environment name.
  'azd-env-name': environmentName
}

// Generate a unique token to be used in naming resources.
// Remove linter suppression after using.
#disable-next-line no-unused-vars
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))

var logAnalyticsName = '${abbrs.operationalInsightsWorkspaces}${environmentName}'
var applicationInsightsName = '${abbrs.insightsComponents}${environmentName}'
var applicationInsightsDashboardName = '${abbrs.portalDashboards}${environmentName}'
var virtualNetworkName = '${abbrs.networkVirtualNetworks}${environmentName}'
var storageAccounName = toLower(replace('${abbrs.storageStorageAccounts}${environmentName}', '-', ''))

// Organize resources in a resource group
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: !empty(resourceGroupName) ? resourceGroupName : '${abbrs.resourcesResourceGroups}${environmentName}'
  location: location
  tags: tags
}

// Create the monitoring resources for the environment
module monitoring 'core/monitor/monitoring.bicep' = {
  name: 'monitoring'
  scope: rg
  params: {
    location: location
    tags: tags
    logAnalyticsName: logAnalyticsName
    applicationInsightsName: applicationInsightsName
    applicationInsightsDashboardName: applicationInsightsDashboardName
  }
}

// Virtual Network to host all AI services and supporting resources
module virtualNetwork 'core/networking/virtual-network.bicep' = {
  name: 'virtual-network'
  scope: rg
  params: {
    name: virtualNetworkName
    location: location
    tags: tags
    addressPrefixes: [
      '10.0.0.0/16'
    ]
    subnets: [
      {
        // Default subnet (generally not used)
        name: 'Default'
        addressPrefix: '10.0.0.0/24'
      }
      {
        // AI Services Subnet
        name: '${abbrs.networkVirtualNetworksSubnets}AiServices'
        addressPrefix: '10.0.1.0/24'
      }
      {
        // Azure AI Foundry Hubs Subnet
        name: '${abbrs.networkVirtualNetworksSubnets}FoundryHubs'
        addressPrefix: '10.0.2.0/24'
      }
      {
        // Shared Services Subnet (storage accounts, key vaults, monitoring, etc.)
        name: '${abbrs.networkVirtualNetworksSubnets}SharedServices'
        addressPrefix: '10.0.3.0/24'
      }
      {
        // Bastion Gateway Subnet
        name: 'AzureBastionSubnet'
        addressPrefix: '10.0.255.0/27'
      }
    ]
  }
}

// Private DNS Zone for the Key Vault to be used by Private Link
module keyVaultPrivateDnsZone 'core/networking/private-dns-zone.bicep' = {
  name: 'keyvault-private-dns-zone'
  scope: rg
  params: {
    privateDnsZoneName: 'privatelink.vaultcore.azure.net'
    location: 'global'
    tags: tags
  }
}

// Create a Key Vault to use for the AI services
module keyVault 'core/security/keyvault.bicep' = {
  name: 'key-vault'
  scope: rg
  params: {
    name: '${abbrs.keyVaultVaults}${environmentName}'
    location: location
    tags: tags
    publicNetworkAccess: 'Disabled'
    networkAcls: {
      bypass: 'None'
      defaultAction: 'Allow'
      ipRules: []
      virtualNetworkRules: [
        {
          id: virtualNetwork.outputs.virtualNetworkId
          ignoreMissingVnetServiceEndpoint: true
        }
      ]
    }
    accessPolicies: [
      {
        tenantId: subscription().tenantId
        objectId: subscription().tenantId
        permissions: {
          keys: [
            'get'
            'list'
            'create'
            'import'
            'delete'
            'update'
            'backup'
            'restore'
            'recover'
          ]
          secrets: [
            'get'
            'list'
            'set'
            'delete'
            'backup'
            'restore'
            'recover'
          ]
          certificates: [
            'get'
            'list'
            'create'
            'import'
            'delete'
            'update'
            'managecontacts'
            'manageissuers'
            'setissuersettings'
          ]
        }
      }
    ]
  }
}

// Private DNS Zone for the storage accounts to be used by Private Link
module storagePrivateDnsZone 'core/networking/private-dns-zone.bicep' = {
  name: 'storage-blobservice-private-dns-zone'
  scope: rg
  params: {
    privateDnsZoneName: 'privatelink.blob.${environment().suffixes.storage}'
    location: 'global'
    tags: tags
  }
}

// Create a Storage Account to use for the AI services
module storageAccount 'core/storage/storage-account.bicep' = {
  name: 'storage-account'
  scope: rg
  params: {
    name: storageAccounName
    location: location
    tags: tags
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    allowCrossTenantReplication: false
    allowSharedKeyAccess: true
    defaultToOAuthAuthentication: true
    deleteRetentionPolicy: {
      enabled: true
      days: 7
    }
    dnsEndpointType: 'Standard'
    isHnsEnabled: false
    kind: 'StorageV2'
    minimumTlsVersion: 'TLS1_2'
    publicNetworkAccess: 'Disabled'
    enablePrivateEndpoint: true
    privateEndpointVnetName: virtualNetworkName
    privateEndpointSubnetName: '${abbrs.networkVirtualNetworksSubnets}SharedServices'
    logAnalyticsWorkspaceId: monitoring.outputs.logAnalyticsWorkspaceId
  }
}

// Create Private DNS Zone for Azure AI Search
module searchPrivateDnsZone 'core/networking/private-dns-zone.bicep' = {
  name: 'search-private-dns-zone'
  scope: rg
  params: {
    privateDnsZoneName: 'privatelink.search.windows.net'
    tags: tags
  }
}

// Create Azure AI Search service
module aiSearchService 'core/search/ai-search-service.bicep' = {
  name: 'ai-search-service'
  scope: rg
  params: {
    name: '${abbrs.aiSearchSearchServices}${environmentName}'
    location: location
    tags: tags
    sku: {
      name: 'standard'
    }
  }
}

// Optional: Create an Azure Bastion host in the virtual network.
module bastion 'core/networking/bastion-host.bicep' = if (createBastionHost) {
  name: 'bastion-host'
  scope: rg
  params: {
    name: '${abbrs.networkBastionHosts}${environmentName}'
    location: location
    tags: tags
    virtualNetworkId: virtualNetwork.outputs.virtualNetworkId
    publicIpName: '${abbrs.networkPublicIPAddresses}${abbrs.networkBastionHosts}${environmentName}'
    publicIpSku: 'Standard'
  }
}

output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
