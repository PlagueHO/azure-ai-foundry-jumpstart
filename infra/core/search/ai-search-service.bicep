metadata description = 'Creates an Azure AI Search instance.'

@description('Name of the Azure AI Search service.')
param name string

@description('Location where the Azure AI Search service should be deployed.')
param location string = resourceGroup().location

@description('Tags to apply to the Azure AI Search service.')
param tags object = {}

@description('SKU configuration for the Azure AI Search service.')
param sku object = {
  name: 'standard'
}

@description('Authentication options for the Azure AI Search service.')
param authOptions object = {}

@description('Flag indicating whether local authentication should be disabled.')
param disableLocalAuth bool = false

@description('List of data exfiltration options to disable.')
param disabledDataExfiltrationOptions array = []

@description('Customer-managed key encryption settings.')
param encryptionWithCmk object = {
  enforcement: 'Unspecified'
}

@description('Hosting mode for the Azure AI Search service.')
@allowed([
  'default'
  'highDensity'
])
param hostingMode string = 'default'

@description('Network rule set configuration for the Azure AI Search service.')
param networkRuleSet object = {
  bypass: 'None'
  ipRules: []
}

@description('Number of partitions for the Azure AI Search service.')
param partitionCount int = 1

@description('Enable or disable public network access to the Azure AI Search service.')
@allowed([
  'enabled'
  'disabled'
])
param publicNetworkAccess string = 'enabled'

@description('Number of replicas for the Azure AI Search service.')
param replicaCount int = 1

@description('Semantic search capability for the Azure AI Search service.')
@allowed([
  'disabled'
  'free'
  'standard'
])
param semanticSearch string = 'disabled'

@description('Flag indicating whether to create a private endpoint for the Azure AI Search service.')
param enablePrivateEndpoint bool = false

@description('The name of the virtual network where the private endpoint will be created.')
param privateEndpointVnetName string = ''

@description('The name of the subnet where the private endpoint will be created.')
param privateEndpointSubnetName string = ''

@description('The name of the private endpoint resource.')
param privateEndpointName string = '${name}-pe'

var searchIdentityProvider = (sku.name == 'free')
  ? null
  : {
      type: 'SystemAssigned'
    }

resource search 'Microsoft.Search/searchServices@2021-04-01-preview' = {
  name: name
  location: location
  tags: tags
  // The free tier does not support managed identity
  identity: searchIdentityProvider
  properties: {
    authOptions: disableLocalAuth ? null : authOptions
    disableLocalAuth: disableLocalAuth
    disabledDataExfiltrationOptions: disabledDataExfiltrationOptions
    encryptionWithCmk: encryptionWithCmk
    hostingMode: hostingMode
    networkRuleSet: networkRuleSet
    partitionCount: partitionCount
    publicNetworkAccess: publicNetworkAccess
    replicaCount: replicaCount
    semanticSearch: semanticSearch
  }
  sku: sku
}

// Enable AI Search private endpoint if specified
module searchPrivateEndpoint 'ai-search-service-private-endpoint.bicep' = if (enablePrivateEndpoint) {
  name: privateEndpointName
  scope: resourceGroup()
  params: {
    virtualNetworkName: privateEndpointVnetName
    subnetName: privateEndpointSubnetName
    searchServicePrivateEndpointName: privateEndpointName
    searchServiceId: search.id
    location: location
    tags: tags
  }
}

@description('The resource ID of the Azure AI Search service.')
output id string = search.id

@description('The endpoint URI of the Azure AI Search service.')
output endpoint string = 'https://${name}.search.windows.net/'

@description('The name of the Azure AI Search service.')
output name string = search.name

@description('The principal ID of the managed identity for the Azure AI Search service, if enabled.')
output principalId string = !empty(searchIdentityProvider) ? search.identity.principalId : ''

@description('The resource ID of the AI Search private endpoint, if enabled.')
output privateEndpointId string = enablePrivateEndpoint
  ? searchPrivateEndpoint.outputs.searchServicePrivateEndpointId
  : ''

@description('The resource ID of the AI Search private DNS zone group, if enabled.')
output privateDnsZoneGroupId string = enablePrivateEndpoint
  ? searchPrivateEndpoint.outputs.searchServicePrivateDnsZoneGroupId
  : ''

@description('The resource ID of the AI Search private DNS zone virtual network link, if enabled.')
output privateDnsZoneVirtualNetworkLinkId string = enablePrivateEndpoint
  ? searchPrivateEndpoint.outputs.searchServicePrivateDnsZoneVirtualNetworkLinkId
  : ''

@description('The resource ID of the AI Search private DNS zone, if enabled.')
output privateDnsZoneId string = enablePrivateEndpoint
  ? searchPrivateEndpoint.outputs.searchServicePrivateDnsZoneId
  : ''

@description('The name of the AI Search private DNS zone, if enabled.')
output privateDnsZoneName string = enablePrivateEndpoint
  ? searchPrivateEndpoint.outputs.searchServicePrivateDnsZoneName
  : ''

@description('The resource ID of the AI Search private DNS zone, if enabled.')
output privateDnsZoneResourceId string = enablePrivateEndpoint
  ? searchPrivateEndpoint.outputs.searchServicePrivateDnsZoneResourceId
  : ''

@description('The name of the AI Search private DNS zone virtual network link, if enabled.')
output privateDnsZoneVirtualNetworkLinkName string = enablePrivateEndpoint
  ? searchPrivateEndpoint.outputs.searchServicePrivateDnsZoneVirtualNetworkLinkName
  : ''
