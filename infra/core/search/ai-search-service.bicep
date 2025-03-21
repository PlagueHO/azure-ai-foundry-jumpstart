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

var searchIdentityProvider = (sku.name == 'free') ? null : {
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

output id string = search.id
output endpoint string = 'https://${name}.search.windows.net/'
output name string = search.name
output principalId string = !empty(searchIdentityProvider) ? search.identity.principalId : ''
