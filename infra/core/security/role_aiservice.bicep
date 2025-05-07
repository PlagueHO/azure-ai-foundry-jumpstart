metadata description = 'Creates role assignments on an Azure AI Services account.'

// TODO: Once this proposal is implemented: https://github.com/azure/bicep/issues/2245
// We can create a generalized version of this resource that can be used any resource
// by passing in the resource as a parameter.

import { roleAssignmentType } from 'br/public:avm/utl/types/avm-common-types:0.5.1'
@sys.description('Optional. Array of role assignments to create.')
param roleAssignments roleAssignmentType[]?

@description('The name of the Azure AI Services account to set the role assignments on.')
param azureAiServiceName string

resource azureAiServiceAccount 'Microsoft.CognitiveServices/accounts@2025-04-01-preview' existing = {
  name: azureAiServiceName
}

resource workspace_roleAssignments 'Microsoft.Authorization/roleAssignments@2022-04-01' = [
  for (roleAssignment, index) in (roleAssignments ?? []): {
    name: roleAssignment.?name ?? guid(azureAiServiceAccount.id, roleAssignment.principalId, roleAssignment.roleDefinitionId)
    properties: {
      roleDefinitionId: roleAssignment.roleDefinitionId
      principalId: roleAssignment.principalId
      description: roleAssignment.?description
      principalType: roleAssignment.?principalType
      condition: roleAssignment.?condition
      conditionVersion: !empty(roleAssignment.?condition) ? (roleAssignment.?conditionVersion ?? '2.0') : null // Must only be set if condtion is set
      delegatedManagedIdentityResourceId: roleAssignment.?delegatedManagedIdentityResourceId
    }
    scope: azureAiServiceAccount
  }
]
