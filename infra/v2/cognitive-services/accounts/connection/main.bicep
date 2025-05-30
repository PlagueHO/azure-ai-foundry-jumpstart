metadata name = 'Machine Learning Services Workspaces Connections'
metadata description = 'This module creates a connection in a Machine Learning Services workspace.'

// ================ //
// Parameters       //
// ================ //

@description('Required. Name of the connection to create.')
param name string

@description('Required. The name of the parent Cognitive Services account. Required if the template is used in a standalone deployment.')
param accountName string

@description('Required. Category of the connection.')
param category categoryType

@description('Optional. The expiry time of the connection.')
param expiryTime string?

@description('Optional. Indicates whether the connection is shared to all users in the workspace.')
param isSharedToAll bool?

@description('Optional. User metadata for the connection.')
param metadata metadataType = {}

@description('Optional. The shared user list of the connection.')
param sharedUserList string[]?

@description('Required. The target of the connection.')
param target string

@description('Optional. Value details of the workspace connection.')
param value string?

@description('Required. The properties of the connection, specific to the auth type.')
param connectionProperties connectionPropertyType

// ============================= //
// Existing resources references //
// ============================= //

resource cognitiveServicesAccount 'Microsoft.CognitiveServices/accounts@2025-04-01-preview' existing = {
  name: accountName
}

// ============== //
// Resources      //
// ============== //

resource connection 'Microsoft.CognitiveServices/accounts/connections@2025-04-01-preview' = {
  name: name
  parent: cognitiveServicesAccount
  properties: union(
    {
      category: category
      expiryTime: expiryTime
      isSharedToAll: isSharedToAll
      metadata: metadata
      sharedUserList: sharedUserList
      target: target
      value: value
    },
    connectionProperties
  )
}

// ============ //
// Outputs      //
// ============ //

@description('The resource ID of the connection.')
output resourceId string = connection.id

@description('The name of the connection.')
output name string = connection.name

@description('The name of the resource group the connection was created in.')
output resourceGroupName string = resourceGroup().name

// ================ //
// Definitions      //
// ================ //

@description('The tpe for the metadata.')
type metadataType = {
  @description('Required. The metadata key-value pairs.')
  *: string
}

@export()
@description('The type of the connection category.')
type categoryType =
  | 'ADLSGen2'
  | 'AIServices'
  | 'AmazonMws'
  | 'AmazonRdsForOracle'
  | 'AmazonRdsForSqlServer'
  | 'AmazonRedshift'
  | 'AmazonS3Compatible'
  | 'ApiKey'
  | 'AzureBlob'
  | 'AzureDataExplorer'
  | 'AzureDatabricksDeltaLake'
  | 'AzureMariaDb'
  | 'AzureMySqlDb'
  | 'AzureOneLake'
  | 'AzureOpenAI'
  | 'AzurePostgresDb'
  | 'AzureSqlDb'
  | 'AzureSqlMi'
  | 'AzureSynapseAnalytics'
  | 'AzureTableStorage'
  | 'BingLLMSearch'
  | 'Cassandra'
  | 'CognitiveSearch'
  | 'CognitiveService'
  | 'Concur'
  | 'ContainerRegistry'
  | 'CosmosDb'
  | 'CosmosDbMongoDbApi'
  | 'Couchbase'
  | 'CustomKeys'
  | 'Db2'
  | 'Drill'
  | 'Dynamics'
  | 'DynamicsAx'
  | 'DynamicsCrm'
  | 'Elasticsearch'
  | 'Eloqua'
  | 'FileServer'
  | 'FtpServer'
  | 'GenericContainerRegistry'
  | 'GenericHttp'
  | 'GenericRest'
  | 'Git'
  | 'GoogleAdWords'
  | 'GoogleBigQuery'
  | 'GoogleCloudStorage'
  | 'Greenplum'
  | 'Hbase'
  | 'Hdfs'
  | 'Hive'
  | 'Hubspot'
  | 'Impala'
  | 'Informix'
  | 'Jira'
  | 'Magento'
  | 'ManagedOnlineEndpoint'
  | 'MariaDb'
  | 'Marketo'
  | 'MicrosoftAccess'
  | 'MongoDbAtlas'
  | 'MongoDbV2'
  | 'MySql'
  | 'Netezza'
  | 'ODataRest'
  | 'Odbc'
  | 'Office365'
  | 'OpenAI'
  | 'Oracle'
  | 'OracleCloudStorage'
  | 'OracleServiceCloud'
  | 'PayPal'
  | 'Phoenix'
  | 'Pinecone'
  | 'PostgreSql'
  | 'Presto'
  | 'PythonFeed'
  | 'QuickBooks'
  | 'Redis'
  | 'Responsys'
  | 'S3'
  | 'Salesforce'
  | 'SalesforceMarketingCloud'
  | 'SalesforceServiceCloud'
  | 'SapBw'
  | 'SapCloudForCustomer'
  | 'SapEcc'
  | 'SapHana'
  | 'SapOpenHub'
  | 'SapTable'
  | 'Serp'
  | 'Serverless'
  | 'ServiceNow'
  | 'Sftp'
  | 'SharePointOnlineList'
  | 'Shopify'
  | 'Snowflake'
  | 'Spark'
  | 'SqlServer'
  | 'Square'
  | 'Sybase'
  | 'Teradata'
  | 'Vertica'
  | 'WebTable'
  | 'Xero'
  | 'Zoho'

@description('The connection properties when the auth type is AAD.')
type aadAuthTypeWorkspaceConnectionPropertyType = {
  @description('Required. The authentication type of the connection target.')
  authType: 'AAD'
}

@description('The connection properties when the auth type is AccessKey.')
type accessKeyAuthTypeWorkspaceConnectionPropertyType = {
  @description('Required. The authentication type of the connection target.')
  authType: 'AccessKey'

  @description('Required. The credentials for the connection.')
  credentials: workspaceConnectionAccessKeyType
}

@description('The connection properties when the auth type is AccountKey.')
type accountKeyAuthTypeWorkspaceConnectionPropertyType = {
  @description('Required. The authentication type of the connection target.')
  authType: 'AccountKey'

  @description('Required. The credentials for the connection.')
  credentials: workspaceConnectionAccountKeyType
}

@description('The connection properties when the auth type is ApiKey.')
type apiKeyAuthWorkspaceConnectionPropertyType = {
  @description('Required. The authentication type of the connection target.')
  authType: 'ApiKey'

  @description('Required. The credentials for the connection.')
  credentials: workspaceConnectionApiKeyType
}

@description('The connection properties when the auth type are CustomKeys.')
type customKeysWorkspaceConnectionPropertyType = {
  @description('Required. The authentication type of the connection target.')
  authType: 'CustomKeys'

  @description('Required. The credentials for the connection.')
  credentials: customKeysType
}

@description('The connection properties when the auth type is ManagedIdentity.')
type managedIdentityAuthTypeWorkspaceConnectionPropertyType = {
  @description('Required. The authentication type of the connection target.')
  authType: 'ManagedIdentity'

  @description('Required. The credentials for the connection.')
  credentials: workspaceConnectionManagedIdentityType
}

@description('The connection properties when the auth type is None.')
type noneAuthTypeWorkspaceConnectionPropertyType = {
  @description('Required. The authentication type of the connection target.')
  authType: 'None'
}

@description('The connection properties when the auth type is OAuth2.')
type oauth2AuthTypeWorkspaceConnectionPropertyType = {
  @description('Required. The authentication type of the connection target.')
  authType: 'OAuth2'

  @description('Required. The credentials for the connection.')
  credentials: workspaceConnectionOAuth2Type
}

@description('The connection properties when the auth type is PAT.')
type patAuthTypeWorkspaceConnectionPropertyType = {
  @description('Required. The authentication type of the connection target.')
  authType: 'PAT'

  @description('Required. The credentials for the connection.')
  credentials: workspaceConnectionPersonalAccessTokenType
}

@description('The connection properties when the auth type is SAS.')
type sasAuthTypeWorkspaceConnectionPropertyType = {
  @description('Required. The authentication type of the connection target.')
  authType: 'SAS'

  @description('Required. The credentials for the connection.')
  credentials: workspaceConnectionSharedAccessSignatureType
}

@description('The connection properties when the auth type is ServicePrincipal.')
type servicePrincipalAuthTypeWorkspaceConnectionPropertyType = {
  @description('Required. The authentication type of the connection target.')
  authType: 'ServicePrincipal'

  @description('Required. The credentials for the connection.')
  credentials: workspaceConnectionServicePrincipalType
}

@description('The connection properties when the auth type is UsernamePassword.')
type usernamePasswordAuthTypeWorkspaceConnectionPropertyType = {
  @description('Required. The authentication type of the connection target.')
  authType: 'UsernamePassword'

  @description('Required. The credentials for the connection.')
  credentials: workspaceConnectionUsernamePasswordType
}

@description('The type fot the custom keys.')
type customKeysType = {
  @description('Required. The custom keys for the connection.')
  keys: {
    @description('Required. Key-value pairs for the custom keys.')
    *: string
  }
}

@description('The type for the workspace connection access key.')
type workspaceConnectionAccessKeyType = {
  @description('Required. The connection access key ID.')
  accessKeyId: string

  @description('Required. The connection secret access key.')
  secretAccessKey: string
}

@description('The type for the workspace connection account key.')
type workspaceConnectionAccountKeyType = {
  @description('Required. The connection key.')
  key: string
}

@description('The type for the workspace connection API key.')
type workspaceConnectionApiKeyType = {
  @description('Required. The connection API key.')
  key: string
}

@description('The type for the workspace connection managed identity.')
type workspaceConnectionManagedIdentityType = {
  @description('Required. The connection managed identity ID.')
  clientId: string

  @description('Required. The connection managed identity resource ID.')
  resourceId: string
}

type workspaceConnectionOAuth2Type = {
  @description('Conditional. The connection auth URL. Required if connection category is Concur.')
  authUrl: string?

  @minLength(36)
  @maxLength(36)
  @description('Required. The connection client ID in the format of UUID.')
  clientId: string

  @description('Required. The connection client secret.')
  clientSecret: string

  @description('Conditional. The connection developer token. Required if connection category is GoogleAdWords.')
  developerToken: string?

  @description('Conditional. The connection password. Required if connection category is Concur or ServiceNow where AccessToken grant type is \'Password\'.')
  password: string?

  @description('Conditional. The connection refresh token. Required if connection category is GoogleBigQuery, GoogleAdWords, Hubspot, QuickBooks, Square, Xero or Zoho.')
  refreshToken: string?

  @description('Conditional. The connection tenant ID. Required if connection category is QuickBooks or Xero.')
  tenantId: string?

  @description('Conditional. The connection username. Required if connection category is Concur or ServiceNow where AccessToken grant type is \'Password\'.')
  username: string?
}

@description('The type for the workspace connection personal access token.')
type workspaceConnectionPersonalAccessTokenType = {
  @description('Required. The connection personal access token.')
  pat: string
}

@description('The type for the workspace connection shared access signature.')
type workspaceConnectionSharedAccessSignatureType = {
  @description('Required. The connection SAS token.')
  sas: string
}

@description('The type for the workspace connection service principal.')
type workspaceConnectionServicePrincipalType = {
  @description('Required. The connection client ID.')
  clientId: string

  @description('Required. The connection client secret.')
  clientSecret: string

  @description('Required. The connection tenant ID.')
  tenantId: string
}

@description('The type for the workspace connection username and password.')
type workspaceConnectionUsernamePasswordType = {
  @description('Required. The connection password.')
  password: string

  @description('Conditional. The connection security token. Required if connection is like SalesForce for extra security in addition to \'UsernamePassword\'.')
  securityToken: string?

  @description('Required. The connection username.')
  username: string
}

@secure()
@export()
@description('The type of the connection properties.')
@discriminator('authType')
type connectionPropertyType =
  | aadAuthTypeWorkspaceConnectionPropertyType
  | accessKeyAuthTypeWorkspaceConnectionPropertyType
  | accountKeyAuthTypeWorkspaceConnectionPropertyType
  | apiKeyAuthWorkspaceConnectionPropertyType
  | customKeysWorkspaceConnectionPropertyType
  | managedIdentityAuthTypeWorkspaceConnectionPropertyType
  | noneAuthTypeWorkspaceConnectionPropertyType
  | oauth2AuthTypeWorkspaceConnectionPropertyType
  | patAuthTypeWorkspaceConnectionPropertyType
  | sasAuthTypeWorkspaceConnectionPropertyType
  | servicePrincipalAuthTypeWorkspaceConnectionPropertyType
  | usernamePasswordAuthTypeWorkspaceConnectionPropertyType


@export()
@sys.description('The type for the workspace connection.')
type connectionType = {
  @sys.description('Required. Name of the connection to create.')
  name: string

  @sys.description('Required. Category of the connection.')
  category: categoryType

  @sys.description('Optional. The expiry time of the connection.')
  expiryTime: string?

  @sys.description('Optional. Indicates whether the connection is shared to all users in the workspace.')
  isSharedToAll: bool?

  @sys.description('Optional. User metadata for the connection.')
  metadata: {
    @sys.description('Required. The metadata key-value pairs.')
    *: string
  }?

  @sys.description('Optional. The shared user list of the connection.')
  sharedUserList: string[]?

  @sys.description('Required. The target of the connection.')
  target: string

  @sys.description('Optional. Value details of the workspace connection.')
  value: string?

  @sys.description('Required. The properties of the connection, specific to the auth type.')
  connectionProperties: connectionPropertyType
}
