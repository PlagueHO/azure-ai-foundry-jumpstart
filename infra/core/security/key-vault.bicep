metadata description = 'Creates an Azure Key Vault.'

@description('Name of the Azure Key Vault.')
param name string

@description('Location where the Azure Key Vault should be deployed.')
param location string = resourceGroup().location

@description('Tags to apply to the Azure Key Vault.')
param tags object = {}

@description('Allow the key vault to be used during resource creation (e.g., VM disk encryption).')
param enabledForDeployment bool = false

@description('Allow the key vault to be used for template deployment.')
param enabledForTemplateDeployment bool = false

@description('Allow Azure Disk Encryption to retrieve secrets from the vault.')
param enabledForDiskEncryption bool = false

@description('Enable or disable public network access to the Azure Key Vault.')
@allowed([
  'Enabled'
  'Disabled'
])
param publicNetworkAccess string = 'Enabled'

@description('Soft delete retention period in days for the Azure Key Vault.')
param softDeleteRetentionInDays int = 90

@description('Enable or disable purge protection for the Azure Key Vault.')
param enablePurgeProtection bool = true

@description('Flag indicating whether to create a private endpoint for the Key Vault.')
param enablePrivateEndpoint bool = false

@description('The name of the virtual network where the private endpoint will be created.')
param privateEndpointVnetName string = ''

@description('The name of the subnet where the private endpoint will be created.')
param privateEndpointSubnetName string = ''

@description('The name of the private endpoint resource.')
param privateEndpointName string = '${name}-pe'

resource keyVault 'Microsoft.KeyVault/vaults@2022-07-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    enabledForDeployment: enabledForDeployment
    enabledForTemplateDeployment: enabledForTemplateDeployment
    enabledForDiskEncryption: enabledForDiskEncryption
    publicNetworkAccess: publicNetworkAccess
    enablePurgeProtection: enablePurgeProtection
    enableSoftDelete: true
    softDeleteRetentionInDays: softDeleteRetentionInDays
    enableRbacAuthorization: true
  }
}

// Enable Key Vault private endpoint if specified
module keyVaultPrivateEndpoint 'key-vault-private-endpoint.bicep' = if (enablePrivateEndpoint) {
  name: privateEndpointName
  scope: resourceGroup()
  params: {
    virtualNetworkName: privateEndpointVnetName
    subnetName: privateEndpointSubnetName
    keyVaultPrivateEndpointName: privateEndpointName
    keyVaultId: keyVault.id
    location: location
    tags: tags
  }
}

output endpoint string = keyVault.properties.vaultUri
output id string = keyVault.id
output name string = keyVault.name
output privateEndpointId string = enablePrivateEndpoint ? keyVaultPrivateEndpoint.outputs.keyVaultPrivateEndpointId : ''
