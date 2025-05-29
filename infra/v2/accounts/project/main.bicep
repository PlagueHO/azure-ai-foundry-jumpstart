metadata name = 'Interface type Azure AI Foundry Project'
metadata description = '''
This module provides a type definition for an Azure AI Foundry Project.
'''

@sys.export()
@sys.description('Defines the properties for an Azure AI Foundry Project.')
type aiFoundryProjectType = {
  @sys.description('The unique name of the Foundry Project. This corresponds to the "name" property of the Microsoft.CognitiveServices/accounts/projects resource.')
  name: string

  @sys.description('The geo-location where the resource lives. This corresponds to the "location" property of the Microsoft.CognitiveServices/accounts/projects resource.')
  location: string

  @sys.description('Properties of Foundry Project project. This corresponds to the "properties" object of the Microsoft.CognitiveServices/accounts/projects resource.')
  properties: aiFoundryProjectPropertiesType

  @sys.description('Identity for the resource. This corresponds to the "identity" property of the Microsoft.CognitiveServices/accounts/projects resource.')
  identity: {
    @sys.description('The identity type.')
    type: ('None' | 'SystemAssigned' | 'UserAssigned' | 'SystemAssigned, UserAssigned')

    @sys.description('The list of user assigned identities associated with the resource. The user identity dictionary key references will be ARM resource ids.')
    userAssignedIdentities: object?
  }?

  @sys.description('Resource tags. This corresponds to the "tags" property of the Microsoft.CognitiveServices/accounts/projects resource.')
  tags: object?
}

@sys.description('Defines the nested properties for an Azure AI Foundry Project, corresponding to the "properties" object of the Microsoft.CognitiveServices/accounts/projects resource.')
type aiFoundryProjectPropertiesType = {
  @sys.description('The friendly display name for the Foundry Project. This corresponds to the "displayName" property within the "properties" of the Microsoft.CognitiveServices/accounts/projects resource.')
  displayName: string

  @sys.description('A description for the Foundry Project. This corresponds to the "description" property within the "properties" of the Microsoft.CognitiveServices/accounts/projects resource.')
  description: string
}
