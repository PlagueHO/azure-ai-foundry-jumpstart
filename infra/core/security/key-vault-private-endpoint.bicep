metadata description = 'Creates a Private Endpoint for an Azure Key Vault.'

@description('Specifies the name of the virtual network.')
param virtualNetworkName string

@description('Specifies the name of the subnet which contains the private endpoint.')
param subnetName string

@description('Specifies the name of the private endpoint to create.')
param keyVaultPrivateEndpointName string

@description('Specifies the resource id of the Azure Key Vault.')
param keyVaultId string

@description('Specifies the location.')
param location string = resourceGroup().location

@description('Specifies the resource tags.')
param tags object

resource vnet 'Microsoft.Network/virtualNetworks@2021-08-01' existing = {
  name: virtualNetworkName
}

resource keyVaultPrivateEndpoint 'Microsoft.Network/privateEndpoints@2021-08-01' = {
  name: keyVaultPrivateEndpointName
  location: location
  tags: tags
  properties: {
    subnet: {
      id: '${vnet.id}/subnets/${subnetName}'
    }
    privateLinkServiceConnections: [
      {
        name: keyVaultPrivateEndpointName
        properties: {
          privateLinkServiceId: keyVaultId
          groupIds: [
            'vault'
          ]
        }
      }
    ]
  }
}

output keyVaultPrivateEndpointId string = keyVaultPrivateEndpoint.id
