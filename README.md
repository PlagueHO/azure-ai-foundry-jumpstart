# Azure AI Foundry Jumpstart Solution Accelerator

[![CI][ci-shield]][ci-url]
[![CD][cd-shield]][cd-url]
[![License][license-shield]][license-url]
[![Azure][azure-shield]][azure-url]
[![IaC][iac-shield]][iac-url]

## Introduction

The Azure AI Foundry Jumpstart Solution Accelerator deploys an [Azure AI Foundry environment](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/create-secure-ai-hub) and supporting services into your Azure subscription. This accelerator is designed to be used as a secure an for exploring and experimenting with Azure AI Foundry capabilities.

This solution accelerator is intended to help getting started with Azure AI Foundry quickly and easily, while meeting security and well-architected framework best practices.

### Zero-trust

By default, this soltion accelerator deploys Azure AI Foundry and most of the supporting resources into a virtual network using private endpoints, disables public access and uses managed identities for services to authenticate to each other.

It automates the deployment of the services using the same approach as the instructions on [How to create a secure Azure AI Foundry hub and project with a managed virtual network](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/secure-data-playground) page.

> Note: Zero-trust is the default configuration. But you can choose to deploy the resources without a virtual network and public endpoints if you prefer. See the [Deployment Options](#deployment-options) section for more details.

## Prerequisites

Before you begin, ensure you have the following prerequisites in place:

- An active Azure subscription - [Create a free account](https://azure.microsoft.com/free/) if you don't have one.

## Deploy to Azure

You can deploy this solution accelerator using either the Azure Developer CLI or the Deploy to Azure button below.

### Deployment Options

You can deploy the application using one of the following options:

- [1. Azure Developer CLI](#1-azure-developer-cli)
- [2. Azure Portal Deployment](#2-azure-portal-deployment)

### 1. Azure Developer CLI

> [!IMPORTANT]
> This section will create Azure resources and deploy the solution from your local environment using the Azure Developer CLI. You do not need to clone this repo to complete these steps.

1. Download the [Azure Developer CLI](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/overview)
1. If you have not cloned this repo, run `azd init -t PlagueHO/azure-ai-foundry-jumpstart`. If you have cloned this repo, just run 'azd init' from the repo root directory.
1. Authenticate the Azure Developer CLI  by running `azd auth login`.

   ```powershell
   azd auth login
   ```

1. Run `azd up` to provision and deploy the application

   ```powershell
   azd init -t PlagueHO/azure-ai-foundry-jumpstart
   azd up
   ```

### 2. Azure Portal Deployment

> [!WARNING]
> This button will only create Azure resources. It will not populate any sample data.

Click on the Deploy to Azure button to deploy the Azure resources for this solution accelerator.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FPlagueHO%2Fazure-ai-foundry-jumpstart%2Fmain%2Finfra%2Fmain.bicepparam)

## Configuration Options

The complete list of environment variables can be found in the [Configuration Options](docs/CONFIGURATION_OPTIONS.md) document.

<!-- Badge reference links -->
[ci-shield]: https://img.shields.io/github/actions/workflow/status/PlagueHO/azure-ai-foundry-jumpstart/continuous-integration.yml?branch=main&label=CI
[ci-url]: https://github.com/PlagueHO/azure-ai-foundry-jumpstart/actions/workflows/continuous-integration.yml

[cd-shield]: https://img.shields.io/github/actions/workflow/status/PlagueHO/azure-ai-foundry-jumpstart/continuous-delivery.yml?branch=main&label=CD
[cd-url]: https://github.com/PlagueHO/azure-ai-foundry-jumpstart/actions/workflows/continuous-delivery.yml

[license-shield]: https://img.shields.io/github/license/PlagueHO/azure-ai-foundry-jumpstart
[license-url]: https://github.com/PlagueHO/azure-ai-foundry-jumpstart/blob/main/LICENSE

[azure-shield]: https://img.shields.io/badge/Azure-Solution%20Accelerator-0078D4?logo=microsoftazure&logoColor=white
[azure-url]: https://azure.microsoft.com/

[iac-shield]: https://img.shields.io/badge/Infrastructure%20as%20Code-Bicep-5C2D91?logo=azurepipelines&logoColor=white
[iac-url]: https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/overview
