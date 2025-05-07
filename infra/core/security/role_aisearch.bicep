metadata description = 'Creates role assignments on an Azure AI Search service.'

// TODO: Once this proposal is implemented: https://github.com/azure/bicep/issues/2245
// We can create a generalized version of this resource that can be used any resource
// by passing in the resource as a parameter.

import { roleAssignmentType } from 'br/public:avm/utl/types/avm-common-types:0.5.1'
@sys.description('Optional. Array of role assignments to create.')
param roleAssignments roleAssignmentType[]?

@description('The name of the Azure AI Search service to set the role assignments on.')
param azureAiSearchName string

resource azureAiSearch 'Microsoft.Search/searchServices@2025-02-01-preview' existing = {
  name: azureAiSearchName
}

resource workspace_roleAssignments 'Microsoft.Authorization/roleAssignments@2022-04-01' = [
  for (roleAssignment, index) in (roleAssignments ?? []): {
    name: roleAssignment.?name ?? guid(azureAiSearch.id, roleAssignment.principalId, roleAssignment.roleDefinitionId)
    properties: {
      roleDefinitionId: roleAssignment.roleDefinitionId
      principalId: roleAssignment.principalId
      description: roleAssignment.?description
      principalType: roleAssignment.?principalType
      condition: roleAssignment.?condition
      conditionVersion: !empty(roleAssignment.?condition) ? (roleAssignment.?conditionVersion ?? '2.0') : null // Must only be set if condtion is set
      delegatedManagedIdentityResourceId: roleAssignment.?delegatedManagedIdentityResourceId
    }
    scope: azureAiSearch
  }
]
