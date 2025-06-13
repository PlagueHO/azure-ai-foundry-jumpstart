---
mode: 'agent'
description: 'Update the Azure Verified Module to the latest version for the Bicep infrastructure as code file.'
tools: ['changes', 'codebase', 'editFiles', 'extensions', 'fetch', 'findTestFiles', 'githubRepo', 'new', 'openSimpleBrowser', 'problems', 'runCommands', 'runNotebooks', 'runTasks', 'search', 'searchResults', 'terminalLastCommand', 'terminalSelection', 'testFailure', 'usages', 'vscodeAPI', 'filesystem', 'create_directory', 'directory_tree', 'edit_file', 'get_file_info', 'list_allowed_directories', 'list_directory', 'read_file', 'read_multiple_files', 'search_files', 'write_file', 'move_file']
---
Your goal is to update the each Azure Verified Module version in the `${file}` Bicep to use the latest version of the Azure Verified Module listed on #fetch https://azure.github.io/Azure-Verified-Modules/indexes/bicep/bicep-resource-modules/. The module version is in the `Modules & Versions` column and the module name is in the `Module Name` column.
You will need to perform these steps:
1. Get a list of all the Azure Verified Modules that are used in the specific `${file}` Bicep file and get the module names and their current versions.
2. Step through each module name and version and find them on the Azure Verified Modules index https://azure.github.io/Azure-Verified-Modules/indexes/bicep/bicep-resource-modules/
3. If there is a newer version of the module available, retrieve the link to the documentation for the module from the index page https://azure.github.io/Azure-Verified-Modules/indexes/bicep/bicep-resource-modules/.
> [!IMPORTANT]
> The documentation for each AVM module is in the Github repo for AVM: https://github.com/Azure/bicep-registry-modules/tree/main/avm/res/. For example: https://github.com/Azure/bicep-registry-modules/tree/main/avm/res/api-management/service
4. Update the Azure Verified Module in the Bicep file to use the latest available version and apply any relevant changes to the module para
5. If there are no changes to the module, leave it as is.

Ensure that the Bicep file is valid after the changes and that it adheres to the latest standards for Azure Verified Modules and there are no linting errors.
