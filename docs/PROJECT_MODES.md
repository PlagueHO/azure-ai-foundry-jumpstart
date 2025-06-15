# Azure AI Foundry Project Modes

This repository supports flexible Azure AI Foundry project architectures with the Azure AI Foundry resource always being deployed with project management capabilities, and an optional Hub that can be deployed alongside it.

> [!IMPORTANT]
> The Azure AI Foundry resource is the new name for Azure AI Services. It will be referenced as such throughout this documentation. It is a resource `Microsoft.CognitiveServices/accounts` with `allowProjectManagement: true`.

## Core Architecture

- **Azure AI Foundry**: Always deployed as `Microsoft.CognitiveServices/accounts` with `allowProjectManagement: true`, providing the foundation for all AI capabilities including Azure OpenAI, Azure AI Search connections, and project management. Used to be referred to as Azure AI Services.
- **Azure AI Foundry Hub**: Optionally deployed as `Microsoft.MachineLearningServices/workspaces` with `kind: 'Hub'` when enhanced ML workspace capabilities are needed. This is not recommended for new deployments, but can be used for existing scenarios that require it.
- **Project Deployment**: Projects can be deployed either to the AI Foundry resource, to the Hub or both, depending on configuration.

> [!NOTE]
> Azure AI Foundry resource is the new name for Azure AI Services. It can be deployed, with our without project capabilities. The Hub is an optional component that provides additional features that are provided by the Azure Machine Learning workspace, such as data asset management, pipelines, and experiment tracking. The Hub is not required for basic AI Foundry capabilities, but can be useful for more complex ML workflows. It is recommended to use the AI Foundry resource for new deployments, as it provides a simpler solution with fewer dependencies.

## Deployment Modes

### AI Foundry Only (Default)

This is the simplest deployment mode, focusing on AI capabilities without the additional complexity of a Hub.

**Configuration**:

```bash
azd env set AZURE_AI_FOUNDRY_HUB_DEPLOY false # This is te default
# AZURE_AI_FOUNDRY_HUB_PROJECT_DEPLOY is not relevant when Hub is not deployed
```

**Resources Deployed**:

- Azure AI Services (`Microsoft.CognitiveServices/accounts`) with `allowProjectManagement: true`
- Azure AI Search (optional)
- Projects deployed as `Microsoft.CognitiveServices/accounts/projects` (child resources of AI Services)

**Use Case**:

- AI application development focused on Foundry capabilities
- Simpler deployment with fewer dependencies
- Cost-optimized scenarios
- When you don't need full ML workspace capabilities

### AI Foundry and AI Foundry Hub with Hub-based Projects

**Configuration**:

```bash
azd env set AZURE_AI_FOUNDRY_HUB_DEPLOY true
azd env set AZURE_AI_FOUNDRY_HUB_PROJECT_DEPLOY true
```

**Resources Deployed**:

- Azure AI Services (`Microsoft.CognitiveServices/accounts`) with `allowProjectManagement: true`
- Azure AI Foundry Hub (`Microsoft.MachineLearningServices/workspaces`)
- Azure Storage Account (required for Hub)
- Azure Key Vault (required for Hub)
- Azure Container Registry (used with hub, optional)
- Azure AI Search (optional)
- Projects deployed as `Microsoft.MachineLearningServices/workspaces` with `kind: 'Project'` connected to the Hub

**Use Case**:

- Traditional ML/AI workloads requiring full workspace capabilities
- Scenarios needing data lineage and experiment tracking
- Multi-project environments with shared compute and storage
- When you need both AI Services capabilities and ML workspace features

### AI Foundry and AI Foundry Hub with AI Services Projects

**Configuration**:

```bash
azd env set AZURE_AI_FOUNDRY_HUB_DEPLOY true
azd env set AZURE_AI_FOUNDRY_HUB_PROJECT_DEPLOY false
```

**Resources Deployed**:

- Azure AI Services (`Microsoft.CognitiveServices/accounts`) with `allowProjectManagement: true`
- Azure AI Foundry Hub (`Microsoft.MachineLearningServices/workspaces`)
- Azure Storage Account (required for Hub)
- Azure Key Vault (required for Hub)
- Azure Container Registry (used with hub, optional)
- Azure AI Search (optional)
- Projects deployed as `Microsoft.CognitiveServices/accounts/projects` (child resources of AI Services)

**Use Case**:

- Hybrid scenarios where you need Hub capabilities for some workloads
- Transitioning from Hub-based to AI Services-based project management
- When you want Hub features available but prefer simpler project management

## Configuration

Control the deployment mode using these environment variables:

```bash
azd env set AZURE_AI_FOUNDRY_HUB_DEPLOY false          # Deploy the Hub and supporting resources
azd env set AZURE_AI_FOUNDRY_HUB_PROJECT_DEPLOY false  # Deploy projects to Hub (vs AI Foundry Services)
```

Or alternatively using these parameters directly in the bicep template:

```bicep
param aiFoundryHubDeploy bool = false         // Deploy the Hub and supporting resources
param aiFoundryHubProjectDeploy bool = false  // Deploy projects to Hub (vs AI Foundry Services)
```

## Resource Connections

The AI Foundry resource is always connected to:

- Azure AI Search (when deployed)
- Azure Storage Account (when Hub is deployed)
- Sample data storage account (when sample data is deployed)

The Azure AI Foundry Hub (when deployed) is connected to:

- Azure AI Foundry resource
- Azure AI Search (when deployed)
- Azure Storage Account (always when Hub is deployed)
- Sample data storage account (when sample data is deployed)

## Migration Considerations

**Adding Hub to AI Services-only deployment**:

- Set `azd env set AZURE_AI_FOUNDRY_HUB_DEPLOY true` to add Hub and supporting resources
- Existing AI Services projects remain functional
- Sample projects can be deployed to Hub by setting `azd env set AZURE_AI_FOUNDRY_HUB_PROJECT_DEPLOY true`

**Removing Hub from deployment**:

- Hub-based projects need to be migrated to AI Services projects (different resource types)
- Set `azd env set AZURE_AI_FOUNDRY_HUB_DEPLOY false` to remove Hub and supporting resources
- AI Services resource continues to function independently

**Moving projects between AI Services and Hub**:

- Projects are different resource types and cannot be moved directly
- Requires recreation of projects in the target location
- Both deployment targets support the same AI capabilities (Azure OpenAI, AI Search connections, etc.)

## Backward Compatibility

The template defaults to Azure AI Foundry only deployment (`azd env set AZURE_AI_FOUNDRY_HUB_DEPLOY false`) for a simplified experience. It is also the recommended mode for new deployments. Existing deployments using an Azure AI Foundry Hub can continue by setting `azd env set AZURE_AI_FOUNDRY_HUB_DEPLOY true`.
