metadata description = 'Creates a Private Endpoint for an Azure Cognitive Services Account.'

@description('Specifies the name of the virtual network.')
param virtualNetworkName string

@description('Specifies the name of the subnet which contains the private endpoint.')
param subnetName string

@description('Specifies the name of the private endpoint to create.')
param aiServicesPrivateEndpointName string

@description('Specifies the resource id of the Azure Cognitive Services Account.')
param aiServicesAccountId string

@description('Specifies the location.')
param location string = resourceGroup().location

@description('Specifies the resource tags.')
param tags object

// Virtual Network
resource vnet 'Microsoft.Network/virtualNetworks@2021-08-01' existing = {
  name: virtualNetworkName
}

// Private DNS Zones
resource aiServicesPrivateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' existing = {
  name: 'privatelink.cognitiveservices.azure.com'
}

// Virtual Network Links
resource aiServicesPrivateDnsZoneVirtualNetworkLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = {
  parent: aiServicesPrivateDnsZone
  name: 'link_to_${toLower(virtualNetworkName)}'
  location: 'global'
  properties: {
    registrationEnabled: false
    virtualNetwork: {
      id: vnet.id
    }
  }
}

// Private Endpoints
resource aiServicesPrivateEndpoint 'Microsoft.Network/privateEndpoints@2021-08-01' = {
  name: aiServicesPrivateEndpointName
  location: location
  tags: tags
  properties: {
    subnet: {
      id: '${vnet.id}/subnets/${subnetName}'
    }
    privateLinkServiceConnections: [
      {
        name: aiServicesPrivateEndpointName
        properties: {
          privateLinkServiceId: aiServicesAccountId
          groupIds: [
            'account'
          ]
        }
      }
    ]
  }
}

resource aiServicesPrivateDnsZoneGroupName 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2021-08-01' = {
  parent: aiServicesPrivateEndpoint
  name: 'PrivateDnsZoneGroupName'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'dnsConfig'
        properties: {
          privateDnsZoneId: aiServicesPrivateDnsZone.id
        }
      }
    ]
  }
}

@description('The resource ID of the Cognitive Services private endpoint.')
output aiServicesPrivateEndpointId string = aiServicesPrivateEndpoint.id

@description('The resource ID of the Cognitive Services private DNS zone group.')
output aiServicesPrivateDnsZoneGroupId string = aiServicesPrivateDnsZoneGroupName.id

@description('The resource ID of the Cognitive Services private DNS zone virtual network link.')
output aiServicesPrivateDnsZoneVirtualNetworkLinkId string = aiServicesPrivateDnsZoneVirtualNetworkLink.id

@description('The resource ID of the Cognitive Services private DNS zone.')
output aiServicesPrivateDnsZoneId string = aiServicesPrivateDnsZone.id

@description('The name of the Cognitive Services private DNS zone.')
output aiServicesPrivateDnsZoneName string = aiServicesPrivateDnsZone.name

@description('The resource ID of the Cognitive Services private DNS zone.')
output aiServicesPrivateDnsZoneResourceId string = aiServicesPrivateDnsZone.id

@description('The name of the Cognitive Services private DNS zone virtual network link.')
output aiServicesPrivateDnsZoneVirtualNetworkLinkName string = aiServicesPrivateDnsZoneVirtualNetworkLink.name
