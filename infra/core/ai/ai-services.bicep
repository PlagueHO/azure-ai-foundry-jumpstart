metadata description = 'Creates an Azure AI Services instance.'

@description('Name of the Azure AI Services instance.')
param name string

@description('Location where the Azure AI Services instance should be deployed.')
param location string = resourceGroup().location

@description('Tags to apply to the Azure AI Services instance.')
param tags object = {}

@description('The custom subdomain name used to access the API. Defaults to the value of the name parameter.')
param customSubDomainName string = name

@description('Flag indicating whether local authentication should be disabled.')
param disableLocalAuth bool = false

@description('Array of deployments for the AI Services account.')
param deployments array = []

@description('The kind of AI Services account.')
param kind string = 'OpenAI'

@allowed(['Enabled', 'Disabled'])
@description('Enable or disable public network access to the AI Services account.')
param publicNetworkAccess string = 'Enabled'

@description('SKU for the AI Services account.')
param sku object = {
  name: 'S0'
}

@description('Allowed IP rules for network ACLs.')
param allowedIpRules array = []

@description('Network ACLs configuration for the AI Services account.')
param networkAcls object = empty(allowedIpRules)
  ? {
      defaultAction: 'Allow'
    }
  : {
      ipRules: allowedIpRules
      defaultAction: 'Deny'
    }

@description('Flag indicating whether to create a private endpoint for the AI Services account.')
param enablePrivateEndpoint bool = false

@description('The name of the virtual network where the private endpoint will be created.')
param privateEndpointVnetName string = ''

@description('The name of the subnet where the private endpoint will be created.')
param privateEndpointSubnetName string = ''

@description('The name of the private endpoint resource.')
param privateEndpointName string = '${name}-pe'

resource account 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: name
  location: location
  tags: tags
  kind: kind
  properties: {
    customSubDomainName: customSubDomainName
    publicNetworkAccess: publicNetworkAccess
    networkAcls: networkAcls
    disableLocalAuth: disableLocalAuth
  }
  sku: sku
}

@batchSize(1)
resource deployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = [
  for deployment in deployments: {
    parent: account
    name: deployment.name
    properties: {
      model: deployment.model
      raiPolicyName: deployment.?raiPolicyName ?? null
    }
    sku: deployment.?sku ?? {
      name: 'Standard'
      capacity: 20
    }
  }
]

// Enable AI Services private endpoint if specified
module aiServicesPrivateEndpoint 'ai-services-private-endpoint.bicep' = if (enablePrivateEndpoint) {
  name: privateEndpointName
  scope: resourceGroup()
  params: {
    virtualNetworkName: privateEndpointVnetName
    subnetName: privateEndpointSubnetName
    aiServicesPrivateEndpointName: privateEndpointName
    aiServicesAccountId: account.id
    location: location
    tags: tags
  }
}

@description('The endpoint URI of the AI Services account.')
output endpoint string = account.properties.endpoint

@description('The endpoints object of the AI Services account.')
output endpoints object = account.properties.endpoints

@description('The resource ID of the AI Services account.')
output id string = account.id

@description('The name of the AI Services account.')
output name string = account.name

@description('The resource ID of the AI Services private endpoint, if enabled.')
output privateEndpointId string = enablePrivateEndpoint
  ? aiServicesPrivateEndpoint.outputs.aiServicesPrivateEndpointId
  : ''

@description('The resource ID of the AI Services private DNS zone group, if enabled.')
output privateDnsZoneGroupId string = enablePrivateEndpoint
  ? aiServicesPrivateEndpoint.outputs.aiServicesPrivateDnsZoneGroupId
  : ''

@description('The resource ID of the AI Services private DNS zone virtual network link, if enabled.')
output privateDnsZoneVirtualNetworkLinkId string = enablePrivateEndpoint
  ? aiServicesPrivateEndpoint.outputs.aiServicesPrivateDnsZoneVirtualNetworkLinkId
  : ''

@description('The resource ID of the AI Services private DNS zone, if enabled.')
output privateDnsZoneId string = enablePrivateEndpoint
  ? aiServicesPrivateEndpoint.outputs.aiServicesPrivateDnsZoneId
  : ''

@description('The name of the AI Services private DNS zone, if enabled.')
output privateDnsZoneName string = enablePrivateEndpoint
  ? aiServicesPrivateEndpoint.outputs.aiServicesPrivateDnsZoneName
  : ''

@description('The resource ID of the AI Services private DNS zone, if enabled.')
output privateDnsZoneResourceId string = enablePrivateEndpoint
  ? aiServicesPrivateEndpoint.outputs.aiServicesPrivateDnsZoneResourceId
  : ''

@description('The name of the AI Services private DNS zone virtual network link, if enabled.')
output privateDnsZoneVirtualNetworkLinkName string = enablePrivateEndpoint
  ? aiServicesPrivateEndpoint.outputs.aiServicesPrivateDnsZoneVirtualNetworkLinkName
  : ''
