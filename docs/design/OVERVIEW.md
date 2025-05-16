# Azure AI Foundry Jumpstart Solution Accelerator – Overview

The Azure AI Foundry Jumpstart Solution Accelerator provides a secure, well-architected, and automated way to deploy an Azure AI Foundry environment and its supporting resources. It is designed to help organizations quickly explore and experiment with Azure AI Foundry capabilities while adhering to Microsoft’s Zero Trust security model and Azure Well-Architected Framework best practices.

## Key Features

- **Zero-Trust Security**: Deploys resources into a virtual network with private endpoints, disables public access, and enforces managed identities for secure service-to-service authentication.
- **Azure Verified Modules**: Uses AVM Bicep modules for all supported resources, ensuring reliability and compliance.
- **Flexible Network Isolation**: Supports both network-isolated (private) and public endpoint deployments.
- **Managed Identities**: Eliminates the need for API keys by leveraging Azure-managed identities and optional Entra ID-only authentication.
- **Comprehensive Logging**: Configures diagnostic settings for all resources, sending logs to Log Analytics for monitoring and compliance.
- **Optional Bastion Host**: Enables secure RDP/SSH access via Azure Bastion when required.
- **Extensible Model and Data Deployment**: Optionally deploys sample OpenAI models and uploads sample data to accelerate onboarding.
- **Customizable Resource Attachments**: Supports attaching existing Azure Container Registries and configuring Azure AI Search service deployment.
- **Role-Based Access Control**: Grants access to specified users or service principals.

## Configurable Capabilities

Deployment behavior can be tailored using environment variables, including:

- **Sample Data and Model Deployment**: Toggle deployment of sample OpenAI models and sample data containers.
- **Network Isolation**: Enable or disable VNet isolation and configure IP allow lists.
- **API Key Management**: Optionally disable API keys for Azure AI services.
- **Resource Sizing and Selection**: Choose SKUs for Azure AI Search and control deployment of optional infrastructure like Bastion and Container Registry.
- **Access Control**: Specify principal IDs and types for hub access.
- **Security Enhancements**: Enable Key Vault purge protection.

For a full list of configuration options, see [CONFIGURATION_OPTIONS.md](../CONFIGURATION_OPTIONS.md).

---
This accelerator is ideal for secure, rapid prototyping and evaluation of Azure AI Foundry in enterprise environments.
