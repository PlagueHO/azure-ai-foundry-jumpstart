---
title: Infrastructure Deployment using Bicep and Azure Verified Modules
version: 1.0  
date_created: 2025-06-07  
owner: Platform Engineering Team
tags: [infrastructure, bicep, avm, azure, deployment]
---

## Introduction

This specification defines the requirements, constraints, and interfaces for deploying infrastructure using Bicep and Azure Verified Modules (AVM). It is optimized to be deployed by Azure Developer CLI.

## 1. Purpose & Scope

The purpose of this specification is to standardize infrastructure deployment for the solution using Bicep and AVM. It covers the structure, requirements, and validation criteria for the main Bicep file (`main.bicep`) and its parameter file (`main.bicepparam`). The intended audience includes platform engineers, DevOps, and AI agents generating or validating IaC for Azure environments. It is intended to be deployed using the Azure Developer CLI, ensuring a consistent and secure deployment process.

## 2. Definitions

- **Bicep**: A domain-specific language (DSL) for deploying Azure resources declaratively.
- **AZD (Azure Developer CLI)**: A command-line interface for deploying Azure resources using Bicep and other tools.
- **AVM (Azure Verified Modules)**: Pre-built, Microsoft-verified Bicep modules for common Azure resources, available at https://aka.ms/avm.
- **IaC**: Infrastructure as Code.
- **Parameter File**: A `.bicepparam` file providing input values for Bicep deployments.

## 3. Requirements, Constraints & Guidelines

- **REQ-001**: All core Azure resources must be deployed using AVM modules where available.
- **REQ-002**: The `main.bicep` file must follow the structure and modularity pattern of the [Azure AI Foundry Jumpstart main.bicep](https://github.com/PlagueHO/azure-ai-foundry-jumpstart/blob/main/infra/main.bicep).
- **REQ-003**: A `main.bicepparam` file must exist in the same directory as `main.bicep` and provide all required parameters for deployment.
- **REQ-004**: Must comply with requirements for being deployed via Azure  
  Developer CLI, including parameterization and secure handling of secrets.
- **REQ-005**: The `main.bicepparam` file must read all parameter values from  
  environment variables using `readEnvironmentVariable()` function with Azure  
  Developer CLI naming conventions (uppercase with underscore separators) and  
  provide appropriate default values.
- **SEC-001**: All secrets and sensitive values must be passed as secure  
  parameters and never hardcoded.
- **SEC-002**: Role-based access control (RBAC) and network security rules must be defined using AVM modules where possible.
- **CON-001**: Only Microsoft-verified AVM modules from https://aka.ms/avm may be used for core resources.
- **GUD-001**: Use parameterization and outputs to maximize reusability and composability.
- **PAT-001**: Follow the folder and file naming conventions: `infra/main.bicep`, `infra/main.bicepparam`, and `infra/modules/` for custom modules if needed.

## 4. Interfaces & Data Contracts

- **main.bicep**: Accepts parameters for location, resource group, naming, and secrets. Imports AVM modules for resources such as resource groups, networks, compute, databases, and monitoring.
- **main.bicepparam**: Provides values for all required parameters in `main.bicep`.

Example parameter block in `main.bicep`:

```bicep
param location string
param resourceGroupName string
param sqlAdminPassword secureString
```

Example AVM module usage:

```bicep
module rg 'br/public:azurerm:resource-group:2.0.0' = {
  name: 'resourceGroup'
  params: {
    name: resourceGroupName
    location: location
  }
}
```

Example parameter file with environment variable usage:

```bicep
using './main.bicep'

param environmentName = readEnvironmentVariable('AZURE_ENV_NAME', 'azdtemp')
param location = readEnvironmentVariable('AZURE_LOCATION', 'EastUS2')
param resourceGroupName = readEnvironmentVariable('AZURE_RESOURCE_GROUP', '')
```

## 5. Rationale & Context

Using AVM modules ensures security, compliance, and maintainability by leveraging Microsoft-verified best practices. Standardizing the structure and naming conventions improves onboarding and automation for both humans and AI agents.

## 6. Examples & Edge Cases

````bicep
// Example: Securely passing a password
param sqlAdminPassword secureString

// Example: Using AVM for a SQL Server
module sql 'br/public:azurerm:mssql-server:2.0.0' = {
  name: 'sqlServer'
  params: {
    name: 'my-sql-server'
    location: location
    administratorLoginPassword: sqlAdminPassword
  }
}
````

## 7. Validation Criteria

- All core resources are deployed using AVM modules.
- No secrets are hardcoded in any Bicep file.
- The `main.bicepparam` file exists and is valid.
- All parameters in `main.bicepparam` use `readEnvironmentVariable()` with  
  Azure Developer CLI naming conventions (UPPERCASE_WITH_UNDERSCORES).
- The structure matches the referenced pattern.
- All parameters required by AVM modules are provided.

## 8. Related Specifications / Further Reading

- [Azure Verified Modules](https://aka.ms/avm)
- [Bicep Documentation](https://learn.microsoft.com/azure/azure-resource-manager/bicep/)
- [Azure AI Foundry Jumpstart main.bicep](https://github.com/PlagueHO/azure-ai-foundry-jumpstart/blob/main/infra/v1/main.bicep)
