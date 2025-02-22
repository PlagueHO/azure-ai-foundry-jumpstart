metadata description = 'Creates an Azure Virtual Network with subnets.'

param name string
param location string = resourceGroup().location
param tags object = {}

@description('Array of address prefixes for the Virtual Network (e.g. ["10.0.0.0/16"])')
param addressPrefixes array

@description('Array of subnet objects, each with a "name" and "addressPrefix" property.')
param subnets array = []

resource virtualNetwork 'Microsoft.Network/virtualNetworks@2022-09-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    addressSpace: {
      addressPrefixes: addressPrefixes
    }
    subnets: [
      for subnet in subnets: {
        name: subnet.name
        properties: {
          addressPrefix: subnet.addressPrefix
        }
      }
    ]
  }
}

output id string = virtualNetwork.id
output virtualNetworkName string = virtualNetwork.name
