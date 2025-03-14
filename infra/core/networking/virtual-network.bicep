metadata description = 'Creates an Azure Virtual Network with subnets.'

@description('Name of the Virtual Network resource.')
param name string

@description('Location where the Virtual Network resource should be deployed.')
param location string = resourceGroup().location

@description('Tags to apply to the Virtual Network resource.')
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

output virtualNetworkId string = virtualNetwork.id
output virtualNetworkName string = virtualNetwork.name
