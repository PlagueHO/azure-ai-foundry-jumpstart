metadata description = 'Creates an Application Insights instance based on an existing Log Analytics workspace.'

@description('Name of the Application Insights instance.')
param name string

@description('Location where the Application Insights instance should be deployed.')
param location string = resourceGroup().location

@description('Tags to apply to the Application Insights instance.')
param tags object = {}

@description('The ID of the existing Log Analytics workspace to link with Application Insights.')
param logAnalyticsWorkspaceId string

resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: name
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalyticsWorkspaceId
  }
}

output connectionString string = applicationInsights.properties.ConnectionString
output id string = applicationInsights.id
output instrumentationKey string = applicationInsights.properties.InstrumentationKey
output name string = applicationInsights.name
