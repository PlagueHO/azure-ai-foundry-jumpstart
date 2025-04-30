targetScope = 'subscription'

// The main bicep module to provision Azure resources.
// For a more complete walkthrough to understand how this file works with azd,
// see https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/make-azd-compatible?pivots=azd-create

@minLength(1)
@maxLength(64)
@description('Name of the the environment which is used to generate a short unique hash used in all resources.')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('Name of the resource group to create. If not specified, a unique name will be generated.')
param resourceGroupName string = 'rg-${environmentName}'

@description('Optional friendly name for the AI Foundry Hub workspace.')
param aiFoundryHubFriendlyName string = 'AI Foundry Hub (${environmentName})'

@description('Optional description for the AI Foundry Hub workspace.')
param aiFoundryHubDescription string = 'AI Foundry Hub for ${environmentName}'

@description('Should an Azure Bastion be created?')
param createBastionHost bool = false

@description('Disable API key authentication for AI Services and AI Search. Defaults to false.')
param disableApiKeys bool = false

var abbrs = loadJsonContent('./abbreviations.json')

// tags that should be applied to all resources.
var tags = {
  // Tag all resources with the environment name.
  'azd-env-name': environmentName
}

// Generate a unique token to be used in naming resources.
// Remove linter suppression after using.
#disable-next-line no-unused-vars
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))

var logAnalyticsName = '${abbrs.operationalInsightsWorkspaces}${environmentName}'
var sendTologAnalyticsCustomSettingName = 'send-to-${logAnalyticsName}'
var applicationInsightsName = '${abbrs.insightsComponents}${environmentName}'
var virtualNetworkName = '${abbrs.networkVirtualNetworks}${environmentName}'
var storageAccounName = toLower(replace('${abbrs.storageStorageAccounts}${environmentName}', '-', ''))
var keyVaultName = toLower(replace('${abbrs.keyVaultVaults}${environmentName}', '-', ''))
var containerRegistryName = toLower(replace('${abbrs.containerRegistryRegistries}${environmentName}', '-', ''))
var aiSearchUserAssignedIdentityName = '${abbrs.managedIdentityUserAssignedIdentities}${environmentName}'
var aiSearchName = '${abbrs.aiSearchSearchServices}${environmentName}'
var aiServicesName = '${abbrs.aiServicesAccounts}${environmentName}'
var aiServicesCustomSubDomainName = toLower(replace(environmentName, '-', ''))
var aiFoundryHubName = '${abbrs.aiFoundryHubs}${environmentName}'
var bastionHostName = '${abbrs.networkBastionHosts}${environmentName}'

var subnets = [
  {
    // Default subnet (generally not used)
    name: 'Default'
    addressPrefix: '10.0.0.0/24'
  }
  {
    // AI Services Subnet
    name: 'AiServices'
    addressPrefix: '10.0.1.0/24'
  }
  {
    // Azure AI Foundry Hubs Subnet
    name: 'FoundryHubs'
    addressPrefix: '10.0.2.0/24'
  }
  {
    // Shared Services Subnet (storage accounts, key vaults, monitoring, etc.)
    name: 'SharedServices'
    addressPrefix: '10.0.3.0/24'
  }
  {
    // Bastion Gateway Subnet
    name: 'AzureBastionSubnet'
    addressPrefix: '10.0.255.0/27'
  }
]

// Organize resources in a resource group
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: !empty(resourceGroupName) ? resourceGroupName : '${abbrs.resourcesResourceGroups}${environmentName}'
  location: location
  tags: tags
}

// Create the Log Analytics workspace using Azure Verified Module (AVM)
module logAnalyticsWorkspace 'br/public:avm/res/operational-insights/workspace:0.11.1' = {
  name: 'logAnalyticsWorkspace'
  scope: rg
  params: {
    name: logAnalyticsName
    location: location
    tags: tags
  }
}

// Create the Application Insights resource using Azure Verified Module (AVM)
module applicationInsights 'br/public:avm/res/insights/component:0.6.0' = {
  name: 'applicationInsights'
  scope: rg
  params: {
    name: applicationInsightsName
    location: location
    tags: tags
    workspaceResourceId: logAnalyticsWorkspace.outputs.resourceId
  }
}

// Create the Virtual Network and subnets using Azure Verified Modules (AVM)
module virtualNetwork 'br/public:avm/res/network/virtual-network:0.6.1' = {
  name: 'virtualNetwork'
  scope: rg
  params: {
    name: virtualNetworkName
    location: location
    tags: tags
    addressPrefixes: [
      '10.0.0.0/16'
    ]
    subnets: subnets
  }
}

// Create the Private DNS Zone for the Key Vault to be used by Private Link using Azure Verified Module (AVM)
module keyVaultPrivateDnsZone 'br/public:avm/res/network/private-dns-zone:0.7.1' = {
  name: 'keyvault-private-dns-zone'
  scope: rg
  params: {
    name: 'privatelink.vaultcore.azure.net'
    location: 'global'
  }
}

// Create a Key Vault with private endpoint in the Shared Services subnet using Azure Verified Module (AVM)
module keyVault 'br/public:avm/res/key-vault/vault:0.12.1' = {
  name: 'keyVault'
  scope: rg
  params: {
    name: keyVaultName
    diagnosticSettings: [
      {
        workspaceResourceId: logAnalyticsWorkspace.outputs.resourceId
      }
    ]
    enablePurgeProtection: true
    enableRbacAuthorization: true
    networkAcls: {
      bypass: 'AzureServices'
      defaultAction: 'Deny'
    }
    privateEndpoints: [
      {
        privateDnsZoneGroup: {
          privateDnsZoneGroupConfigs: [
            {
              privateDnsZoneResourceId: keyVaultPrivateDnsZone.outputs.resourceId
            }
          ]
        }
        service: 'vault'
        subnetResourceId: virtualNetwork.outputs.subnetResourceIds[3]
      }
    ]
    tags: tags
  }
}

// Create Private DNS Zone for the Storage Account blob service to be used by Private Link using Azure Verified Module (AVM)
module storageBlobPrivateDnsZone 'br/public:avm/res/network/private-dns-zone:0.7.1' = {
  name: 'storage-blobservice-private-dns-zone'
  scope: rg
  params: {
    name: 'privatelink.blob.${environment().suffixes.storage}'
    location: 'global'
    tags: tags
  }
}

// Create a Storage Account with private endpoint in the AppStorage subnet using Azure Verified Module (AVM)
module storageAccount 'br/public:avm/res/storage/storage-account:0.19.0' = {
  name: 'storage-account-deployment'
  scope: rg
  params: {
    name: storageAccounName
    allowBlobPublicAccess: false
    blobServices: {
      automaticSnapshotPolicyEnabled: false
      containerDeleteRetentionPolicyEnabled: false
      deleteRetentionPolicyEnabled: false
      lastAccessTimeTrackingPolicyEnabled: true
    }
    diagnosticSettings: [
      {
        metricCategories: [
          {
            category: 'AllMetrics'
          }
        ]
        name: sendTologAnalyticsCustomSettingName
        workspaceResourceId: logAnalyticsWorkspace.outputs.resourceId
      }
    ]
    enableHierarchicalNamespace: false
    enableNfsV3: false
    enableSftp: false
    largeFileSharesState: 'Enabled'
    location: location
    managedIdentities: {
      systemAssigned: true
    }
    networkAcls: {
      bypass: 'AzureServices'
      defaultAction: 'Deny'
    }
    privateEndpoints: [
      {
        privateDnsZoneGroup: {
          privateDnsZoneGroupConfigs: [
            {
              privateDnsZoneResourceId: storageBlobPrivateDnsZone.outputs.resourceId
            }
          ]
        }
        service: 'blob'
        subnetResourceId: virtualNetwork.outputs.subnetResourceIds[3]
        tags: tags
      }
    ]
    roleAssignments:[
      {
        roleDefinitionIdOrName: 'Storage Blob Data Contributor'
        principalType: 'ServicePrincipal'
        principalId: aiSearchService.outputs.systemAssignedMIPrincipalId
      }
      {
        roleDefinitionIdOrName: 'Storage Blob Data Contributor'
        principalType: 'ServicePrincipal'
        principalId: aiSearchUserAssignedIdentity.outputs.principalId
      }
    ]
    sasExpirationPeriod: '180.00:00:00'
    skuName: 'Standard_LRS'
    tags: tags
  }
}

// Create Private DNS Zone for Container Registry to be used by Private Link using Azure Verified Module (AVM)
module containerRegistryPrivateDnsZone 'br/public:avm/res/network/private-dns-zone:0.7.1' = {
  name: 'container-registry-private-dns-zone'
  scope: rg
  params: {
    name: 'privatelink.azurecr.io'
    location: 'global'
    tags: tags
  }
}

// Create Azure Container Registry with private endpoint in the SharedServices subnet using Azure Verified Module (AVM)
module containerRegistry 'br/public:avm/res/container-registry/registry:0.9.1' = {
  name: 'container-registry-deployment'
  scope: rg
  params: {
    name: containerRegistryName
    location: location
    acrSku: 'Premium'
    acrAdminUserEnabled: false
    diagnosticSettings: [
      {
        metricCategories: [
          {
            category: 'AllMetrics'
          }
        ]
        name: sendTologAnalyticsCustomSettingName
        workspaceResourceId: logAnalyticsWorkspace.outputs.resourceId
      }
    ]
    privateEndpoints: [
      {
        privateDnsZoneGroup: {
          privateDnsZoneGroupConfigs: [
            {
              privateDnsZoneResourceId: containerRegistryPrivateDnsZone.outputs.resourceId
            }
          ]
        }
        subnetResourceId: virtualNetwork.outputs.subnetResourceIds[3]
        tags: tags
      }
    ]
  }
}

// Create a user assigned managed identity for the Azure AI Search using Azure Verified Module (AVM)
// This is needed to decouple the lifecycle of the Azure AI search service from the identity
// to prevent a circular dependency when assigning roles to the identity
module aiSearchUserAssignedIdentity 'br/public:avm/res/managed-identity/user-assigned-identity:0.4.1' = {
  name: 'ai-search-user-assigned-identity-deployment'
  scope: rg
  params: {
    name: aiSearchUserAssignedIdentityName
    location: location
    tags: tags
  }
}

// Create Private DNS Zone for Azure AI Search to be used by Private Link using Azure Verified Module (AVM)
module aiSearchPrivateDnsZone 'br/public:avm/res/network/private-dns-zone:0.7.1' = {
  name: 'ai-search-private-dns-zone'
  scope: rg
  params: {
    name: 'privatelink.search.windows.net'
    location: 'global'
    tags: tags
  }
}

// Create Azure AI Search service with private endpoint in the AiServices subnet using Azure Verified Module (AVM)
module aiSearchService 'br/public:avm/res/search/search-service:0.9.2' = {
  name: 'ai-search-service-deployment'
  scope: rg
  params: {
    name: aiSearchName
    location: location
    sku: 'standard'
    diagnosticSettings: [
      {
        metricCategories: [
          {
            category: 'AllMetrics'
          }
        ]
        name: sendTologAnalyticsCustomSettingName
        workspaceResourceId: logAnalyticsWorkspace.outputs.resourceId
      }
    ]
    disableLocalAuth: disableApiKeys
    managedIdentities: {
      systemAssigned: true
      userAssignedResourceIds: [
        aiSearchUserAssignedIdentity.outputs.resourceId
      ]
    }
    authOptions: {
      aadOrApiKey: {
        aadAuthFailureMode: 'http401WithBearerChallenge'
      }
    }
    privateEndpoints: [
      {
        privateDnsZoneGroup: {
          privateDnsZoneGroupConfigs: [
            {
              privateDnsZoneResourceId: aiSearchPrivateDnsZone.outputs.resourceId
            }
          ]
        }
        subnetResourceId: virtualNetwork.outputs.subnetResourceIds[1]
        tags: tags
      }
    ]
    publicNetworkAccess: 'Disabled'
    roleAssignments: [
      {
        roleDefinitionIdOrName: 'Search Index Data Contributor'
        principalType: 'ServicePrincipal'
        principalId: aiServicesAccount.outputs.systemAssignedMIPrincipalId
      }
      {
        roleDefinitionIdOrName: 'Search Index Data Reader'
        principalType: 'ServicePrincipal'
        principalId: aiServicesAccount.outputs.systemAssignedMIPrincipalId
      }
      {
        roleDefinitionIdOrName: 'Search Service Contributor'
        principalType: 'ServicePrincipal'
        principalId: aiServicesAccount.outputs.systemAssignedMIPrincipalId
      }
    ]
    semanticSearch: 'standard'
    tags: tags
  }
}

// Create Private DNS Zone for Azure AI Services to be used by Private Link using Azure Verified Module (AVM)
module aiServicesPrivateDnsZone 'br/public:avm/res/network/private-dns-zone:0.7.1' = {
  name: 'ai-services-private-dns-zone'
  scope: rg
  params: {
    name: 'privatelink.cognitiveservices.azure.com'
    location: 'global'
    tags: tags
  }
}

// Create Azure AI Services instance with private endpoint in the AiServices subnet using Azure Verified Module (AVM)
module aiServicesAccount 'br/public:avm/res/cognitive-services/account:0.10.2' = {
  name: 'ai-services-account-deployment'
  scope: rg
  params: {
    kind: 'AIServices'
    name: aiServicesName
    location: location
    customSubDomainName: aiServicesCustomSubDomainName
    disableLocalAuth: disableApiKeys
    diagnosticSettings: [
      {
        workspaceResourceId: logAnalyticsWorkspace.outputs.resourceId
      }
    ]
    managedIdentities: {
      systemAssigned: true
    }
    privateEndpoints: [
      {
        privateDnsZoneGroup: {
          privateDnsZoneGroupConfigs: [
            {
              privateDnsZoneResourceId: aiServicesPrivateDnsZone.outputs.resourceId
            }
          ]
        }
        subnetResourceId: virtualNetwork.outputs.subnetResourceIds[1]
        tags: tags
      }
    ]
    publicNetworkAccess: 'Disabled'
    roleAssignments: [
      {
        roleDefinitionIdOrName: 'Cognitive Services Contributor'
        principalType: 'ServicePrincipal'
        principalId: aiSearchUserAssignedIdentity.outputs.principalId
      }
      {
        roleDefinitionIdOrName: 'Cognitive Services OpenAI Contributor'
        principalType: 'ServicePrincipal'
        principalId: aiSearchUserAssignedIdentity.outputs.principalId
      }
    ]
    sku: 'S0'
    tags: tags
  }
}

// Create Private DNS Zone for Azure AI Hub endpoints to be used by Private Link using Azure Verified Module (AVM)
module aiHubApiMlPrivateDnsZone 'br/public:avm/res/network/private-dns-zone:0.7.1' = {
  name: 'ai-hub-apiml-private-dns-zone'
  scope: rg
  params: {
    name: 'privatelink.api.azureml.ms'
    location: 'global'
    tags: tags
  }
}

module aiHubNotebooksPrivateDnsZone 'br/public:avm/res/network/private-dns-zone:0.7.1' = {
  name: 'ai-hub-notebooks-private-dns-zone'
  scope: rg
  params: {
    name: 'privatelink.notebooks.azure.net'
    location: 'global'
    tags: tags
  }
}

// Create Azure AI Foundry Hub workspace with private endpoint in the FoundryHubs subnet using Azure Verified Module (AVM)
module aiFoundryHub 'br/public:avm/res/machine-learning-services/workspace:0.12.0' = {
  name: 'ai-foundry-hub-workspace-deployment'
  scope: rg
  params: {
    name: aiFoundryHubName
    friendlyName: aiFoundryHubFriendlyName
    description: aiFoundryHubDescription
    location: location
    kind: 'Hub'
    sku: 'Basic'
    associatedApplicationInsightsResourceId: applicationInsights.outputs.resourceId
    associatedKeyVaultResourceId: keyVault.outputs.resourceId
    associatedStorageAccountResourceId: storageAccount.outputs.resourceId
    associatedContainerRegistryResourceId: containerRegistry.outputs.resourceId
    connections: [
      {
        category: 'AIServices'
        connectionProperties: {
          authType: 'ApiKey'
          credentials: {
            key: 'key'
          }
        }
        metadata: {
          ApiType: 'Azure'
          ApiVersion: '2023-07-01-preview'
          DeploymentApiVersion: '2023-10-01-preview'
          Location: location
          ResourceId: aiServicesAccount.outputs.resourceId
        }
        name: 'ai'
        target: aiServicesAccount.outputs.resourceId
        isSharedToAll: true
      }
    ]
    diagnosticSettings: [
      {
        metricCategories: [
          {
            category: 'AllMetrics'
          }
        ]
        name: sendTologAnalyticsCustomSettingName
        workspaceResourceId: logAnalyticsWorkspace.outputs.resourceId
      }
    ]
    managedIdentities: {
      systemAssigned: true
    }
    managedNetworkSettings: {
      firewallSku: 'Basic'
      isolationMode: 'AllowInternetOutbound'
    }
    publicNetworkAccess: 'Disabled'
    privateEndpoints: [
      {
        privateDnsZoneGroup: {
          privateDnsZoneGroupConfigs: [
            {
              privateDnsZoneResourceId: aiHubApiMlPrivateDnsZone.outputs.resourceId
            }
            {
              privateDnsZoneResourceId: aiHubNotebooksPrivateDnsZone.outputs.resourceId
            }
          ]
        }
        subnetResourceId: virtualNetwork.outputs.subnetResourceIds[2]
        tags: tags
      }
    ]
    provisionNetworkNow: true
    systemDatastoresAuthMode: 'Identity'
    tags: tags
    workspaceHubConfig: {
      defaultWorkspaceResourceGroup: rg.id
    }
  }
}

// Final stage of the deployment is to set the IAM role assignments for the
// Azure AI Service for the Azure AI Search Service to avoie a circular dependency

// Optional: Create an Azure Bastion host in the virtual network using Azure Verified Module (AVM)
module bastionHost 'br/public:avm/res/network/bastion-host:0.6.1' = if (createBastionHost) {
  name: 'bastion-host-deployment'
  scope: rg
  params: {
    name: bastionHostName
    location: location
    virtualNetworkResourceId: virtualNetwork.outputs.resourceId
    skuName: 'Developer'
    tags: tags
  }
}

output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
