# Quick Configurations

The following configurations are quick setups for deploying Azure AI Foundry with project support. These configurations can be used to set up the environment variables required for deployment.

## Without Network Isolation

```bash
azd env set AZURE_NETWORK_ISOLATION false
azd env set DEPLOY_SAMPLE_OPENAI_MODELS true
azd env set DEPLOY_SAMPLE_DATA true
azd env set AZURE_AI_SEARCH_DEPLOY true
azd env set AZURE_AI_FOUNDRY_PROJECTS_FROM_JSON true
azd env set AZURE_AI_FOUNDRY_PROJECT_DEPLOY true
```

## With Network Isolation

```bash
azd env set AZURE_NETWORK_ISOLATION true
azd env set DEPLOY_SAMPLE_OPENAI_MODELS true
azd env set DEPLOY_SAMPLE_DATA true
azd env set AZURE_AI_SEARCH_DEPLOY true
azd env set AZURE_AI_FOUNDRY_PROJECTS_FROM_JSON true
azd env set AZURE_AI_FOUNDRY_PROJECT_DEPLOY true
```
