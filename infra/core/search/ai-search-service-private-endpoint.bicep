metadata description = 'Creates a Private Endpoint for an Azure AI Search Service.'

@description('Specifies the name of the virtual network.')
param virtualNetworkName string

@description('Specifies the name of the subnet which contains the private endpoint.')
param subnetName string

@description('Specifies the name of the private endpoint to create.')
param searchServicePrivateEndpointName string

@description('Specifies the resource id of the Azure AI Search Service.')
param searchServiceId string

@description('Specifies the location.')
param location string = resourceGroup().location

@description('Specifies the resource tags.')
param tags object

// Virtual Network
resource vnet 'Microsoft.Network/virtualNetworks@2021-08-01' existing = {
  name: virtualNetworkName
}

// Private DNS Zones
resource searchServicePrivateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' existing = {
  name: 'privatelink.search.windows.net'
}

// Virtual Network Links
resource searchServicePrivateDnsZoneVirtualNetworkLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = {
  parent: searchServicePrivateDnsZone
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
resource searchServicePrivateEndpoint 'Microsoft.Network/privateEndpoints@2021-08-01' = {
  name: searchServicePrivateEndpointName
  location: location
  tags: tags
  properties: {
    subnet: {
      id: '${vnet.id}/subnets/${subnetName}'
    }
    privateLinkServiceConnections: [
      {
        name: searchServicePrivateEndpointName
        properties: {
          privateLinkServiceId: searchServiceId
          groupIds: [
            'searchService'
          ]
        }
      }
    ]
  }
}

resource searchServicePrivateDnsZoneGroupName 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2021-08-01' = {
  parent: searchServicePrivateEndpoint
  name: 'PrivateDnsZoneGroupName'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'dnsConfig'
        properties: {
          privateDnsZoneId: searchServicePrivateDnsZone.id
        }
      }
    ]
  }
}

output searchServicePrivateEndpointId string = searchServicePrivateEndpoint.id
output searchServicePrivateDnsZoneGroupId string = searchServicePrivateDnsZoneGroupName.id
output searchServicePrivateDnsZoneVirtualNetworkLinkId string = searchServicePrivateDnsZoneVirtualNetworkLink.id
output searchServicePrivateDnsZoneId string = searchServicePrivateDnsZone.id
output searchServicePrivateDnsZoneName string = searchServicePrivateDnsZone.name
output searchServicePrivateDnsZoneResourceId string = searchServicePrivateDnsZone.id
output searchServicePrivateDnsZoneVirtualNetworkLinkName string = searchServicePrivateDnsZoneVirtualNetworkLink.name
