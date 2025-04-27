metadata description = 'Creates an Application Insights instance and a Log Analytics workspace.'

@description('Name of the Log Analytics workspace.')
param logAnalyticsName string

@description('Name of the Application Insights instance.')
param applicationInsightsName string

@description('Location where the resources should be deployed.')
param location string = resourceGroup().location

@description('Tags to apply to the resources.')
param tags object = {}

module logAnalytics 'loganalytics.bicep' = {
  name: 'loganalytics'
  params: {
    name: logAnalyticsName
    location: location
    tags: tags
  }
}

module applicationInsights 'applicationinsights.bicep' = {
  name: 'applicationinsights'
  params: {
    name: applicationInsightsName
    location: location
    tags: tags
    logAnalyticsWorkspaceId: logAnalytics.outputs.id
  }
}

@description('The connection string of the Application Insights instance.')
output applicationInsightsConnectionString string = applicationInsights.outputs.connectionString

@description('The resource ID of the Application Insights instance.')
output applicationInsightsId string = applicationInsights.outputs.id

@description('The instrumentation key of the Application Insights instance.')
output applicationInsightsInstrumentationKey string = applicationInsights.outputs.instrumentationKey

@description('The name of the Application Insights instance.')
output applicationInsightsName string = applicationInsights.outputs.name

@description('The resource ID of the Log Analytics workspace.')
output logAnalyticsWorkspaceId string = logAnalytics.outputs.id

@description('The name of the Log Analytics workspace.')
output logAnalyticsWorkspaceName string = logAnalytics.outputs.name
