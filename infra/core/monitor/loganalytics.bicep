metadata description = 'Creates a Log Analytics workspace.'

@description('Name of the Log Analytics workspace.')
param name string

@description('Location where the Log Analytics workspace should be deployed.')
param location string = resourceGroup().location

@description('Tags to apply to the Log Analytics workspace.')
param tags object = {}

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2021-12-01-preview' = {
  name: name
  location: location
  tags: tags
  properties: any({
    retentionInDays: 30
    features: {
      searchVersion: 1
    }
    sku: {
      name: 'PerGB2018'
    }
  })
}

output id string = logAnalytics.id
output name string = logAnalytics.name
