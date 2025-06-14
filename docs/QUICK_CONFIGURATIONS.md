# Quick Configurations

The following configurations are quick setups for deploying the Agentic AI Foundry Hub and Project modes. These configurations can be used to set up the environment variables required for deployment.

## Without Network Isolation and Without Hub

```bash
azd env set AZURE_NETWORK_ISOLATION false
azd env set DEPLOY_SAMPLE_OPENAI_MODELS true
azd env set DEPLOY_SAMPLE_DATA true
azd env set AZURE_AI_SEARCH_DEPLOY true
azd env set AZURE_AI_FOUNDRY_PROJECTS_FROM_JSON true
azd env set AZURE_AI_FOUNDRY_PROJECT_DEPLOY true
```

## With Network Isolation and Without Hub

```bash
azd env set AZURE_NETWORK_ISOLATION true
azd env set DEPLOY_SAMPLE_OPENAI_MODELS true
azd env set DEPLOY_SAMPLE_DATA true
azd env set AZURE_AI_SEARCH_DEPLOY true
azd env set AZURE_AI_FOUNDRY_PROJECTS_FROM_JSON true
azd env set AZURE_AI_FOUNDRY_PROJECT_DEPLOY true
```

## Without Network Isolation but With Hub

```bash
azd env set AZURE_AI_FOUNDRY_PROJECT_MODE Foundry
azd env set AZURE_NETWORK_ISOLATION false
azd env set DEPLOY_SAMPLE_OPENAI_MODELS true
azd env set DEPLOY_SAMPLE_DATA true
azd env set AZURE_AI_SEARCH_DEPLOY true
aze env set AZURE_AI_FOUNDRY_HUB_DEPLOY true
azd env set AZURE_AI_FOUNDRY_HUB_DESCRIPTION "Sandbox hub for PoC work" # Only when AZURE_AI_FOUNDRY_PROJECT_MODE is set to Hub
azd env set AZURE_AI_FOUNDRY_HUB_FRIENDLY_NAME "My AI Hub" # Only when AZURE_AI_FOUNDRY_PROJECT_MODE is set to Hub
azd env set AZURE_AI_FOUNDRY_PROJECTS_FROM_JSON true
azd env set AZURE_AI_FOUNDRY_PROJECT_DEPLOY true
azd env set AZURE_AI_FOUNDRY_PROJECT_DEPLOY_TO_HUB true
```

## Foundry Project Mode with Network Isolation

```bash
azd env set AZURE_AI_FOUNDRY_PROJECT_MODE Foundry
azd env set AZURE_NETWORK_ISOLATION true
azd env set DEPLOY_SAMPLE_OPENAI_MODELS true
azd env set DEPLOY_SAMPLE_DATA true
azd env set AZURE_AI_SEARCH_DEPLOY true
aze env set AZURE_AI_FOUNDRY_HUB_DEPLOY true
azd env set AZURE_AI_FOUNDRY_HUB_DESCRIPTION "Sandbox hub for PoC work" # Only when AZURE_AI_FOUNDRY_PROJECT_MODE is set to Hub
azd env set AZURE_AI_FOUNDRY_HUB_FRIENDLY_NAME "My AI Hub" # Only when AZURE_AI_FOUNDRY_PROJECT_MODE is set to Hub
azd env set AZURE_AI_FOUNDRY_PROJECTS_FROM_JSON true
azd env set AZURE_AI_FOUNDRY_PROJECT_DEPLOY true
azd env set AZURE_AI_FOUNDRY_PROJECT_DEPLOY_TO_HUB true
```
