metadata name = 'Tnterface type Azure AI Foundry Project'
metadata description = '''
This module provides a type definition for an Azure AI Foundry Project.
'''

import { roleAssignmentType } from 'br/public:avm/utl/types/avm-common-types:0.5.1'

@sys.export()
@sys.description('Defines the properties for an Azure AI Foundry Project workspace.')
type aiFoundryProjectType = {
  @sys.description('The unique name of the Foundry Project workspace.')
  name: string

  @sys.description('The friendly display name for the Foundry Project workspace.')
  friendlyName: string

  @sys.description('A description for the Foundry Project workspace.')
  description: string

  @sys.description('Array of public IPv4 addresses or CIDR ranges to allow access to the workspace.')
  ipAllowlist: string[]?

  @sys.description('Role assignments to apply to the workspace.')
  roleAssignments: roleAssignmentType[]?
}
