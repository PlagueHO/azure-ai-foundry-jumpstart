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

@sys.description('Deploy Azure AI Foundry Hub (MachineLearning workspace) and supporting resources (Key Vault, Storage Account, Container Registry). When false, only Azure AI Services with ProjectMode is deployed. Defaults to false.')
param aiFoundryHubDeploy bool = false

@sys.description('Deploy AI Foundry projects to the AI Foundry Hub instead of the Azure AI Foundry. Set to false to skip creation of Azure AI Foundry projects to the AI Foundry Hub resource. Only applies when aiFoundryHubDeploy is true. Defaults to false.')
param aiFoundryHubProjectDeploy bool = false

@sys.description('Enable purge protection on the Key Vault. When set to true the vault cannot be permanently deleted until purge protection is disabled. Defaults to false. Only applies when aiFoundryHubDeploy is true.')
param keyVaultEnablePurgeProtection bool = false

@sys.description('Optional friendly name for the AI Foundry Hub workspace. Only applies when aiFoundryHubDeploy is true.')
param aiFoundryHubFriendlyName string

@sys.description('Optional description for the AI Foundry Hub workspace. Only applies when aiFoundryHubDeploy is true.')
param aiFoundryHubDescription string

@sys.description('Array of public IPv4 addresses or CIDR ranges that will be added to the Azure AI Foundry allow-list when azureNetworkIsolation is true.')
param aiFoundryIpAllowList array = []

@sys.description('SKU for the Azure AI Search service. Defaults to standard.')
@allowed([
  'standard'
  'standard2'
  'standard3'
  'storage_optimized_l1'
  'storage_optimized_l2'
])
param azureAiSearchSku string = 'standard'

@sys.description('Number of replicas in the Azure AI Search service. Must be between 1 and 12. Defaults to 1.')
@minValue(1)
@maxValue(12)
param azureAiSearchReplicaCount int = 1

@sys.description('Number of partitions in the Azure AI Search service. Must be 1, 2, 3, 4, 6, or 12. Defaults to 1.')
@allowed([1, 2, 3, 4, 6, 12])
param azureAiSearchPartitionCount int = 1

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

@sys.description('Resource ID of an existing Azure Container Registry (ACR) to use instead of deploying a new one. When provided the registry module is skipped. If `azureNetworkIsolation` is true you must ensure the registry has the required private networking configuration. Only applies when aiFoundryHubDeploy is true.')
param containerRegistryResourceId string = ''

@sys.description('Deploy Azure Container Registry and all dependent configuration. Set to false to skip its deployment. Only applies when aiFoundryHubDeploy is true. Defaults to true.')
param containerRegistryDeploy bool = true

@sys.description('Deploy AI Foundry projects to the AI Foundry resource. Set to false to skip creation of Azure AI Foundry projects to the AI Foundry resource. Defaults to false.')
param aiFoundryProjectDeploy bool = false

@sys.description('The name of the AI Foundry project to create.')
param aiFoundryProjectName string

@sys.description('The description of the Azure AI Foundry project to create.') 
param aiFoundryProjectDescription string

@sys.description('The friendly name of the Azure AI Foundry project to create.')
param aiFoundryProjectFriendlyName string

@sys.description('Use projects defined in sample-ai-foundry-projects.json file instead of the single project parameters. When true, the aiFoundryProject* parameters are ignored. Defaults to false.')
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

var effectiveResourceGroupName = !empty(resourceGroupName) ? resourceGroupName : '${abbrs.resourcesResourceGroups}${environmentName}'
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
var aiSearchServiceName = '${abbrs.aiSearchSearchServices}${environmentName}'
var aiFoundryServiceName = '${abbrs.aiFoundryAccounts}${environmentName}'
var aiFoundryCustomSubDomainName = toLower(replace(environmentName, '-', ''))
// Ensure the AI Foundry Hub name is ≤ 32 characters as required by Azure.
var aiFoundryHubName = take('${abbrs.aiFoundryHubs}${environmentName}',32)
var bastionHostName = '${abbrs.networkBastionHosts}${environmentName}'
var networkDefaultAction = azureNetworkIsolation ? 'Deny' : 'Allow'

// Assemble list of sample data containers
var sampleDataContainersArray = loadJsonContent('./sample-data-containers.json')
var sampleDataContainers = [for name in sampleDataContainersArray: {
  name: name
  publicAccess: 'None'
}]

// Load sample OpenAI models from JSON file
var openAiSampleModels = loadJsonContent('./sample-openai-models.json')

// Build a Cartesian product index across projects and sample-data containers
var sampleDataContainerCount = length(sampleDataContainersArray)

// Transform IP allow list for networkAcls
var aiFoundryIpRules = [for ip in aiFoundryIpAllowList: {
  value: ip
}]

// ---------- PROJECT DEPLOYMENT LOGIC ----------
// Stage 1: Determine if we should deploy projects and create the effective project list

// Check if we should deploy projects to either AI Foundry Hub or AI Services
var shouldDeployProjects = (aiFoundryHubProjectDeploy && aiFoundryHubDeploy) || aiFoundryProjectDeploy

// Load projects from JSON file for reference
var projectsFromJson = loadJsonContent('./sample-ai-foundry-projects.json')

// Stage 2: Create the effective list of projects to deploy
// This list contains the base project information that will be used by both deployment scenarios
var effectiveProjectList = shouldDeployProjects 
  ? (aiFoundryProjectsFromJson 
      ? projectsFromJson
      : [
          {
            Name: aiFoundryProjectName
            FriendlyName: aiFoundryProjectFriendlyName
            Description: aiFoundryProjectDescription
          }
        ])
  : []

// Stage 3: Transform the effective project list for AI Foundry Hub deployment
// Only create this list if we're deploying to Hub
var aiFoundryHubProjectsSourceList = (aiFoundryHubDeploy && aiFoundryHubProjectDeploy) ? effectiveProjectList : []

var aiFoundryHubProjectsList = [for project in aiFoundryHubProjectsSourceList: {
  name: replace(project.Name, ' ', '-')
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

// Stage 4: Transform the effective project list for AI Services deployment
// Only deploy to AI Services if not deploying to Hub
var aiFoundryServiceProjectsArray = (!aiFoundryHubProjectDeploy && aiFoundryProjectDeploy)
  ? effectiveProjectList
  : []

var aiFoundryServiceProjects = [for project in aiFoundryServiceProjectsArray: {
  name: replace(project.Name, ' ', '-')
  location: location
  properties: {
    displayName: project.FriendlyName
    description: project.Description
  }
  identity: {
    systemAssigned: true
  }
  roleAssignments: !empty(principalId) ? [
    {
      roleDefinitionIdOrName: 'Azure AI Developer'
      principalType: principalIdType
      principalId: principalId
    }
  ] : []
}]

var projectCount = length(effectiveProjectList)

// ---------- RESOURCE GROUP (BOTH HUB AND PROJECT MODE) ----------
module resourceGroup 'br/public:avm/res/resources/resource-group:0.4.1' = {
  name: 'resource-group-deployment-${location}'
  params: {
    name: effectiveResourceGroupName
    location: location
    tags: tags
  }
}

// ---------- MONITORING RESOURCES (BOTH HUB AND PROJECT MODE) ----------
module logAnalyticsWorkspace 'br/public:avm/res/operational-insights/workspace:0.12.0' = {
  name: 'logAnalytics-workspace-deployment'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [resourceGroup]
  params: {
    name: logAnalyticsName
    location: location
    tags: tags
  }
}

module applicationInsights 'br/public:avm/res/insights/component:0.6.0' = {
  name: 'application-insights-deployment'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [resourceGroup]
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
    privateEndpointNetworkPolicies: 'Disabled'
    privateLinkServiceNetworkPolicies: 'Disabled'
  }
  {
    // AiServices Subnet (AI Foundry Hub, AI Search, AI Services private endpoints)
    name: 'AiServices'
    addressPrefix: '10.0.1.0/24'
    privateEndpointNetworkPolicies: 'Disabled'
    privateLinkServiceNetworkPolicies: 'Disabled'
  }
  {
    // Data Subnet (Storage, Key Vault, Container Registry)
    name: 'Data'
    addressPrefix: '10.0.2.0/24'
    privateEndpointNetworkPolicies: 'Disabled'
    privateLinkServiceNetworkPolicies: 'Disabled'
  }
  {
    // Management Subnet (Log Analytics, Application Insights) - Not used yet
    name: 'Management'
    addressPrefix: '10.0.3.0/24'
    privateEndpointNetworkPolicies: 'Disabled'
    privateLinkServiceNetworkPolicies: 'Disabled'
  }
  {
    // Bastion Gateway Subnet
    name: 'AzureBastionSubnet'
    addressPrefix: '10.0.255.0/27'
    privateEndpointNetworkPolicies: 'Disabled'
    privateLinkServiceNetworkPolicies: 'Disabled'
  }
]

module virtualNetwork 'br/public:avm/res/network/virtual-network:0.7.0' = if (azureNetworkIsolation) {
  name: 'virtualNetwork'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [resourceGroup]
  params: {
    name: virtualNetworkName
    location: location
    addressPrefixes: [
      '10.0.0.0/16'
    ]
    subnets: subnets
    tags: tags
    ddosProtectionPlanResourceId: null // Corrected parameter name
  }
}

// ---------- PRIVTE DNS ZONES (REQUIRED FOR NETOWRK ISOLATION) ----------
module storageBlobPrivateDnsZone 'br/public:avm/res/network/private-dns-zone:0.7.1' = if ((aiFoundryHubDeploy || deploySampleData) && azureNetworkIsolation) {
  name: 'storage-blobservice-private-dns-zone'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [resourceGroup]
  params: {
    name: 'privatelink.blob.${environment().suffixes.storage}'
    location: 'global'
    tags: tags
    virtualNetworkLinks: [
      {
        virtualNetworkResourceId: virtualNetwork.outputs.resourceId
        registrationEnabled: false
      }
    ]
  }
}

// Private DNS zones for AI Search
module aiSearchPrivateDnsZone 'br/public:avm/res/network/private-dns-zone:0.7.1' = if (azureNetworkIsolation && azureAiSearchDeploy) {
  name: 'ai-search-private-dns-zone'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [resourceGroup]
  params: {
    name: 'privatelink.search.windows.net'
    location: 'global'
    tags: tags
    virtualNetworkLinks: [
      {
        virtualNetworkResourceId: virtualNetwork.outputs.resourceId
        registrationEnabled: false
      }
    ]
  }
}

// Private DNS zones for AI Foundry Hub
module aiHubApiMlPrivateDnsZone 'br/public:avm/res/network/private-dns-zone:0.7.1' = if (aiFoundryHubDeploy && azureNetworkIsolation) {
  name: 'ai-hub-apiml-private-dns-zone'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [resourceGroup]
  params: {
    name: 'privatelink.api.azureml.ms'
    location: 'global'
    tags: tags
    virtualNetworkLinks: [
      {
        virtualNetworkResourceId: virtualNetwork.outputs.resourceId
        registrationEnabled: false
      }
    ]
  }
}

module aiHubNotebooksPrivateDnsZone 'br/public:avm/res/network/private-dns-zone:0.7.1' = if (aiFoundryHubDeploy && azureNetworkIsolation) {
  name: 'ai-hub-notebooks-private-dns-zone'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [resourceGroup]
  params: {
    name: 'privatelink.notebooks.azure.net'
    location: 'global'
    tags: tags
    virtualNetworkLinks: [
      {
        virtualNetworkResourceId: virtualNetwork.outputs.resourceId
        registrationEnabled: false
      }
    ]
  }
}

// Private DNS zones for AI Foundry Hub dependencies
module keyVaultPrivateDnsZone 'br/public:avm/res/network/private-dns-zone:0.7.1' = if (aiFoundryHubDeploy && azureNetworkIsolation) {
  name: 'keyvault-private-dns-zone'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [resourceGroup]
  params: {
    name: 'privatelink.vaultcore.azure.net'
    location: 'global'
    tags: tags
    virtualNetworkLinks: [
      {
        virtualNetworkResourceId: virtualNetwork.outputs.resourceId
        registrationEnabled: false
      }
    ]
  }
}


module containerRegistryPrivateDnsZone 'br/public:avm/res/network/private-dns-zone:0.7.1' = if (aiFoundryHubDeploy && azureNetworkIsolation) {
  name: 'container-registry-private-dns-zone'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [resourceGroup]
  params: {
    name: 'privatelink.azurecr.io'
    location: 'global'
    tags: tags
    virtualNetworkLinks: [
      {
        virtualNetworkResourceId: virtualNetwork.outputs.resourceId
        registrationEnabled: false
      }
    ]
  }
}

// Private DNS zones for AI Services
module aiServicesPrivateDnsZone 'br/public:avm/res/network/private-dns-zone:0.7.1' = if (azureNetworkIsolation) {
  name: 'ai-services-private-dns-zone'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [resourceGroup]
  params: {
    name: 'privatelink.cognitiveservices.azure.com'
    location: 'global'
    tags: tags
    virtualNetworkLinks: [
      {
        virtualNetworkResourceId: virtualNetwork.outputs.resourceId
        registrationEnabled: false
      }
    ]
  }
}

module aiServicesOpenAiDnsZone 'br/public:avm/res/network/private-dns-zone:0.7.1' = if (azureNetworkIsolation) {
  name: 'ai-services-openai-dns-zone'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [resourceGroup]
  params: {
    name: 'privatelink.openai.azure.com'
    location: 'global'
    tags: tags
    virtualNetworkLinks: [
      {
        virtualNetworkResourceId: virtualNetwork.outputs.resourceId
        registrationEnabled: false
      }
    ]
  }
}

module aiServicesAiDnsZone 'br/public:avm/res/network/private-dns-zone:0.7.1' = if (azureNetworkIsolation) {
  name: 'ai-services-ai-dns-zone'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [resourceGroup]
  params: {
    name: 'privatelink.services.ai.azure.com'
    location: 'global'
    tags: tags
    virtualNetworkLinks: [
      {
        virtualNetworkResourceId: virtualNetwork.outputs.resourceId
        registrationEnabled: false
      }
    ]
  }
}

// ---------- KEY VAULT (HUB DEPLOY ONLY) ----------
module keyVault 'br/public:avm/res/key-vault/vault:0.13.0' = if (aiFoundryHubDeploy) {
  name: 'key-vault-deployment'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [resourceGroup]
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
        subnetResourceId: virtualNetwork.outputs.subnetResourceIds[2] // Data subnet
      }
    ] : []
    tags: tags
  }
}

// ---------- STORAGE ACCOUNT (HUB DEPLOY ONLY) ----------
module storageAccount 'br/public:avm/res/storage/storage-account:0.23.0' = if (aiFoundryHubDeploy) {
  name: 'hub-storage-account-deployment'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [resourceGroup]
  params: {
    name: storageAccountName
    location: location
    kind: 'StorageV2'
    skuName: 'Standard_LRS'
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    allowCrossTenantReplication: false
    blobServices: {
      containers: [
        {
          name: 'default'
          publicAccess: 'None'
        }
      ]
      deleteRetentionPolicy: {
        enabled: true
        days: 7
      }
      containerDeleteRetentionPolicy: {
        enabled: true
        days: 7
      }
    }
    supportsHttpsTrafficOnly: true // Corrected parameter name
    enableHierarchicalNamespace: false // Corrected parameter name (was isHnsEnabled)
    largeFileSharesState: 'Disabled'
    minimumTlsVersion: 'TLS1_2'
    networkAcls: {
      bypass: 'AzureServices'
      defaultAction: networkDefaultAction
    }
    publicNetworkAccess: azureNetworkIsolation ? 'Disabled' : 'Enabled'
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
    sasExpirationPeriod: '1.00:00:00'
    tags: tags
    allowSharedKeyAccess: true
  }
}

// ---------- CONTAINER REGISTRY (HUB DEPLOY ONLY) ----------
module containerRegistry 'br/public:avm/res/container-registry/registry:0.9.1' = if (aiFoundryHubDeploy && containerRegistryDeploy && empty(containerRegistryResourceId)) {
  name: 'container-registry-deployment'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [resourceGroup]
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
        subnetResourceId: virtualNetwork.outputs.subnetResourceIds[2] // Data Subnet
        tags: tags
      }
    ] : []
  }
}

// Effective ACR resource-id used by the hub ('' when not deploying / skipped)
var effectiveContainerRegistryResourceId = containerRegistryDeploy
  ? (empty(containerRegistryResourceId) ? containerRegistry.outputs.resourceId : containerRegistryResourceId)
  : ''

// ---------- STORAGE ACCOUNT SAMPLE DATA (OPTIONAL) ----------
module sampleDataStorageAccount 'br/public:avm/res/storage/storage-account:0.23.0' = if (deploySampleData) {
  name: 'sample-data-storage-account-deployment'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [resourceGroup]
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
    sasExpirationPeriod: '180.00:00:00'
    skuName: 'Standard_LRS'
    tags: tags
  }
}

// ---------- STORAGE ACCOUNT ROLE ASSIGNMENTS (HUB DEPLOY ONLY) ----------
module storageAccountRoles './core/security/role_storageaccount.bicep' = if (aiFoundryHubDeploy) {
  name: 'storage-account-role-assignments'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [
    resourceGroup
    storageAccount
  ]
  params: {
    azureStorageAccountName: storageAccountName
    roleAssignments: [
      // AI Foundry role assignments
      {
        roleDefinitionIdOrName: 'Storage Blob Data Contributor'
        principalType: 'ServicePrincipal'
        principalId: aiFoundryService.outputs.?systemAssignedMIPrincipalId ?? ''
      }
      // AI Search role assignments
      ...(azureAiSearchDeploy ? [
        {
          roleDefinitionIdOrName: 'Storage Blob Data Contributor'
          principalType: 'ServicePrincipal'
          principalId: aiSearchService.outputs.?systemAssignedMIPrincipalId ?? ''
        }
      ] : [])
      // Developer role assignments
      ...(!empty(principalId) ? [
        {
          roleDefinitionIdOrName: 'Storage Blob Data Contributor'
          principalType: principalIdType
          principalId: principalId
        }
        {
          roleDefinitionIdOrName: 'Storage Blob Data Reader'
          principalType: principalIdType
          principalId: principalId
        }
        {
          roleDefinitionIdOrName: 'Storage Account Contributor'
          principalType: principalIdType
          principalId: principalId
        }
      ] : [])
    ]
  }
}

// ---------- SAMPLE DATA STORAGE ACCOUNT ROLE ASSIGNMENTS (OPTIONAL) ----------
module sampleDataStorageAccountRoles './core/security/role_storageaccount.bicep' = if (deploySampleData) {
  name: 'sample-data-storage-account-role-assignments'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [resourceGroup]
  params: {
    azureStorageAccountName: sampleDataStorageAccountName
    roleAssignments: [
      // AI Foundry role assignments
      {
        roleDefinitionIdOrName: 'Storage Blob Data Contributor'
        principalType: 'ServicePrincipal'
        principalId: aiFoundryService.outputs.?systemAssignedMIPrincipalId ?? ''
      }
      // AI Search role assignments
      ...(azureAiSearchDeploy ? [
        {
          roleDefinitionIdOrName: 'Storage Blob Data Contributor'
          principalType: 'ServicePrincipal'
          principalId: aiSearchService.outputs.?systemAssignedMIPrincipalId ?? ''
        }
      ] : [])
      // Developer role assignments
      ...(!empty(principalId) ? [
        {
          roleDefinitionIdOrName: 'Storage Blob Data Contributor'
          principalType: principalIdType
          principalId: principalId
        }
        {
          roleDefinitionIdOrName: 'Storage Blob Data Reader'
          principalType: principalIdType
          principalId: principalId
        }
        {
          roleDefinitionIdOrName: 'Storage Account Contributor'
          principalType: principalIdType
          principalId: principalId
        }
      ] : [])
    ]
  }
}

// ---------- AI SEARCH (OPTIONAL) ----------
module aiSearchService 'br/public:avm/res/search/search-service:0.10.0' = if (azureAiSearchDeploy) {
  name: 'ai-search-service-deployment'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [resourceGroup]
  params: {
    name: aiSearchServiceName
    location: location
    sku: azureAiSearchSku
    replicaCount: azureAiSearchReplicaCount
    partitionCount: azureAiSearchPartitionCount
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
        subnetResourceId: virtualNetwork.outputs.subnetResourceIds[1] // AiServices Subnet
        tags: tags
      }
    ] : []
    publicNetworkAccess: azureNetworkIsolation ? 'Disabled' : 'Enabled'
    semanticSearch: 'standard'
    tags: tags
  }
}

// The Service Principal of the Azure Machine Learning service.
// This is used to assign the Reader role for AI Search and AI Services and used by the AI Foundry Hub
resource azureMachineLearningServicePrincipal 'Microsoft.Graph/servicePrincipals@v1.0' = {
  appId: '0736f41a-0425-4b46-bdb5-1563eff02385' // Azure Machine Learning service principal
}

// Role assignments (only when Search exists)
var aiSearchRoleAssignmentsArray = azureAiSearchDeploy ? [
  {
    roleDefinitionIdOrName: 'Search Index Data Contributor'
    principalType: 'ServicePrincipal'
    principalId: aiFoundryService.outputs.?systemAssignedMIPrincipalId
  }
  {
    roleDefinitionIdOrName: 'Search Index Data Reader'
    principalType: 'ServicePrincipal'
    principalId: aiFoundryService.outputs.?systemAssignedMIPrincipalId
  }
  {
    roleDefinitionIdOrName: 'Search Service Contributor'
    principalType: 'ServicePrincipal'
    principalId: aiFoundryService.outputs.?systemAssignedMIPrincipalId
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
  ...((aiFoundryHubDeploy) ? [
    {
      roleDefinitionIdOrName: 'Reader'
      principalType: 'ServicePrincipal'
      principalId: azureMachineLearningServicePrincipal.id
    }
  ] : [])
] : []

module aiSearchRoleAssignments './core/security/role_aisearch.bicep' = if (azureAiSearchDeploy) {
  name: 'ai-search-role-assignments'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [resourceGroup]
  params: {
    azureAiSearchName: aiSearchServiceName
    roleAssignments: aiSearchRoleAssignmentsArray
  }
}

// ---------- AI FOUNDRY/AI SERVICES ----------
// Deploy AI Foundry (Cognitive Services) resource with projects (Stage 2)
// Projects are deployed directly into the AI Services resource when not using Hub mode
// Prepare connections for the AI Foundry Account
var aiFoundryServiceConnections = concat(azureAiSearchDeploy ? [
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
    // Full aiSearchServiceName can't be used because may cause deployment name to be too long
    name: replace(aiSearchServiceName,'-','')
    target: aiSearchService.outputs.endpoint
    isSharedToAll: true
  }
] : [], (deploySampleData) ? [
  {
    // SampleDataStorageAccount connection
    category: 'AzureBlob'
    connectionProperties: {
      authType: 'AAD'
    }
    metadata: {
      Type: 'azure_storage_account'
      ApiType: 'Azure'
      ApiVersion: '2023-10-01'
      DeploymentApiVersion: '2023-10-01'
      Location: location
      ResourceId: sampleDataStorageAccount.outputs.resourceId
      AccountName: sampleDataStorageAccountName
      ContainerName: 'default'
    }
    name: replace(sampleDataStorageAccountName,'-','')
    target: sampleDataStorageAccount.outputs.primaryBlobEndpoint
    isSharedToAll: true
  }
] : [])

module aiFoundryService './cognitive-services/accounts/main.bicep' = {
  name: 'ai-foundry-service-deployment'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [resourceGroup]
  params: {
    name: aiFoundryServiceName
    kind: 'AIServices'
    location: location
    customSubDomainName: aiFoundryCustomSubDomainName
    disableLocalAuth: disableApiKeys
    allowProjectManagement: true // Even if a Hub is deployed we will still allow project management in the AI Services account
    diagnosticSettings: [
      {
        workspaceResourceId: logAnalyticsWorkspace.outputs.resourceId
      }
    ]
    managedIdentities: {
      systemAssigned: true
    }
    networkAcls: azureNetworkIsolation ? {
      defaultAction: 'Deny'
      ipRules: aiFoundryIpRules
      virtualNetworkRules: []
    } : {
      defaultAction: 'Allow'
      ipRules: []
      virtualNetworkRules: []
    }
    privateEndpoints: azureNetworkIsolation ? [
      {
        privateDnsZoneGroup: {
          privateDnsZoneGroupConfigs: [
            {
              privateDnsZoneResourceId: aiServicesPrivateDnsZone.outputs.resourceId
            }
            {
              privateDnsZoneResourceId: aiServicesOpenAiDnsZone.outputs.resourceId
            }
            {
              privateDnsZoneResourceId: aiServicesAiDnsZone.outputs.resourceId
            }
          ]
        }
        service: 'account'
        subnetResourceId: virtualNetwork.outputs.subnetResourceIds[1] // AiServices Subnet
      }
    ] : []
    restrictOutboundNetworkAccess: azureNetworkIsolation
    publicNetworkAccess: azureNetworkIsolation ? 'Disabled' : 'Enabled'
    sku: 'S0'
    deployments: deploySampleOpenAiModels ? openAiSampleModels : []
    connections: aiFoundryServiceConnections
    projects: aiFoundryServiceProjects
    tags: tags
  }
}

// Add role assignments for AI Services using the role_aiservice.bicep module
// This needs to be done after the AI Services account is created to avoid circular dependencies
// between the AI Services account and the AI Search service.
var aiFoundryRoleAssignmentsArray = [
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

module aiFoundryRoleAssignments './core/security/role_aifoundry.bicep' = {
  name: 'ai-foundry-role-assignments'
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [
    resourceGroup
    aiFoundryService
  ]
  params: {
    azureAiFoundryName: aiFoundryServiceName
    roleAssignments: aiFoundryRoleAssignmentsArray
  }
}

// ---------- AI FOUNDRY PROJECT ROLE ASSIGNMENTS TO AI SEARCH ----------
// Add any Search Index Reader and Search Service Contributor roles for each AI Foundry project
// to the AI Search Account. This ensures Agents created within a project can access indexes in
// the AI Search account.
@batchSize(1)
module aiFoundryProjectToAiSearchRoleAssignments './core/security/role_aisearch.bicep' = [
  for (project,index) in aiFoundryServiceProjects : if (aiFoundryProjectDeploy && azureAiSearchDeploy) {
    name: take('aifp-aisch-ra-${project.name}',64)
    scope: az.resourceGroup(effectiveResourceGroupName)
    params: {
      azureAiSearchName: aiSearchServiceName
      roleAssignments: [
        {
          roleDefinitionIdOrName: 'Search Index Data Reader'
          principalType: 'ServicePrincipal'
          principalId: aiFoundryService.outputs.projects[index].?systemAssignedMIPrincipalId ?? ''
        }
        {
          roleDefinitionIdOrName: 'Search Service Contributor'
          principalType: 'ServicePrincipal'
          principalId: aiFoundryService.outputs.projects[index].?systemAssignedMIPrincipalId ?? ''
        }
      ]
    }
  }
]

// ---------- AI FOUNDRY HUB (HUB DEPLOY ONLY) ----------
// Deploy AI Foundry Hub (Machine Learning workspace) with connections (Stage 3)
// Projects will be deployed separately as child resources when using Hub mode
// Prepare connections for the AI Foundry Hub
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
      ResourceId: aiFoundryService.outputs.resourceId
    }
    // Full aiFoundryServiceName can't be used because may cause deployment name to be too long
    name: replace(aiFoundryServiceName,'-','')
    target: aiFoundryService.outputs.endpoint
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
    // Full aiSearchServiceName can't be used because may cause deployment name to be too long
    name: replace(aiSearchServiceName,'-','')
    target: aiSearchService.outputs.endpoint
    isSharedToAll: true
  }
] : [])

module aiFoundryHub 'br/public:avm/res/machine-learning-services/workspace:0.12.1' = if (aiFoundryHubDeploy) {
  name: 'ai-foundry-hub-workspace-deployment'
  scope: az.resourceGroup(effectiveResourceGroupName)
  params: {
    name: aiFoundryHubName
    friendlyName: empty(aiFoundryHubFriendlyName) ? 'AI Foundry Hub (${environmentName})' : aiFoundryHubFriendlyName
    description: empty(aiFoundryHubDescription) ? 'AI Foundry Hub for ${environmentName}' : aiFoundryHubDescription
    location: location
    kind: 'Hub'
    sku: 'Basic'
    associatedApplicationInsightsResourceId: applicationInsights.outputs.resourceId
    associatedKeyVaultResourceId: aiFoundryHubDeploy ? keyVault.outputs.resourceId : null
    associatedStorageAccountResourceId: aiFoundryHubDeploy ? storageAccount.outputs.resourceId : null
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
    ipAllowlist: aiFoundryIpAllowList
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
        subnetResourceId: virtualNetwork.outputs.subnetResourceIds[1] // AiServices Subnet
        tags: tags
      }
    ] : []
    provisionNetworkNow: true
    roleAssignments: aiFoundryHubRoleAssignments
    systemDatastoresAuthMode: 'Identity'
    tags: tags
    workspaceHubConfig: {
      defaultWorkspaceResourceGroup: resourceGroup.outputs.resourceId
    }
  }
}

// ---------- AI FOUNDRY PROJECTS (HUB DEPLOY ONLY) ----------
// Deploy AI Foundry projects as separate Machine Learning workspace resources (Stage 3)
// These are only deployed when using Hub mode (aiFoundryHubDeploy && aiFoundryHubProjectDeploy)
module aiFoundryHubProjects 'br/public:avm/res/machine-learning-services/workspace:0.12.1' = [for project in aiFoundryHubProjectsList: if (aiFoundryHubDeploy && aiFoundryHubProjectDeploy) {
  name: take('aifp-${project.name}',64)
  scope: az.resourceGroup(effectiveResourceGroupName)
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
    hubResourceId: aiFoundryHubDeploy ? aiFoundryHub.outputs.resourceId : ''
    managedIdentities: {
      systemAssigned: true
    }
    publicNetworkAccess: azureNetworkIsolation ? 'Disabled' : 'Enabled'
    roleAssignments: project.roleAssignments ?? []
    tags: tags
  }
}]

// ---------- AI FOUNDRY PROJECTS ROLE ASSIGNMENTS TO AI SERVICES (HUB DEPLOY ONLY) ----------
// Add any Azure AI Developer role for each AI Foundry project to the AI Services account
// This ensures a developer with access to the AI Foundry project can also access the AI Services
@batchSize(1)
module aiFoundryHubProjectToAiServiceRoleAssignments './core/security/role_aifoundry.bicep' = [
  for (project,index) in aiFoundryHubProjectsList: if (aiFoundryHubDeploy && aiFoundryHubProjectDeploy) {
  name: take('aifhp-aisvc-ra-${project.name}',64)
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [
    aiFoundryHubProjects
  ]
  params: {
    azureAiFoundryName: aiFoundryServiceName
    roleAssignments: [
      {
        roleDefinitionIdOrName: '/providers/Microsoft.Authorization/roleDefinitions/64702f94-c441-49e6-a78b-ef80e0188fee' // 'Azure AI Developer'
        principalType: 'ServicePrincipal'
        principalId: aiFoundryHubProjects[index].outputs.?systemAssignedMIPrincipalId ?? ''
      }
    ]
  }
}]

// ---------- AI FOUNDRY PROJECT ROLE ASSIGNMENTS TO AI SEARCH (HUB DEPLOY ONLY) ----------
// Add any Search Index Reader and Search Service Contributor roles for each AI Foundry project
// to the AI Search Account. This ensures Agents created within a project can access indexes in
// the AI Search account.
@batchSize(1)
module aiFoundryHubProjectToAiSearchRoleAssignments './core/security/role_aisearch.bicep' = [
  for (project,index) in aiFoundryHubProjectsList : if (aiFoundryHubDeploy && aiFoundryHubProjectDeploy && azureAiSearchDeploy) {
    name: take('aifhp-aisch-ra-${project.name}',64)
    scope: az.resourceGroup(effectiveResourceGroupName)
    dependsOn: [
      aiFoundryHubProjects
    ]
    params: {
      azureAiSearchName: aiSearchServiceName
      roleAssignments: [
        {
          roleDefinitionIdOrName: 'Search Index Data Reader'
          principalType: 'ServicePrincipal'
          principalId: aiFoundryHubProjects[index].outputs.?systemAssignedMIPrincipalId ?? ''
        }
        {
          roleDefinitionIdOrName: 'Search Service Contributor'
          principalType: 'ServicePrincipal'
          principalId: aiFoundryHubProjects[index].outputs.?systemAssignedMIPrincipalId ?? ''
        }
      ]
    }
  }
]

// ---------- AI FOUNDRY PROJECTS DATASTORES (HUB DEPLOY ONLY) ----------
// One module instance per <project, container> when deploySampleData == true
module aiFoundryHubProjectSampleDataStores 'core/ai/ai-foundry-project-datastore.bicep' = [
  for idx in range(0, (projectCount * sampleDataContainerCount)) : if (aiFoundryHubDeploy && aiFoundryHubProjectDeploy && deploySampleData && aiFoundryProjectDeploy) {
    // Make the module deployment name unique
    name: replace(toLower(take('datastore_${aiFoundryHubProjectsList[idx / sampleDataContainerCount].name}_${sampleDataContainersArray[idx % sampleDataContainerCount]}',64)),'-','_')
    scope: az.resourceGroup(effectiveResourceGroupName)
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
  scope: az.resourceGroup(effectiveResourceGroupName)
  dependsOn: [resourceGroup]
  params: {
    name: bastionHostName
    location: location
    virtualNetworkResourceId: virtualNetwork.outputs.resourceId
    skuName: 'Developer'
    tags: tags
  }
}

output AZURE_RESOURCE_GROUP string = resourceGroup.outputs.name
output AZURE_PRINCIPAL_ID string = principalId
output AZURE_PRINCIPAL_ID_TYPE string = principalIdType
output AZURE_AI_FOUNDRY_HUB_DEPLOY bool = aiFoundryHubDeploy
output AZURE_AI_FOUNDRY_PROJECT_DEPLOY_TO_HUB bool = aiFoundryHubProjectDeploy

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

// Output the supporting resources (conditional for Hub mode)
output AZURE_STORAGE_ACCOUNT_NAME string = aiFoundryHubDeploy ? storageAccount.outputs.name : ''
output AZURE_STORAGE_ACCOUNT_RESOURCE_ID string = aiFoundryHubDeploy ? storageAccount.outputs.resourceId : ''
output AZURE_STORAGE_ACCOUNT_BLOB_ENDPOINT string = aiFoundryHubDeploy ? storageAccount.outputs.primaryBlobEndpoint : ''
output AZURE_STORAGE_ACCOUNT_PRIVATE_ENDPOINTS array = aiFoundryHubDeploy ? storageAccount.outputs.privateEndpoints : []
output AZURE_STORAGE_ACCOUNT_SERVICE_ENDPOINTS object = aiFoundryHubDeploy ? storageAccount.outputs.serviceEndpoints : {}
output AZURE_SAMPLE_DATA_STORAGE_ACCOUNT_NAME string = deploySampleData ? sampleDataStorageAccount.outputs.name : ''
output AZURE_SAMPLE_DATA_STORAGE_ACCOUNT_RESOURCE_ID string = deploySampleData ? sampleDataStorageAccount.outputs.resourceId : ''
output AZURE_SAMPLE_DATA_STORAGE_ACCOUNT_BLOB_ENDPOINT string = deploySampleData ? sampleDataStorageAccount.outputs.primaryBlobEndpoint : ''
output AZURE_KEY_VAULT_NAME string = aiFoundryHubDeploy ? keyVault.outputs.name : ''
output AZURE_KEY_VAULT_RESOURCE_ID string = aiFoundryHubDeploy ? keyVault.outputs.resourceId : ''
output AZURE_KEY_VAULT_ENDPOINT string = aiFoundryHubDeploy ? keyVault.outputs.uri : ''
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
output AZURE_AI_FOUNDRY_NAME string = aiFoundryService.outputs.name
output AZURE_AI_FOUNDRY_ID string = aiFoundryService.outputs.resourceId
output AZURE_AI_FOUNDRY_ENDPOINT string = aiFoundryService.outputs.endpoint
output AZURE_AI_FOUNDRY_RESOURCE_ID string = aiFoundryService.outputs.resourceId

// Output the Azure AI Foundry resources (conditional based on deployment mode)
output AZURE_AI_FOUNDRY_HUB_NAME string = aiFoundryHubDeploy ? aiFoundryHub.outputs.name : ''
output AZURE_AI_FOUNDRY_HUB_RESOURCE_ID string = aiFoundryHubDeploy ? aiFoundryHub.outputs.resourceId : ''
output AZURE_AI_FOUNDRY_HUB_PRIVATE_ENDPOINTS array = (aiFoundryHubDeploy && azureNetworkIsolation) ? aiFoundryHub.outputs.privateEndpoints : []

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
