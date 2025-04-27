metadata description = 'Creates an Azure Bastion resource.'

@description('Name of the Azure Bastion resource.')
param name string

@description('Location where the Azure Bastion resource should be deployed.')
param location string

@description('Tags to apply to the Azure Bastion resource.')
param tags object

@description('ID of the virtual network where the Azure Bastion will be deployed.')
param virtualNetworkId string

@description('Name of the Public IP to be associated with the Azure Bastion.')
param publicIpName string

@allowed([
  'Standard'
])
@description('SKU of the Public IP to be associated with the Azure Bastion. Must be Standard.')
param publicIpSku string = 'Standard'

@description('SKU for the Azure Bastion host. Allowed values are usually Standard or other variations.')
@allowed([
  'Basic'
  'Standard'
])
param bastionHostSku string = 'Standard'

// Create the Public IP for Azure Bastion
resource bastionPublicIp 'Microsoft.Network/publicIPAddresses@2023-02-01' = {
  name: publicIpName
  location: location
  sku: {
    name: publicIpSku
    tier: 'Regional'
  }
  properties: {
    publicIPAllocationMethod: 'Static'
    idleTimeoutInMinutes: 4
  }
  tags: tags
}

// Create Azure Bastion
resource azureBastion 'Microsoft.Network/bastionHosts@2023-02-01' = {
  name: name
  location: location
  sku: {
    name: bastionHostSku
  }
  properties: {
    ipConfigurations: [
      {
        name: 'ipconfig1'
        properties: {
          subnet: {
            id: resourceId(virtualNetworkId, 'Microsoft.Network/virtualNetworks/subnets', 'AzureBastionSubnet')
          }
          publicIPAddress: {
            id: bastionPublicIp.id
          }
        }
      }
    ]
  }
  tags: tags
}

@description('The resource ID of the Azure Bastion host.')
output bastionId string = azureBastion.id

@description('The name of the Azure Bastion host.')
output bastionName string = azureBastion.name

@description('The resource ID of the public IP associated with the Azure Bastion host.')
output publicIpId string = bastionPublicIp.id

@description('The name of the public IP associated with the Azure Bastion host.')
output publicIpName string = bastionPublicIp.name
