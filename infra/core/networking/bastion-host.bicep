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
            // Todo: Fix the linter error: If property "id" represents a resource ID, it must use a symbolic resource reference, be a parameter or start with one of these functions: extensionResourceId, guid, if, managementGroupResourceId, reference, resourceId, subscription, subscriptionResourceId, tenantResourceId.
            id: '${virtualNetworkId}/subnets/AzureBastionSubnet'
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

output bastionId string = azureBastion.id
output bastionName string = azureBastion.name
output publicIpId string = bastionPublicIp.id
output publicIpName string = bastionPublicIp.name
