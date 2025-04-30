# Azure AI Foundry Secure Hub Solution Accelerator

[![CI][ci-shield]][ci-url]
[![CD][cd-shield]][cd-url]
[![License][license-shield]][license-url]
[![Azure][azure-shield]][azure-url]
[![IaC][iac-shield]][iac-url]

The Azure AI Foundry Secure Hub Solution Accelerator deploys a [network isolated Azure AI Foundry environment](https://le    arn.microsoft.com/en-us/azure/ai-foundry/how-to/create-secure-ai-hub) and supporting services into your Azure subscription. This accelerator is designed to be used as a secure an for exploring and experimenting with Azure AI Foundry capabilities.

This was created to get started with Azure AI Foundry quickly and easily, while meeting security and well-architected framework best practices.

This Secure Hub isn't a special version of Azure AI Foundry but rather is a quick and simple way to get Azure AI Foundry up and running in a virtual network using private endpoints, no public access and managed identities for services to authenticate to each other. It autlomates the deployment of the services using the same approach as the instructions on [How to create a secure Azure AI Foundry hub and project with a managed virtual network](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/secure-data-playground) page.

## Prerequisites

Before you begin, ensure you have the following prerequisites in place:

- An active Azure subscription - [Create a free account](https://azure.microsoft.com/free/) if you don't have one.
- The Azure Developer CLI (azd) installed on your machine - [Install azd](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd).

## Next Steps

### Step 1: Add application code

1. Initialize the service source code projects anywhere under the current directory. Ensure that all source code projects can be built successfully.
    - > Note: For `function` services, it is recommended to initialize the project using the provided [quickstart tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-get-started).
2. Once all service source code projects are building correctly, update `azure.yaml` to reference the source code projects.
3. Run `azd package` to validate that all service source code projects can be built and packaged locally.

### Step 2: Provision Azure resources

Update or add Bicep files to provision the relevant Azure resources. This can be done incrementally, as the list of [Azure resources](https://learn.microsoft.com/en-us/azure/?product=popular) are explored and added.

- A reference library that contains all of the Bicep modules used by the azd templates can be found [here](https://github.com/Azure-Samples/todo-nodejs-mongo/tree/main/infra/core).
- All Azure resources available in Bicep format can be found [here](https://learn.microsoft.com/en-us/azure/templates/).

Run `azd provision` whenever you want to ensure that changes made are applied correctly and work as expected.

### Step 3: Tie in application and infrastructure

Certain changes to Bicep files or deployment manifests are required to tie in application and infrastructure together. For example:

1. Set up [application settings](#application-settings) for the code running in Azure to connect to other Azure resources.
1. If you are accessing sensitive resources in Azure, set up [managed identities](#managed-identities) to allow the code running in Azure to securely access the resources.
1. If you have secrets, it is recommended to store secrets in [Azure Key Vault](#azure-key-vault) that then can be retrieved by your application, with the use of managed identities.
1. Configure [host configuration](#host-configuration) on your hosting platform to match your application's needs. This may include networking options, security options, or more advanced configuration that helps you take full advantage of Azure capabilities.

For more details, see [additional details](#additional-details) below.

When changes are made, use azd to validate and apply your changes in Azure, to ensure that they are working as expected:

- Run `azd up` to validate both infrastructure and application code changes.
- Run `azd deploy` to validate application code changes only.

### Step 4: Up to Azure

Finally, run `azd up` to run the end-to-end infrastructure provisioning (`azd provision`) and deployment (`azd deploy`) flow. Visit the service endpoints listed to see your application up-and-running!

## Additional Details

The following section examines different concepts that help tie in application and infrastructure.

### Application settings

It is recommended to have application settings managed in Azure, separating configuration from code. Typically, the service host allows for application settings to be defined.

- For `appservice` and `function`, application settings should be defined on the Bicep resource for the targeted host. Reference template example [here](https://github.com/Azure-Samples/todo-nodejs-mongo/tree/main/infra).
- For `aks`, application settings are applied using deployment manifests under the `<service>/manifests` folder. Reference template example [here](https://github.com/Azure-Samples/todo-nodejs-mongo-aks/tree/main/src/api/manifests).

### Managed identities

[Managed identities](https://learn.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/overview) allows you to secure communication between services. This is done without having the need for you to manage any credentials.

### Azure Key Vault

[Azure Key Vault](https://learn.microsoft.com/en-us/azure/key-vault/general/overview) allows you to store secrets securely. Your application can access these secrets securely through the use of managed identities.

### Host configuration

For `appservice`, the following host configuration options are often modified:

- Language runtime version
- Exposed port from the running container (if running a web service)
- Allowed origins for CORS (Cross-Origin Resource Sharing) protection (if running a web service backend with a frontend)
- The run command that starts up your service

<!-- Badge reference links -->
[ci-shield]: https://img.shields.io/github/actions/workflow/status/PlagueHO/azure-ai-foundry-secure-hub/continuous-integration.yml?branch=main
[ci-url]: https://github.com/PlagueHO/azure-ai-foundry-secure-hub/actions/workflows/continuous-integration.yml

[cd-shield]: https://img.shields.io/github/actions/workflow/status/PlagueHO/azure-ai-foundry-secure-hub/continuous-deployment.yml?branch=main
[cd-url]: https://github.com/PlagueHO/azure-ai-foundry-secure-hub/actions/workflows/continuous-deployment.yml

[license-shield]: https://img.shields.io/github/license/PlagueHO/azure-ai-foundry-secure-hub
[license-url]: https://github.com/PlagueHO/azure-ai-foundry-secure-hub/blob/main/LICENSE

[azure-shield]: https://img.shields.io/badge/Azure-Solution%20Accelerator-0078D4?logo=microsoftazure&logoColor=white
[azure-url]: https://azure.microsoft.com/

[iac-shield]: https://img.shields.io/badge/Infrastructure%20as%20Code-Bicep-5C2D91?logo=azurepipelines&logoColor=white
[iac-url]: https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/overview
