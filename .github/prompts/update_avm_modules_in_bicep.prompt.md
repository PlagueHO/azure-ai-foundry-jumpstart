---
mode: 'agent'
description: 'Update the Azure Verified Module to the latest version for the Bicep infrastructure as code file.'
tools: ['changes', 'codebase', 'editFiles', 'extensions', 'fetch', 'githubRepo', 'openSimpleBrowser', 'problems', 'runTasks', 'search', 'searchResults', 'terminalLastCommand', 'terminalSelection', 'testFailure', 'usages', 'vscodeAPI']
---

Your goal is to update the Bicep file `${file}` to use the latest available versions of Azure Verified Modules (AVM).
You will need to perform these steps:

1. Get a list of all the Azure Verified Modules that are used in the specific `${file}` Bicep file and get the module names and their current versions.
2. Step through each module referenced in the Bicep file and find the latest version of the module. Do this by using the `fetch` tool to get the tags list from Microsoft Container Registry. E.g. for 'br/public:avm/res/compute/virtual-machine' fetch [https://mcr.microsoft.com/v2/bicep/avm/res/compute/virtual-machine/tags/list](https://mcr.microsoft.com/v2/bicep/avm/res/compute/virtual-machine/tags/list) and find the latest version tag.
3. If there is a newer version of the module available based on the tags list from Microsoft Container Registry than is currently used in the Bicep, use the `fetch` tool to get the documentation for the module from the Azure Verified Modules index page. E.g., for `br/public:avm/res/compute/virtual-machine` the docs are [https://github.com/Azure/bicep-registry-modules/tree/main/avm/res/compute/virtual-machine](https://github.com/Azure/bicep-registry-modules/tree/main/avm/res/compute/virtual-machine)
4. Display a list of the modules with their current versions and the latest available versions, along with the documentation links for each module to the user.
5. Compare the documentation for the module to the current usage in the Bicep file and identify any changes that need to be made to the module parameters or usage.
> [!IMPORTANT]
> If the changes to the module parameters are not compatible with the current usage, are new changes that would change the behaviour, are related to security or compliance, then these changes must be reviewed and approved before being applied. So, PAUSE and ask for user input before proceeding.
6. Update the Azure Verified Module version and the resource in the Bicep file to use the latest available version and apply any relevant changes based on the documentation and including guidance from the user if required, to the module parameters.
7. If there are no changes to the module, leave it as is and make no other changes.
8. Display a table summary of the modules detected, their current versions and whether they were updated or not, and the documentation links for each module.

## IMPORTANT

- Ensure that the Bicep file is valid after the changes and that it adheres to the latest standards for Azure Verified Modules and there are no linting errors.
- Do not try to find the latest version of an Azure Verified Module by any other mechanism than fetching the tags list from Microsoft Container Registry.
- The tags list returned from Microsoft Container Registry is an array of JSON strings, so is not in version order. You will need to parse the tags and find the latest version based on the semantic versioning scheme.
