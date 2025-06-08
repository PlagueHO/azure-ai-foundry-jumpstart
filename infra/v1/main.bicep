targetScope = 'subscription'
extension microsoftGraphV1

@sys.description('Name of the the environment which is used to generate a short unique hash used in all resources.')
@minLength(1)
@maxLength(40)
param environmentName string

@sys.description('Location for all resources')
@minLength(1)
@metadata({
  azd: {
    type: 'location'
  }
})
param location string

@sys.description('The Azure resource group where new resources will be deployed.')
@metadata({
  azd: {
    type: 'resourceGroup'
  }
})
param resourceGroupName string = 'rg-${environmentName}'

@sys.description('Enable purge protection on the Key Vault. When set to true the vault cannot be permanently deleted until purge protection is disabled. Defaults to false.')
param keyVaultEnablePurgeProtection bool = false

@sys.description('Optional friendly name for the AI Foundry Hub workspace.')
param aiFoundryHubFriendlyName string

@sys.description('Optional description for the AI Foundry Hub workspace.')
param aiFoundryHubDescription string

@sys.description('Array of public IPv4 addresses or CIDR ranges that will be added to the Azure AI Foundry Hub allow-list when azureNetworkIsolation is true.')
param aiFoundryHubIpAllowList array = []

@sys.description('SKU for the Azure AI Search service. Defaults to standard.')
@allowed([
  'standard'
  'standard2'
  'standard3'
  'storage_optimized_l1'
  'storage_optimized_l2'
])
param azureAiSearchSku string = 'standard'

@sys.description('Id of the user or app to assign application roles.')
param principalId string

@sys.description('Type of the principal referenced by principalId.')
@allowed([
  'User'
  'ServicePrincipal'
])
param principalIdType string = 'User'

@sys.description('Enable network isolation. When false no virtual network, private endpoint or private DNS resources are created and all services expose public endpoints')
param azureNetworkIsolation bool = true

@sys.description('Deploy an Azure Bastion Host to the virtual network. This is required for private endpoint access to the AI Foundry Hub and AI Services. Defaults to false.')
param bastionHostDeploy bool = false

@sys.description('Disable API key authentication for AI Services and AI Search. Defaults to false.')
param disableApiKeys bool = false

@sys.description('Deploy the sample OpenAI model deployments listed in ./sample-openai-models.json. Defaults to false')
param deploySampleOpenAiModels bool = false

@sys.description('Deploy sample data containers into the Azure Storage Account. Defaults to false.')
param deploySampleData bool = false

@sys.description('Resource ID of an existing Azure Container Registry (ACR) to use instead of deploying a new one. When provided the registry module is skipped. If `azureNetworkIsolation` is true you must ensure the registry has the required private networking configuration.')
param containerRegistryResourceId string = ''

@sys.description('Deploy Azure Container Registry and all dependent configuration. Set to false to skip its deployment.')
param containerRegistryDeploy bool = true

@sys.description('Deploy an Azure AI Foundry project. Set to false to skip its deployment.')
param aiFoundryProjectDeploy bool

@sys.description('The name of the Azure AI Foundry project to create.')
param aiFoundryProjectName string

@sys.description('The description of the Azure AI Foundry project to create.') 
param aiFoundryProjectDescription string

@sys.description('The friendly name of the Azure AI Foundry project to create.')
param aiFoundryProjectFriendlyName string

@sys.description('Use projects defined in sample-ai-foundry-projects.json file instead of the single project parameters. When true, the aiFoundryProject* parameters are ignored.')
param aiFoundryProjectsFromJson bool = false

@sys.description('Deploy Azure AI Search and all dependent configuration. Set to false to skip its deployment.')
param azureAiSearchDeploy bool = true

@sys.description('Override the default storage account name. Use the magic string `default` to fall back to the generated name.')
@minLength(3)
@maxLength(24)
param azureStorageAccountName string = 'default'

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
var storageAccountName = azureStorageAccountName == 'default'
  ? take(toLower(replace('${abbrs.storageStorageAccounts}${environmentName}', '-', '')), 24)
  : azureStorageAccountName
// Sample data storage account name - derive from foundry storage account with 'sample' postfix
var sampleDataStorageAccountName = take(toLower(replace('${storageAccountName}sample', '-', '')), 24)
// Ensure the key vault name is ≤ 24 characters as required by Azure.
var keyVaultName = take(toLower(replace('${abbrs.keyVaultVaults}${environmentName}', '-', '')),24)
var containerRegistryName = toLower(replace('${abbrs.containerRegistryRegistries}${environmentName}', '-', ''))
var aiSearchName = '${abbrs.aiSearchSearchServices}${environmentName}'
var aiServicesName = '${abbrs.aiServicesAccounts}${environmentName}'
var aiServicesCustomSubDomainName = toLower(replace(environmentName, '-', ''))
// Ensure the AI Foundry Hub name is ≤ 32 characters as required by Azure.
var aiFoundryHubName = take('${abbrs.aiFoundryHubs}${environmentName}',32)
var bastionHostName = '${abbrs.networkBastionHosts}${environmentName}'
var networkDefaultAction = azureNetworkIsolation ? 'Deny' : 'Allow'

// List of sample data containers
var sampleDataContainersArray = loadJsonContent('./sample-data-containers.json')

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
// Update subnet definitions to match architecture doc
var subnets = [
  {
    // Default subnet (generally not used)
    name: 'Default'
    addressPrefix: '10.0.0.0/24'
  }
  {
    // AiServices Subnet (AI Foundry Hub, AI Search, AI Services private endpoints)
    name: 'AiServices'
    addressPrefix: '10.0.1.0/24'
  }
  {
    // Data Subnet (Storage, Key Vault)
    name: 'Data'
    addressPrefix: '10.0.2.0/24'
  }
  {
    // Container Registry Subnet (ACR private endpoints)
    name: 'ContainerRegistry'
    addressPrefix: '10.0.3.0/24'
  }
  {
    // Management Subnet (Log Analytics, Application Insights)
    name: 'Management'
    addressPrefix: '10.0.4.0/24'
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

module aiSearchPrivateDnsZone 'br/public:avm/res/network/private-dns-zone:0.7.1' = if (azureNetworkIsolation && azureAiSearchDeploy) {
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
        subnetResourceId: virtualNetwork.outputs.subnetResourceIds[2] // SharedServices
      }
    ] : []
    tags: tags
  }
}

// ---------- STORAGE ACCOUNT ----------
// Role assignments for Storage Account
var storageAccountRoleAssignments = [
  ...(azureAiSearchDeploy ? [
    {
      roleDefinitionIdOrName: 'Storage Blob Data Contributor'
      principalType: 'ServicePrincipal'
      principalId: aiSearchService.outputs.?systemAssignedMIPrincipalId
    }
  ] : [])
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

// Sample data containers for the storage account
var sampleDataContainers = [for name in sampleDataContainersArray: {
  name: name
  publicAccess: 'None'
}]

module storageAccount 'br/public:avm/res/storage/storage-account:0.19.0' = {
  name: 'storage-account-deployment'
  scope: rg
  params: {
    // use the computed storageAccountName
    name: storageAccountName
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
    enableHierarchicalNamespace: false // not supported for AI Foundry
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
        subnetResourceId: virtualNetwork.outputs.subnetResourceIds[2] // SharedServices
        tags: tags
      }
    ] : []
    roleAssignments: storageAccountRoleAssignments
    sasExpirationPeriod: '180.00:00:00'
    skuName: 'Standard_LRS'
    tags: tags
  }
}

// ---------- SAMPLE DATA STORAGE ACCOUNT (CONDITIONAL) ----------
module sampleDataStorageAccount 'br/public:avm/res/storage/storage-account:0.19.0' = if (deploySampleData) {
  name: 'sample-data-storage-account-deployment'
  scope: rg
  params: {
    name: sampleDataStorageAccountName
    allowBlobPublicAccess: false
    blobServices: {
      automaticSnapshotPolicyEnabled: false
      containerDeleteRetentionPolicyEnabled: false
      deleteRetentionPolicyEnabled: false
      lastAccessTimeTrackingPolicyEnabled: true
      containers: sampleDataContainers
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
    enableHierarchicalNamespace: false // not supported for AI Foundry
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
        subnetResourceId: virtualNetwork.outputs.subnetResourceIds[2] // Data subnet
        tags: tags
      }
    ] : []
    roleAssignments: storageAccountRoleAssignments
    sasExpirationPeriod: '180.00:00:00'
    skuName: 'Standard_LRS'
    tags: tags
  }
}

// ---------- CONTAINER REGISTRY ----------
module containerRegistry 'br/public:avm/res/container-registry/registry:0.9.1' = if (containerRegistryDeploy && empty(containerRegistryResourceId)) {
  name: 'container-registry-deployment'
  scope: rg
  params: {
    name: containerRegistryName
    location: location
    acrSku: 'Premium'
    acrAdminUserEnabled: false
    publicNetworkAccess: azureNetworkIsolation ? 'Disabled' : 'Enabled'
    exportPolicyStatus: azureNetworkIsolation ? 'disabled' : 'enabled'
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
        subnetResourceId: virtualNetwork.outputs.subnetResourceIds[2] // SharedServices
        tags: tags
      }
    ] : []
  }
}

// Effective ACR resource-id used by the hub ('' when not deploying / skipped)
var effectiveContainerRegistryResourceId = containerRegistryDeploy
  ? (empty(containerRegistryResourceId) ? containerRegistry.outputs.resourceId : containerRegistryResourceId)
  : ''

// ---------- AI SEARCH ----------
module aiSearchService 'br/public:avm/res/search/search-service:0.10.0' = if (azureAiSearchDeploy) {
  name: 'ai-search-service-deployment'
  scope: rg
  params: {
    name: aiSearchName
    location: location
    sku: azureAiSearchSku
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
        subnetResourceId: virtualNetwork.outputs.subnetResourceIds[1] // AiServices
        tags: tags
      }
    ] : []
    publicNetworkAccess: azureNetworkIsolation ? 'Disabled' : 'Enabled'
    semanticSearch: 'standard'
    tags: tags
  }
}

// The Service Principal of the Azure Machine Learning service.
// This is used to assign the Reader role for AI Search and AI Services.
resource azureMachineLearningServicePrincipal 'Microsoft.Graph/servicePrincipals@v1.0' = {
  appId: '0736f41a-0425-4b46-bdb5-1563eff02385' // Azure Machine Learning service principal
}

// Role assignments (only when Search exists)
var aiSearchRoleAssignmentsArray = azureAiSearchDeploy ? [
  {
    roleDefinitionIdOrName: 'Search Index Data Contributor'
    principalType: 'ServicePrincipal'
    principalId: aiServicesAccount.outputs.?systemAssignedMIPrincipalId
  }
  {
    roleDefinitionIdOrName: 'Search Index Data Reader'
    principalType: 'ServicePrincipal'
    principalId: aiServicesAccount.outputs.?systemAssignedMIPrincipalId
  }
  {
    roleDefinitionIdOrName: 'Search Service Contributor'
    principalType: 'ServicePrincipal'
    principalId: aiServicesAccount.outputs.?systemAssignedMIPrincipalId
  }
  {
      roleDefinitionIdOrName: 'Reader'
      principalType: 'ServicePrincipal'
      principalId: azureMachineLearningServicePrincipal.id
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
] : []

module aiSearchRoleAssignments './core/security/role_aisearch.bicep' = if (azureAiSearchDeploy) {
  name: 'ai-search-role-assignments'
  scope: rg
  dependsOn: [
    aiSearchService
  ]
  params: {
    azureAiSearchName: aiSearchName
    roleAssignments: aiSearchRoleAssignmentsArray
  }
}

// ---------- AI SERVICES ----------
var openAiSampleModels = loadJsonContent('./sample-openai-models.json')

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
        subnetResourceId: virtualNetwork.outputs.subnetResourceIds[1] // AiServices
        tags: tags
      }
    ] : []
    publicNetworkAccess: azureNetworkIsolation ? 'Disabled' : 'Enabled'
    sku: 'S0'
    deployments: deploySampleOpenAiModels ? openAiSampleModels : []
    tags: tags
  }
}

// Add role assignments for AI Services using the role_aiservice.bicep module
// This needs to be done after the AI Services account is created to avoid circular dependencies
// between the AI Services account and the AI Search service.
var aiServicesRoleAssignmentsArray = [
  // search–specific roles only when search is present
  ...(azureAiSearchDeploy ? [
    {
      roleDefinitionIdOrName: 'Cognitive Services Contributor'
      principalType: 'ServicePrincipal'
      principalId: aiSearchService.outputs.?systemAssignedMIPrincipalId
    }
    {
      roleDefinitionIdOrName: 'Cognitive Services OpenAI Contributor'
      principalType: 'ServicePrincipal'
      principalId: aiSearchService.outputs.?systemAssignedMIPrincipalId
    }
  ] : [])
  // Developer role assignments
  ...(!empty(principalId) ? [
    {
      roleDefinitionIdOrName: 'Contributor'
      principalType: principalIdType
      principalId: principalId
    }
    {
      roleDefinitionIdOrName: 'Cognitive Services OpenAI Contributor'
      principalType: principalIdType
      principalId: principalId
    }
    {
      roleDefinitionIdOrName: 'Reader'
      principalType: 'ServicePrincipal'
      principalId: azureMachineLearningServicePrincipal.id
    }
  ] : [])
]

module aiServicesRoleAssignments './core/security/role_aiservice.bicep' = {
  name: 'ai-services-role-assignments'
  scope: rg
  dependsOn: [
    aiServicesAccount
  ]
  params: {
    azureAiServiceName: aiServicesName
    roleAssignments: aiServicesRoleAssignmentsArray
  }
}

// ---------- AI FOUNDRY HUB ----------
// Role assignments for the AI Foundry Hub
var aiFoundryHubRoleAssignments = !empty(principalId) ? [
  {
    roleDefinitionIdOrName: '/providers/Microsoft.Authorization/roleDefinitions/b78c5d69-af96-48a3-bf8d-a8b4d589de94' // 'Azure AI Administrator'
    principalType: principalIdType
    principalId: principalId
  }
] : []

var aiFoundryHubConnections = concat([
  {
    // AIServices connection
    category: 'AIServices'
    connectionProperties: {
      authType: 'AAD'
    }
    metadata: {
      ApiType: 'Azure'
      ApiVersion: '2023-07-01-preview'
      DeploymentApiVersion: '2023-10-01-preview'
      Location: location
      ResourceId: aiServicesAccount.outputs.resourceId
    }
    // Full aiServicesName can't be used because may cause deployment name to be too long
    name: replace(abbrs.aiServicesAccounts,'-','')
    target: aiServicesAccount.outputs.endpoint
    isSharedToAll: true
  }
], azureAiSearchDeploy ? [
  {
    // CognitiveSearch connection
    category: 'CognitiveSearch'
    connectionProperties: {
      authType: 'AAD'
    }
    metadata: {
      Type: 'azure_ai_search'
      ApiType: 'Azure'
      ApiVersion: '2024-05-01-preview'
      DeploymentApiVersion: '2023-11-01'
      Location: location
      ResourceId: aiSearchService.outputs.resourceId
    }
    // Full aiSearchName can't be used because may cause deployment name to be too long
    name: replace(abbrs.aiSearchSearchServices,'-','')
    target: aiSearchService.outputs.endpoint
    isSharedToAll: true
  }
] : [])

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
    associatedContainerRegistryResourceId: containerRegistryDeploy ? effectiveContainerRegistryResourceId : null
    connections: aiFoundryHubConnections
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
        subnetResourceId: virtualNetwork.outputs.subnetResourceIds[1] // AiServices
        tags: tags
      }
    ] : []
    provisionNetworkNow: true
    roleAssignments: aiFoundryHubRoleAssignments
    systemDatastoresAuthMode: 'Identity'
    tags: tags
    workspaceHubConfig: {
      defaultWorkspaceResourceGroup: rg.id
    }
  }
}

// ---------- AI FOUNDRY PROJECTS ----------
import { aiFoundryProjectType } from './types/ai/aiFoundryProjectType.bicep'

var projectsFromJson = loadJsonContent('./sample-ai-foundry-projects.json')

var aiFoundryProjectsFromJsonArray = [for project in projectsFromJson: {
  name: replace(project.Name,' ','-')
  friendlyName: project.FriendlyName
  description: project.Description
  roleAssignments: [
    {
      roleDefinitionIdOrName: 'AzureML Data Scientist'
      principalType: principalIdType
      principalId: principalId
    }
  ]
}]

var aiFoundryProjectsSingleArray = [
  {
    name: replace(aiFoundryProjectName,' ','-')
    friendlyName: aiFoundryProjectFriendlyName
    description: aiFoundryProjectDescription
    roleAssignments: [
      {
        roleDefinitionIdOrName: 'AzureML Data Scientist'
        principalType: principalIdType
        principalId: principalId
      }
    ]
  }
]

var effectiveAiFoundryProjects = aiFoundryProjectDeploy 
  ? (aiFoundryProjectsFromJson ? aiFoundryProjectsFromJsonArray : aiFoundryProjectsSingleArray)
  : []

module aiFoundryHubProjects 'br/public:avm/res/machine-learning-services/workspace:0.12.0' = [for project in effectiveAiFoundryProjects: {
  name: take('aifp-${project.name}',64)
  scope: rg
  params: {
    name: project.name
    friendlyName: project.friendlyName
    description: project.description
    location: location
    kind: 'Project'
    sku: 'Basic'
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
    hubResourceId: aiFoundryHub.outputs.resourceId
    managedIdentities: {
      systemAssigned: true
    }
    publicNetworkAccess: azureNetworkIsolation ? 'Disabled' : 'Enabled'
    roleAssignments: project.roleAssignments ?? []
    tags: tags
  }
}]

// ---------- AI FOUNDRY PROJECTS ROLE ASSIGNMENTS TO AI SERVICES ----------
// Add any Azure AI Developer role for each AI Foundry project to the AI Services account
// This ensures a developer with access to the AI Foundry project can also access the AI Services
module aiFoundryProjectToAiServiceRoleAssignments './core/security/role_aiservice.bicep' = [
  for (project,index) in effectiveAiFoundryProjects: {
  name: take('aifp-aisvc-ra-${project.name}',64)
  scope: rg
  dependsOn: [
    aiFoundryHubProjects
  ]
  params: {
    azureAiServiceName: aiServicesName
    roleAssignments: [
      {
        roleDefinitionIdOrName: '/providers/Microsoft.Authorization/roleDefinitions/64702f94-c441-49e6-a78b-ef80e0188fee' // 'Azure AI Developer'
        principalType: 'ServicePrincipal'
        principalId: aiFoundryHubProjects[index].outputs.systemAssignedMIPrincipalId
      }
    ]
  }
}]

// ---------- AI FOUNDRY PROJECT ROLE ASSIGNMENTS TO AI SEARCH ----------
// Add any Search Index Reader and Search Service Contributor roles for each AI Foundry project
// to the AI Search Account. This ensures Agents created within a project can access indexes in
// the AI Search account.
module aiFoundryProjectToAiSearchRoleAssignments './core/security/role_aisearch.bicep' = [
  for (project,index) in effectiveAiFoundryProjects : if (azureAiSearchDeploy) {
    name: take('aifp-aisch-ra-${project.name}',64)
    scope: rg
    dependsOn: [
      aiFoundryHubProjects
    ]
    params: {
      azureAiSearchName: aiSearchName
      roleAssignments: [
        {
          roleDefinitionIdOrName: 'Search Index Data Reader'
          principalType: 'ServicePrincipal'
          principalId: aiFoundryHubProjects[index].outputs.systemAssignedMIPrincipalId
        }
        {
          roleDefinitionIdOrName: 'Search Service Contributor'
          principalType: 'ServicePrincipal'
          principalId: aiFoundryHubProjects[index].outputs.systemAssignedMIPrincipalId
        }
      ]
    }
  }
]

// ---------- AI FOUNDRY PROJECTS DATASTORES ----------
// Build a Cartesian product index across projects and sample-data containers
var projectCount   = length(effectiveAiFoundryProjects)
var sampleDataContainerCount = length(sampleDataContainersArray)

// One module instance per <project, container> when deploySampleData == true
module projectSampleDataStores 'core/ai/ai-foundry-project-datastore.bicep' = [
  for idx in range(0, (projectCount * sampleDataContainerCount)) : if (deploySampleData && aiFoundryProjectDeploy) {
    // Make the module deployment name unique
    name: replace(toLower(take('datastore_${effectiveAiFoundryProjects[idx / sampleDataContainerCount].name}_${sampleDataContainersArray[idx % sampleDataContainerCount]}',64)),'-','_')
    scope: rg
    dependsOn: [
      aiFoundryHubProjects
    ]
    params: {
      projectWorkspaceName: aiFoundryHubProjects[idx / sampleDataContainerCount].outputs.name
      storageAccountName: sampleDataStorageAccountName
      storageContainerName: sampleDataContainersArray[idx % sampleDataContainerCount]
      dataStoreName: replace(toLower(sampleDataContainersArray[idx % sampleDataContainerCount]),'-','_')
    }
  }
]

// ------------- BASTION HOST (OPTIONAL) -------------
module bastionHost 'br/public:avm/res/network/bastion-host:0.6.1' = if (bastionHostDeploy && azureNetworkIsolation) {
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

output AZURE_RESOURCE_GROUP string = rg.name
output AZURE_PRINCIPAL_ID string = principalId
output AZURE_PRINCIPAL_ID_TYPE string = principalIdType

// Output the monitoring resources
output LOG_ANALYTICS_WORKSPACE_NAME string = logAnalyticsWorkspace.outputs.name
output LOG_ANALYTICS_RESOURCE_ID string = logAnalyticsWorkspace.outputs.resourceId
output LOG_ANALYTICS_WORKSPACE_ID string = logAnalyticsWorkspace.outputs.logAnalyticsWorkspaceId
output APPLICATION_INSIGHTS_NAME string = applicationInsights.outputs.name
output APPLICATION_INSIGHTS_RESOURCE_ID string = applicationInsights.outputs.resourceId
output APPLICATION_INSIGHTS_INSTRUMENTATION_KEY string = applicationInsights.outputs.instrumentationKey

// Output the network isolation resources
output AZURE_NETWORK_ISOLATION bool = azureNetworkIsolation
output AZURE_VIRTUAL_NETWORK_NAME string = azureNetworkIsolation ? virtualNetwork.outputs.name : ''
output AZURE_VIRTUAL_NETWORK_RESOURCE_ID string = azureNetworkIsolation ? virtualNetwork.outputs.resourceId : ''

// Output the supporting resources
output AZURE_STORAGE_ACCOUNT_NAME string = storageAccount.outputs.name
output AZURE_STORAGE_ACCOUNT_RESOURCE_ID string = storageAccount.outputs.resourceId
output AZURE_STORAGE_ACCOUNT_BLOB_ENDPOINT string = storageAccount.outputs.primaryBlobEndpoint
output AZURE_STORAGE_ACCOUNT_PRIVATE_ENDPOINTS array = storageAccount.outputs.privateEndpoints
output AZURE_STORAGE_ACCOUNT_SERVICE_ENDPOINTS object = storageAccount.outputs.serviceEndpoints
output AZURE_SAMPLE_DATA_STORAGE_ACCOUNT_NAME string = deploySampleData ? sampleDataStorageAccount.outputs.name : ''
output AZURE_SAMPLE_DATA_STORAGE_ACCOUNT_RESOURCE_ID string = deploySampleData ? sampleDataStorageAccount.outputs.resourceId : ''
output AZURE_SAMPLE_DATA_STORAGE_ACCOUNT_BLOB_ENDPOINT string = deploySampleData ? sampleDataStorageAccount.outputs.primaryBlobEndpoint : ''
output AZURE_KEY_VAULT_NAME string = keyVault.outputs.name
output AZURE_KEY_VAULT_RESOURCE_ID string = keyVault.outputs.resourceId
output AZURE_KEY_VAULT_ENDPOINT string = keyVault.outputs.uri
output AZURE_KEY_VAULT_ENABLE_PURGE_PROTECTION bool = keyVaultEnablePurgeProtection
output AZURE_CONTAINER_REGISTRY_DEPLOY bool = containerRegistryDeploy
output AZURE_CONTAINER_REGISTRY_NAME string = (containerRegistryDeploy && empty(containerRegistryResourceId)) ? containerRegistry.outputs.name : ''
output AZURE_CONTAINER_REGISTRY_RESOURCE_ID   string = containerRegistryDeploy
  ? (empty(containerRegistryResourceId) ? containerRegistry.outputs.resourceId : containerRegistryResourceId)
  : ''

// Output the AI resources
output AZURE_DISABLE_API_KEYS bool = disableApiKeys
output AZURE_AI_SEARCH_NAME string = azureAiSearchDeploy ? aiSearchService.outputs.name : ''
output AZURE_AI_SEARCH_ID   string = azureAiSearchDeploy ? aiSearchService.outputs.resourceId : ''
output AZURE_AI_SERVICES_NAME string = aiServicesAccount.outputs.name
output AZURE_AI_SERVICES_ID string = aiServicesAccount.outputs.resourceId
output AZURE_AI_SERVICES_ENDPOINT string = aiServicesAccount.outputs.endpoint
output AZURE_AI_SERVICES_RESOURCE_ID string = aiServicesAccount.outputs.resourceId

// Output the Azure AI Foundry resources
output AZURE_AI_FOUNDRY_HUB_NAME string = aiFoundryHub.outputs.name
output AZURE_AI_FOUNDRY_HUB_RESOURCE_ID string = aiFoundryHub.outputs.resourceId
output AZURE_AI_FOUNDRY_HUB_PRIVATE_ENDPOINTS array = aiFoundryHub.outputs.privateEndpoints

// Output the AI Foundry project
output AZURE_AI_FOUNDRY_PROJECT_DEPLOY bool = aiFoundryProjectDeploy
output AZURE_AI_FOUNDRY_PROJECTS_FROM_JSON bool = aiFoundryProjectsFromJson
output AZURE_AI_FOUNDRY_PROJECT_NAME string = aiFoundryProjectDeploy ? aiFoundryProjectName : ''
output AZURE_AI_FOUNDRY_PROJECT_DESCRIPTION string = aiFoundryProjectDeploy ? aiFoundryProjectDescription : ''
output AZURE_AI_FOUNDRY_PROJECT_FRIENDLY_NAME string = aiFoundryProjectDeploy ? aiFoundryProjectFriendlyName : ''

// Output the Bastion Host resources
output AZURE_BASTION_HOST_DEPLOY bool = bastionHostDeploy
output AZURE_BASTION_HOST_NAME string = bastionHostDeploy && azureNetworkIsolation ? bastionHost.outputs.name : ''
output AZURE_BASTION_HOST_RESOURCE_ID string = bastionHostDeploy && azureNetworkIsolation ? bastionHost.outputs.resourceId : ''
