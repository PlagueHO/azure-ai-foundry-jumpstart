# Azure AI Foundry Deployment Modes

This repository supports flexible Azure AI Foundry deployment architectures with the Azure AI Services resource always being deployed with project management capabilities, and an optional Hub that can be deployed alongside it.

## Core Architecture

- **Azure AI Foundry**: Always deployed as `Microsoft.CognitiveServices/accounts` with `allowProjectManagement: true`, providing the foundation for all AI capabilities including Azure OpenAI, Azure AI Search connections, and project management. Used to be referred to as Azure AI Services.
- **Azure AI Foundry Hub**: Optionally deployed as `Microsoft.MachineLearningServices/workspaces` with `kind: 'Hub'` when enhanced ML workspace capabilities are needed. This is not recommended for new deployments, but can be used for existing scenarios that require it.
- **Project Deployment**: Projects can be deployed either to the AI Services resource or to the Hub, depending on configuration.

## Deployment Modes

### AI Foundry/AI Services Only (Default)

**Configuration**:

```bicep
param aiFoundryHubDeploy = false
param aiFoundryHubProjectDeploy = false  // Not relevant when Hub is not deployed
```

**Resources Deployed**:

- Azure AI Services (`Microsoft.CognitiveServices/accounts`) with `allowProjectManagement: true`
- Azure Application Insights (for monitoring)
- Azure AI Search (optional)
- Projects deployed as `Microsoft.CognitiveServices/accounts/projects` (child resources of AI Services)

**Use Case**:

- AI application development focused on Foundry capabilities
- Simpler deployment with fewer dependencies
- Cost-optimized scenarios
- When you don't need full ML workspace capabilities

### AI Foundry/AI Services + AI Foundry Hub with Hub-based Projects

**Configuration**:

```bicep
param aiFoundryHubDeploy = true
param aiFoundryHubProjectDeploy = true
```

**Resources Deployed**:

- Azure AI Services (`Microsoft.CognitiveServices/accounts`) with `allowProjectManagement: true`
- Azure AI Foundry Hub (`Microsoft.MachineLearningServices/workspaces`)
- Azure Storage Account (required for Hub)
- Azure Key Vault (required for Hub)
- Azure Container Registry (optional)
- Azure Application Insights
- Azure AI Search (optional)
- Projects deployed as `Microsoft.MachineLearningServices/workspaces` with `kind: 'Project'` connected to the Hub

**Use Case**:

- Traditional ML/AI workloads requiring full workspace capabilities
- Scenarios needing data lineage and experiment tracking
- Multi-project environments with shared compute and storage
- When you need both AI Services capabilities and ML workspace features

### AI Foundry/AI Services + AI Foundry Hub with AI Services Projects

**Configuration**:

```bicep
param aiFoundryHubDeploy = true
param aiFoundryHubProjectDeploy = false
```

**Resources Deployed**:

- Azure AI Services (`Microsoft.CognitiveServices/accounts`) with `allowProjectManagement: true`
- Azure AI Foundry Hub (`Microsoft.MachineLearningServices/workspaces`)
- All Hub supporting resources (Storage, Key Vault, etc.)
- Azure Application Insights
- Azure AI Search (optional)
- Projects deployed as `Microsoft.CognitiveServices/accounts/projects` (child resources of AI Services)

**Use Case**:

- Hybrid scenarios where you need Hub capabilities for some workloads
- Transitioning from Hub-based to AI Services-based project management
- When you want Hub features available but prefer simpler project management

## Configuration

Control the deployment mode using these parameters:

```bicep
param aiFoundryHubDeploy bool = false              // Deploy the Hub and supporting resources
param aiFoundryHubProjectDeploy bool = false       // Deploy projects to Hub (vs AI Services)
```

Or via environment variables:

```bash
export AZURE_AI_FOUNDRY_HUB_DEPLOY=true
export AZURE_AI_FOUNDRY_HUB_PROJECT_DEPLOY=false
```

## Resource Connections

The AI Services resource is always connected to:

- Azure AI Search (when deployed)
- Azure Storage Account (when Hub is deployed)
- Sample data storage account (when sample data is deployed)

The Hub (when deployed) is connected to:

- Azure AI Services resource
- Azure AI Search (when deployed)
- Azure Storage Account (always when Hub is deployed)
- Sample data storage account (when sample data is deployed)

## Key Architectural Principles

| Aspect | AI Services Always | Hub Optional | Projects Flexible |
|--------|-------------------|-------------|-------------------|
| **AI Services** | Always deployed with project support | N/A | Can host projects when Hub projects disabled |
| **Hub Resources** | Not required | Only when `aiFoundryHubDeploy=true` | Can host projects when Hub projects enabled |
| **Cost Model** | Base cost for AI capabilities | Additional cost for ML workspace features | Projects can be deployed to most cost-effective location |
| **Complexity** | Simple, focused on AI | Complex, full ML workspace | Flexible based on deployment choice |
| **Capabilities** | Azure OpenAI, AI Search, basic project management | Full ML workspace + AI capabilities | Varies based on deployment target |

## Migration Considerations

**Adding Hub to AI Services-only deployment**:

- Set `aiFoundryHubDeploy=true` to add Hub and supporting resources
- Existing AI Services projects remain functional
- New projects can be deployed to Hub by setting `aiFoundryHubProjectDeploy=true`

**Removing Hub from deployment**:

- Hub-based projects need to be migrated to AI Services projects (different resource types)
- Set `aiFoundryHubDeploy=false` to remove Hub and supporting resources
- AI Services resource continues to function independently

**Moving projects between AI Services and Hub**:

- Projects are different resource types and cannot be moved directly
- Requires recreation of projects in the target location
- Both deployment targets support the same AI capabilities (Azure OpenAI, AI Search connections, etc.)

## Backward Compatibility

The template defaults to AI Services-only deployment (`aiFoundryHubDeploy=false`) for:

- Simpler default experience
- Lower cost for getting started
- Reduced complexity for basic AI scenarios

Existing deployments using Hub mode can continue by setting `aiFoundryHubDeploy=true`.
