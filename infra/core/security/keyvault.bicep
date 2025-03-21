metadata description = 'Creates an Azure Key Vault.'

@description('Name of the Azure Key Vault.')
param name string

@description('Location where the Azure Key Vault should be deployed.')
param location string = resourceGroup().location

@description('Tags to apply to the Azure Key Vault.')
param tags object = {}

@description('Principal ID to grant access policies to the Azure Key Vault.')
param principalId string = ''

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

@description('Network ACLs configuration for the Azure Key Vault.')
param networkAcls object = {
  bypass: 'AzureServices'
  defaultAction: 'Allow'
  ipRules: []
  virtualNetworkRules: []
}

@description('Soft delete retention period in days for the Azure Key Vault.')
param softDeleteRetentionInDays int = 90

@description('Enable or disable purge protection for the Azure Key Vault.')
param enablePurgeProtection bool = true

@description('List of access policies to apply to the Azure Key Vault.')
param accessPolicies array = []

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
    accessPolicies: accessPolicies
    enabledForDeployment: enabledForDeployment
    enabledForTemplateDeployment: enabledForTemplateDeployment
    enabledForDiskEncryption: enabledForDiskEncryption
    publicNetworkAccess: publicNetworkAccess
    enablePurgeProtection: enablePurgeProtection
    enableSoftDelete: true
    softDeleteRetentionInDays: softDeleteRetentionInDays
  }
}

output endpoint string = keyVault.properties.vaultUri
output id string = keyVault.id
output name string = keyVault.name
