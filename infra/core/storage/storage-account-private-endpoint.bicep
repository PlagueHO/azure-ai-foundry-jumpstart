metadata description = 'Creates a Private Endpoint for a Storage Account.'

@description('Specifies the name of the virtual network.')
param virtualNetworkName string

@description('Specifies the name of the subnet which contains the virtual machine.')
param subnetName string

@description('Specifies the name of the private endpoint to create.')
param storageAccountPrivateEndpointName string = '${serviceType}StorageAccountPrivateEndpoint'

@description('Specifies the resource id of the Azure Storage Account.')
param storageAccountId string

@description('Specifies the location.')
param location string = resourceGroup().location

@description('Specified the type of the Azure Storage Account private endpoint.')
@allowed(['blob', 'file', 'queue', 'table'])
param serviceType string = 'blob'

@description('Specifies the resource tags.')
param tags object

// Virtual Network
resource vnet 'Microsoft.Network/virtualNetworks@2021-08-01' existing = {
  name: virtualNetworkName
}

// Private DNS Zones
resource storageAccountPrivateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' existing = {
  name: 'privatelink.${serviceType}.${environment().suffixes.storage}'
}

// Virtual Network Links
resource storageAccountPrivateDnsZoneVirtualNetworkLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = {
  parent: storageAccountPrivateDnsZone
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
resource storageAccountPrivateEndpoint 'Microsoft.Network/privateEndpoints@2021-08-01' = {
  name: storageAccountPrivateEndpointName
  location: location
  tags: tags
  properties: {
    subnet: {
      id: '${vnet.id}/subnets/${subnetName}'
    }
    privateLinkServiceConnections: [
      {
        name: storageAccountPrivateEndpointName
        properties: {
          privateLinkServiceId: storageAccountId
          groupIds: [
            'blob'
          ]
        }
      }
    ]
  }
}

resource storageAccountPrivateDnsZoneGroupName 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2021-08-01' = {
  parent: storageAccountPrivateEndpoint
  name: 'PrivateDnsZoneGroupName'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'dnsConfig'
        properties: {
          privateDnsZoneId: storageAccountPrivateDnsZone.id
        }
      }
    ]
  }
}

output storageAccountPrivateEndpointId string = storageAccountPrivateEndpoint.id
output storageAccountPrivateDnsZoneGroupId string = storageAccountPrivateDnsZoneGroupName.id
output storageAccountPrivateDnsZoneVirtualNetworkLinkId string = storageAccountPrivateDnsZoneVirtualNetworkLink.id
output storageAccountPrivateDnsZoneId string = storageAccountPrivateDnsZone.id
output storageAccountPrivateDnsZoneName string = storageAccountPrivateDnsZone.name
output storageAccountPrivateDnsZoneResourceId string = storageAccountPrivateDnsZone.id
output storageAccountPrivateDnsZoneVirtualNetworkLinkName string = storageAccountPrivateDnsZoneVirtualNetworkLink.name
