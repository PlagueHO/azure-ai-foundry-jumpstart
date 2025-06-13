# Quick Configurations

The following configurations are quick setups for deploying the Agentic AI Foundry Hub and Project modes. These configurations can be used to set up the environment variables required for deployment.

## Hub-based Project Mode without Network Isolation

```bash
azd env set AZURE_AI_FOUNDRY_PROJECT_MODE Hub
azd env set AZURE_NETWORK_ISOLATION false
azd env set DEPLOY_SAMPLE_OPENAI_MODELS true
azd env set DEPLOY_SAMPLE_DATA true
azd env set AZURE_AI_SEARCH_DEPLOY true
azd env set AZURE_AI_FOUNDRY_HUB_DESCRIPTION "Agentic AI Hub"
azd env set AZURE_AI_FOUNDRY_HUB_FRIENDLY_NAME "Agentic AI Hub for evaluation and testing"
azd env set AZURE_AI_FOUNDRY_PROJECTS_FROM_JSON true
azd env set AZURE_AI_FOUNDRY_PROJECT_DEPLOY true
azd env set AZURE_AI_FOUNDRY_PROJECT_MODE Hub
```

## Hub-based Project Mode with Network Isolation

```bash
azd env set AZURE_AI_FOUNDRY_PROJECT_MODE Hub
azd env set AZURE_NETWORK_ISOLATION true
azd env set DEPLOY_SAMPLE_OPENAI_MODELS true
azd env set DEPLOY_SAMPLE_DATA true
azd env set AZURE_AI_SEARCH_DEPLOY true
azd env set AZURE_AI_FOUNDRY_HUB_DESCRIPTION "Agentic AI Hub"
azd env set AZURE_AI_FOUNDRY_HUB_FRIENDLY_NAME "Agentic AI Hub for evaluation and testing"
azd env set AZURE_AI_FOUNDRY_PROJECTS_FROM_JSON true
azd env set AZURE_AI_FOUNDRY_PROJECT_DEPLOY true
azd env set AZURE_AI_FOUNDRY_PROJECT_MODE Hub
```

## Foundry Project Mode without Network Isolation

```bash
azd env set AZURE_AI_FOUNDRY_PROJECT_MODE Foundry
azd env set AZURE_NETWORK_ISOLATION false
azd env set DEPLOY_SAMPLE_OPENAI_MODELS true
azd env set DEPLOY_SAMPLE_DATA true
azd env set AZURE_AI_SEARCH_DEPLOY true
azd env set AZURE_AI_FOUNDRY_PROJECTS_FROM_JSON true
azd env set AZURE_AI_FOUNDRY_PROJECT_DEPLOY true
azd env set AZURE_AI_FOUNDRY_PROJECT_MODE Hub
```

## Foundry Project Mode with Network Isolation

```bash
azd env set AZURE_AI_FOUNDRY_PROJECT_MODE Foundry
azd env set AZURE_NETWORK_ISOLATION true
azd env set DEPLOY_SAMPLE_OPENAI_MODELS true
azd env set DEPLOY_SAMPLE_DATA true
azd env set AZURE_AI_SEARCH_DEPLOY true
azd env set AZURE_AI_FOUNDRY_PROJECTS_FROM_JSON true
azd env set AZURE_AI_FOUNDRY_PROJECT_DEPLOY true
azd env set AZURE_AI_FOUNDRY_PROJECT_MODE Hub
```