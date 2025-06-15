---
mode: 'agent'
description: 'Update the Azure Verified Module to the latest version for the Bicep infrastructure as code file.'
tools: ['changes', 'codebase', 'editFiles', 'extensions', 'fetch', 'githubRepo', 'openSimpleBrowser', 'problems', 'runTasks', 'search', 'searchResults', 'terminalLastCommand', 'terminalSelection', 'testFailure', 'usages', 'vscodeAPI', 'github', 'filesystem', 'playwright']
---
Your goal is to update the Bicep file `${file}` to use the latest available versions of Azure Verified Modules (AVM).
You will need to perform these steps:
1. Get a list of all the Azure Verified Modules that are used in the specific `${file}` Bicep file and get the module names and their current versions.
2. Step through each module referenced in the Bicep file and find the latest version of the module. Do this by fetching the tags list from Microsoft Container Registry. E.g. for 'br/public:avm/res/compute/virtual-machine' fetch [https://mcr.microsoft.com/v2/bicep/avm/res/compute/virtual-machine/tags/list](https://mcr.microsoft.com/v2/bicep/avm/res/compute/virtual-machine/tags/list) and find the latest version tag. The latest version is the highest number in the list of tags.
3. If there is a newer version of the module available based on the tags list from Microsoft Container Registry than is currently used in the Bicep, fetch the documentation for the module from the Azure Verified Modules index page. E.g., for `br/public:avm/res/compute/virtual-machine` the docs are [https://github.com/Azure/bicep-registry-modules/tree/main/avm/res/compute/virtual-machine](https://github.com/Azure/bicep-registry-modules/tree/main/avm/res/compute/virtual-machine)
4. Update the Azure Verified Module in the Bicep file to use the latest available version and apply any relevant changes to the module parameters based on the documentation.
5. If there are no changes to the module, leave it as is.

Ensure that the Bicep file is valid after the changes and that it adheres to the latest standards for Azure Verified Modules and there are no linting errors.
Do not try to find the latest version of an Azure Verified Module by any other mechanism than fetching the tags list from Microsoft Container Registry.
