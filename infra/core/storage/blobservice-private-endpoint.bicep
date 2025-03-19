// Parameters
@description('Specifies the name of the virtual network.')
param virtualNetworkName string

@description('Specifies the name of the subnet which contains the virtual machine.')
param subnetName string

@description('Specifies the name of the private link to the boot diagnostics storage account.')
param blobStorageAccountPrivateEndpointName string = 'BlobStorageAccountPrivateEndpoint'

@description('Specifies the resource id of the Azure Storage Account.')
param storageAccountId string

@description('Specifies the location.')
param location string = resourceGroup().location

@description('Specifies the resource tags.')
param tags object

// Virtual Network
resource vnet 'Microsoft.Network/virtualNetworks@2021-08-01' existing = {
  name: virtualNetworkName
}

// Private DNS Zones
resource blobPrivateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' existing = {
  name: 'privatelink.blob.${environment().suffixes.storage}'
}

// Virtual Network Links
resource blobPrivateDnsZoneVirtualNetworkLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = {
  parent: blobPrivateDnsZone
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
resource blobStorageAccountPrivateEndpoint 'Microsoft.Network/privateEndpoints@2021-08-01' = {
  name: blobStorageAccountPrivateEndpointName
  location: location
  tags: tags
  properties: {
    privateLinkServiceConnections: [
      {
        name: blobStorageAccountPrivateEndpointName
        properties: {
          privateLinkServiceId: storageAccountId
          groupIds: [
            'blob'
          ]
        }
      }
    ]
    subnet: {
      id: '${vnet.id}/subnets/${subnetName}'
    }
  }
}

resource blobStorageAccountPrivateDnsZoneGroupName 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2021-08-01' = {
  parent: blobStorageAccountPrivateEndpoint
  name: 'PrivateDnsZoneGroupName'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'dnsConfig'
        properties: {
          privateDnsZoneId: blobPrivateDnsZone.id
        }
      }
    ]
  }
}

output blobStorageAccountPrivateEndpointId string = blobStorageAccountPrivateEndpoint.id
output blobStorageAccountPrivateDnsZoneGroupId string = blobStorageAccountPrivateDnsZoneGroupName.id
output blobPrivateDnsZoneVirtualNetworkLinkId string = blobPrivateDnsZoneVirtualNetworkLink.id
output blobPrivateDnsZoneId string = blobPrivateDnsZone.id
output blobPrivateDnsZoneName string = blobPrivateDnsZone.name
output blobPrivateDnsZoneResourceId string = blobPrivateDnsZone.id
output blobPrivateDnsZoneVirtualNetworkLinkName string = blobPrivateDnsZoneVirtualNetworkLink.name
