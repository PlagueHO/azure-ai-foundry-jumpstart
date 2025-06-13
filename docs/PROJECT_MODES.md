# Azure AI Foundry Project Modes

This repository has been refactored to support two different Azure AI Foundry project modes:

## Foundry Based-Project - Recommended Architecture

**Resource Type**: `Microsoft.CognitiveServices/accounts` with `allowProjectManagement: true`

**Dependencies**:

- Azure Application Insights (for monitoring)
- Azure AI Search (optional)
- No Azure Storage Account or Key Vault required

**Projects**: Deployed as `Microsoft.CognitiveServices/accounts/projects` (child resources of the AI Services account).

**Connections**: Both `Microsoft.CognitiveServices/accounts` and `Microsoft.CognitiveServices/accounts/projects` can connect to other resources using the connection child resource type `Microsoft.CognitiveServices/accounts/connections` or `Microsoft.CognitiveServices/accounts/projects/connections`.

**Use Case**:

- AI application development focused on Foundry capabilities
- Simpler deployment with fewer dependencies
- Cost-optimized scenarios
- When you don't need the full ML workspace overhead

## Hub Based-Project - Traditional Architecture

**Resource Type**: `Microsoft.MachineLearningServices/workspaces` with `kind: 'Hub'`

**Dependencies**:

- Azure Storage Account (required for ML workspace)
- Azure Key Vault (required for ML workspace)
- Azure Application Insights (required for ML workspace)
- Azure Container Registry (optional)
- Azure AI Search (optional)
- Azure AI Services

**Projects**: Deployed as `Microsoft.MachineLearningServices/workspaces` with `kind: 'Project'` that reference the hub via `hubResourceId`.

**Use Case**:

- Traditional ML/AI workloads
- Scenarios requiring full ML workspace capabilities
- When you need data lineage and experiment tracking
- Multi-project environments with shared compute and storage


## Configuration

Set the project mode using the `aiFoundryProjectMode` parameter:

```bicep
param aiFoundryProjectMode string = 'Hub' // or 'Project'
```

Or via environment variable:

```bash
export AZURE_AI_FOUNDRY_PROJECT_MODE=Project
```

## Key Differences

| Aspect | Hub Mode | Project Mode |
|--------|----------|--------------|
| **Resource Count** | Higher (Hub + Storage + Key Vault) | Lower (AI Services account only) |
| **Cost** | Higher due to additional resources | Lower, pay only for what you use |
| **Complexity** | More complex setup | Simpler deployment |
| **Features** | Full ML workspace capabilities | AI Foundry focused features |
| **Projects** | ML workspace projects | CognitiveServices projects |
| **Dependency Management** | Hub manages shared resources | Projects are more independent |

## Migration Considerations

- **Hub to Project**: Projects need to be recreated as they are different resource types
- **Project to Hub**: Requires deploying hub infrastructure and migrating project configurations
- Both modes support the same AI capabilities (Azure OpenAI, AI Search connections, etc.)

## Backward Compatibility

The refactored template defaults to `Hub` mode to ensure backward compatibility with existing deployments.
