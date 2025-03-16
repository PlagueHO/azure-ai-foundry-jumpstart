metadata description = 'Creates an Azure Private DNS Zone.'

@description('Name of the Azure Private DNS Zone.')
param privateDnsZoneName string

@description('Location for the Azure Private DNS Zone metadata. Typically global.')
param location string = 'global'

@description('Tags to apply to the Azure Private DNS Zone.')
param tags object = {}

resource privateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = {
  name: privateDnsZoneName
  location: location
  tags: tags
}

output privateDnsZoneId string = privateDnsZone.id
output privateDnsZoneName string = privateDnsZone.name
