targetScope = 'subscription'

// The main bicep module to provision Azure resources.
// For a more complete walkthrough to understand how this file works with azd,
// see https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/make-azd-compatible?pivots=azd-create

@description('Name of the the environment which is used to generate a short unique hash used in all resources.')
@minLength(1)
@maxLength(64)
param environmentName string

@description('Primary location for all resources')
@minLength(1)
param location string

@description('Name of the resource group to create. If not specified, a unique name will be generated.')
param resourceGroupName string = 'rg-${environmentName}'

@description('Optional friendly name for the AI Foundry Hub workspace.')
param aiFoundryHubFriendlyName string

@description('Optional description for the AI Foundry Hub workspace.')
param aiFoundryHubDescription string

@description('Array of public IPv4 addresses or CIDR ranges that will be added to the Azure AI Foundry Hub allow‑list when `azureNetworkIsolation` is true.')
param aiFoundryHubIpAllowList array = []

@description('Id of the user or app to assign application roles')
param principalId string

@description('Type of the principal referenced by *principalId*.')
@allowed([
  'User'
  'ServicePrincipal'
])
param principalIdType string = 'User'

@description('Enable network isolation. When false no virtual network, private endpoint or private DNS resources are created and all services expose public endpoints.')
param azureNetworkIsolation bool = true

@description('Should an Azure Bastion be created?')
param createBastionHost bool = false

@description('Disable API key authentication for AI Services and AI Search. Defaults to false.')
param disableApiKeys bool = false

@description('Enable purge protection on the Key Vault. When set to true the vault cannot be permanently deleted until purge protection is disabled. Defaults to false.')
param keyVaultEnablePurgeProtection bool = false

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
// Ensure the storage account name is ≤ 24 characters as required by Azure.
var storageAccounName = substring(toLower(replace('${abbrs.storageStorageAccounts}${environmentName}', '-', '')),0,24)
// Ensure the key vault name is ≤ 24 characters as required by Azure.
var keyVaultName = substring(toLower(replace('${abbrs.keyVaultVaults}${environmentName}', '-', '')),0,24)
var containerRegistryName = toLower(replace('${abbrs.containerRegistryRegistries}${environmentName}', '-', ''))
var aiSearchUserAssignedIdentityName = '${abbrs.managedIdentityUserAssignedIdentities}${abbrs.aiSearchSearchServices}${environmentName}'
var aiSearchName = '${abbrs.aiSearchSearchServices}${environmentName}'
var aiServicesName = '${abbrs.aiServicesAccounts}${environmentName}'
var aiServicesCustomSubDomainName = toLower(replace(environmentName, '-', ''))
// Ensure the AI Foundry Hub name is ≤ 32 characters as required by Azure.
var aiFoundryHubName = substring('${abbrs.aiFoundryHubs}${environmentName}',0,32)
var bastionHostName = '${abbrs.networkBastionHosts}${environmentName}'

var networkDefaultAction = azureNetworkIsolation ? 'Deny' : 'Allow'

// ---------- RESOURCE GROUP ----------
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: !empty(resourceGroupName) ? resourceGroupName : '${abbrs.resourcesResourceGroups}${environmentName}'
  location: location
  tags: tags
}

// ---------- MONITORING RESOURCES ----------
module logAnalyticsWorkspace 'br/public:avm/res/operational-insights/workspace:0.11.1' = {
  name: 'logAnalyticsWorkspace'
  scope: rg
  params: {
    name: logAnalyticsName
    location: location
    tags: tags
  }
}

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

// ---------- VIRTUAL NETWORK (REQUIRED FOR NETOWRK ISOLATION) ----------
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

module virtualNetwork 'br/public:avm/res/network/virtual-network:0.6.1' = if (azureNetworkIsolation) {
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

// ---------- PRIVTE DNS ZONES (REQUIRED FOR NETOWRK ISOLATION) ----------
module keyVaultPrivateDnsZone 'br/public:avm/res/network/private-dns-zone:0.7.1' = if (azureNetworkIsolation) {
  name: 'keyvault-private-dns-zone'
  scope: rg
  params: {
    name: 'privatelink.vaultcore.azure.net'
    location: 'global'
  }
}

module storageBlobPrivateDnsZone   'br/public:avm/res/network/private-dns-zone:0.7.1' = if (azureNetworkIsolation) {
  name: 'storage-blobservice-private-dns-zone'
  scope: rg
  params: {
    name: 'privatelink.blob.${environment().suffixes.storage}'
    location: 'global'
    tags: tags
  }
}

module containerRegistryPrivateDnsZone 'br/public:avm/res/network/private-dns-zone:0.7.1' = if (azureNetworkIsolation) {
  name: 'container-registry-private-dns-zone'
  scope: rg
  params: {
    name: 'privatelink.azurecr.io'
    location: 'global'
    tags: tags
  }
}

module aiSearchPrivateDnsZone 'br/public:avm/res/network/private-dns-zone:0.7.1' = if (azureNetworkIsolation) {
  name: 'ai-search-private-dns-zone'
  scope: rg
  params: {
    name: 'privatelink.search.windows.net'
    location: 'global'
    tags: tags
  }
}

module aiServicesPrivateDnsZone 'br/public:avm/res/network/private-dns-zone:0.7.1' = if (azureNetworkIsolation) {
  name: 'ai-services-private-dns-zone'
  scope: rg
  params: {
    name: 'privatelink.cognitiveservices.azure.com'
    location: 'global'
    tags: tags
  }
}

module aiHubApiMlPrivateDnsZone 'br/public:avm/res/network/private-dns-zone:0.7.1' = if (azureNetworkIsolation) {
  name: 'ai-hub-apiml-private-dns-zone'
  scope: rg
  params: {
    name: 'privatelink.api.azureml.ms'
    location: 'global'
    tags: tags
  }
}

module aiHubNotebooksPrivateDnsZone'br/public:avm/res/network/private-dns-zone:0.7.1' = if (azureNetworkIsolation) {
  name: 'ai-hub-notebooks-private-dns-zone'
  scope: rg
  params: {
    name: 'privatelink.notebooks.azure.net'
    location: 'global'
    tags: tags
  }
}

// ---------- KEY VAULT ----------
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
    enablePurgeProtection: keyVaultEnablePurgeProtection
    enableRbacAuthorization: true
    networkAcls: {
      bypass: 'AzureServices'
      defaultAction: networkDefaultAction
    }
    privateEndpoints: azureNetworkIsolation ? [
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
    ] : []
    tags: tags
  }
}

// ---------- STORAGE ACCOUNT ----------
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
      defaultAction: networkDefaultAction
    }
    privateEndpoints: azureNetworkIsolation ? [
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
    ] : []
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
      // Developer role assignments
      ...(!empty(principalId) ? [
        {
          roleDefinitionIdOrName: 'Contributor'
          principalType: principalIdType
          principalId: principalId
        }
        {
          roleDefinitionIdOrName: 'Storage Blob Data Contributor'
          principalType: principalIdType
          principalId: principalId
        }
        {
          roleDefinitionIdOrName: 'Storage File Data Privileged Contributor'
          principalType: principalIdType
          principalId: principalId
        }
      ] : [])
    ]
    sasExpirationPeriod: '180.00:00:00'
    skuName: 'Standard_LRS'
    tags: tags
  }
}

// ---------- CONTAINER REGISTRY ----------
module containerRegistry 'br/public:avm/res/container-registry/registry:0.9.1' = {
  name: 'container-registry-deployment'
  scope: rg
  params: {
    name: containerRegistryName
    location: location
    acrSku: 'Premium'
    acrAdminUserEnabled: false
    publicNetworkAccess: azureNetworkIsolation ? 'Disabled' : 'Enabled'
    exportPolicyStatus: 'disabled'
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
    privateEndpoints: azureNetworkIsolation ? [
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
    ] : []
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

// ---------- AI SEARCH ----------
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
    privateEndpoints: azureNetworkIsolation ? [
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
    ] : []
    publicNetworkAccess: azureNetworkIsolation ? 'Disabled' : 'Enabled'
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
      // Developer role assignments
      ...(!empty(principalId) ? [
        {
          roleDefinitionIdOrName: 'Search Service Contributor'
          principalType: principalIdType
          principalId: principalId
        }
        {
          roleDefinitionIdOrName: 'Search Index Data Contributor'
          principalType: principalIdType
          principalId: principalId
        }
      ] : [])
    ]
    semanticSearch: 'standard'
    tags: tags
  }
}

// ---------- AI SERVICES ----------
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
    privateEndpoints: azureNetworkIsolation ? [
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
    ] : []
    publicNetworkAccess: azureNetworkIsolation ? 'Disabled' : 'Enabled'
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
      {
        roleDefinitionIdOrName: 'Contributor'
        principalType: principalIdType
        principalId: principalId
      }
    ]
    sku: 'S0'
    tags: tags
  }
}

// ---------- AI FOUNDRY HUB ----------
module aiFoundryHub 'br/public:avm/res/machine-learning-services/workspace:0.12.0' = {
  name: 'ai-foundry-hub-workspace-deployment'
  scope: rg
  params: {
    name: aiFoundryHubName
    friendlyName: empty(aiFoundryHubFriendlyName) ? 'AI Foundry Hub (${environmentName})' : aiFoundryHubFriendlyName
    description: empty(aiFoundryHubDescription) ? 'AI Foundry Hub for ${environmentName}' : aiFoundryHubDescription
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
          // TODO: Update the authType to 'ManagedIdentity'
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
    ipAllowlist: aiFoundryHubIpAllowList
    managedIdentities: {
      systemAssigned: true
    }
    managedNetworkSettings: {
      firewallSku: 'Basic'
      isolationMode: 'AllowInternetOutbound'
    }
    publicNetworkAccess: azureNetworkIsolation ? 'Disabled' : 'Enabled'
    privateEndpoints: azureNetworkIsolation ? [
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
    ] : []
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

// ------------- BASTION HOST (OPTIONAL) -------------
module bastionHost 'br/public:avm/res/network/bastion-host:0.6.1' = if (createBastionHost && azureNetworkIsolation) {
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

output RESOURCE_GROUP string = rg.name
output RESOURCE_GROUP_ID string = rg.id

// Output the monitoring resources
output LOG_ANALYTICS_WORKSPACE_NAME string = logAnalyticsWorkspace.outputs.name
output LOG_ANALYTICS_RESOURCE_ID string = logAnalyticsWorkspace.outputs.resourceId
output LOG_ANALYTICS_WORKSPACE_ID string = logAnalyticsWorkspace.outputs.logAnalyticsWorkspaceId
output APPLICATION_INSIGHTS_NAME string = applicationInsights.outputs.name
output APPLICATION_INSIGHTS_RESOURCE_ID string = applicationInsights.outputs.resourceId
output APPLICATION_INSIGHTS_INSTRUMENTATION_KEY string = applicationInsights.outputs.instrumentationKey

// Output the network isolation resources
output VIRTUAL_NETWORK_NAME string = azureNetworkIsolation ? virtualNetwork.outputs.name : ''
output VIRTUAL_NETWORK_RESOURCE_ID string = azureNetworkIsolation ? virtualNetwork.outputs.resourceId : ''

// Output the supporting resources
output STORAGE_ACCOUNT_NAME string = storageAccount.outputs.name
output STORAGE_ACCOUNT_RESOURCE_ID string = storageAccount.outputs.resourceId
output STORAGE_ACCOUNT_BLOB_ENDPOINT string = storageAccount.outputs.primaryBlobEndpoint
output STORAGE_ACCOUNT_PRIVATE_ENDPOINTS array = storageAccount.outputs.privateEndpoints
output STORAGE_ACCOUNT_SERVICE_ENDPOINTS object = storageAccount.outputs.serviceEndpoints
output KEY_VAULT_NAME string = keyVault.outputs.name
output KEY_VAULT_RESOURCE_ID string = keyVault.outputs.resourceId
output KEY_VAULT_ENDPOINT string = keyVault.outputs.uri
output CONTAINER_REGISTRY_NAME string = containerRegistry.outputs.name
output CONTAINER_REGISTRY_ID string = containerRegistry.outputs.resourceId
output AI_SEARCH_NAME string = aiSearchService.outputs.name
output AI_SEARCH_ID string = aiSearchService.outputs.resourceId
output AI_SERVICES_NAME string = aiServicesAccount.outputs.name
output AI_SERVICES_ID string = aiServicesAccount.outputs.resourceId
output AI_SERVICES_ENDPOINT string = aiServicesAccount.outputs.endpoint
output AI_SERVICES_RESOURCE_ID string = aiServicesAccount.outputs.resourceId

// Output the Azure AI Foundry resources
output AI_FOUNDRY_HUB_NAME string = aiFoundryHub.outputs.name
output AI_FOUNDRY_HUB_RESOURCE_ID string = aiFoundryHub.outputs.resourceId
output AI_FOUNDRY_HUB_PRIVATE_ENDPOINTS array = aiFoundryHub.outputs.privateEndpoints

// Output the Bastion Host resources
output BASTION_HOST_NAME string = createBastionHost && azureNetworkIsolation ? bastionHost.outputs.name : ''
output BASTION_HOST_RESOURCE_ID string = createBastionHost && azureNetworkIsolation ? bastionHost.outputs.resourceId : ''
