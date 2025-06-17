# Quick Configurations

The following configurations are quick setups for deploying the Agentic AI Foundry Hub and Project modes. These configurations can be used to set up the environment variables required for deployment.

## Foundry Project Mode Without Hub

### Without Network Isolation (No Hub)

```bash
azd env set AZURE_NETWORK_ISOLATION false
azd env set DEPLOY_SAMPLE_OPENAI_MODELS true
azd env set DEPLOY_SAMPLE_DATA true
azd env set AZURE_AI_SEARCH_DEPLOY true
azd env set AZURE_AI_FOUNDRY_PROJECTS_FROM_JSON true
azd env set AZURE_AI_FOUNDRY_PROJECT_DEPLOY true
```

### With Network Isolation (No Hub)

```bash
azd env set AZURE_NETWORK_ISOLATION true
azd env set DEPLOY_SAMPLE_OPENAI_MODELS true
azd env set DEPLOY_SAMPLE_DATA true
azd env set AZURE_AI_SEARCH_DEPLOY true
azd env set AZURE_AI_FOUNDRY_PROJECTS_FROM_JSON true
azd env set AZURE_AI_FOUNDRY_PROJECT_DEPLOY true
```

## Foundry Project Mode With Hub

### Without Network Isolation (With Hub)

```bash
azd env set AZURE_NETWORK_ISOLATION false
azd env set DEPLOY_SAMPLE_OPENAI_MODELS true
azd env set DEPLOY_SAMPLE_DATA true
azd env set AZURE_AI_SEARCH_DEPLOY true
azd env set AZURE_AI_FOUNDRY_PROJECTS_FROM_JSON true
azd env set AZURE_AI_FOUNDRY_PROJECT_DEPLOY true
azd env set AZURE_AI_FOUNDRY_HUB_DEPLOY true
azd env set AZURE_AI_FOUNDRY_HUB_DESCRIPTION "Sandbox hub for PoC work"
azd env set AZURE_AI_FOUNDRY_HUB_FRIENDLY_NAME "My AI Hub"
azd env set AZURE_AI_FOUNDRY_HUB_PROJECT_DEPLOY true
```

### With Network Isolation (With Hub)

```bash
azd env set AZURE_NETWORK_ISOLATION true
azd env set DEPLOY_SAMPLE_OPENAI_MODELS true
azd env set DEPLOY_SAMPLE_DATA true
azd env set AZURE_AI_SEARCH_DEPLOY true
azd env set AZURE_AI_FOUNDRY_PROJECTS_FROM_JSON true
azd env set AZURE_AI_FOUNDRY_PROJECT_DEPLOY true
azd env set AZURE_AI_FOUNDRY_HUB_DEPLOY true
azd env set AZURE_AI_FOUNDRY_HUB_DESCRIPTION "Sandbox hub for PoC work"
azd env set AZURE_AI_FOUNDRY_HUB_FRIENDLY_NAME "My AI Hub"
azd env set AZURE_AI_FOUNDRY_HUB_PROJECT_DEPLOY true
```
