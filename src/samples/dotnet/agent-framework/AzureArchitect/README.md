# Prerequisites

Before you begin, ensure you have the following prerequisites:

- .NET 8.0 SDK or later
- Azure Foundry service endpoint and deployment configured
- Azure CLI installed and authenticated (for Azure credential authentication)

**Note**: This demo uses Azure CLI credentials for authentication. Make sure you're logged in with `az login` and have access to the Azure Foundry resource. For more information, see the [Azure CLI documentation](https://learn.microsoft.com/cli/azure/authenticate-azure-cli-interactively).

Set the following environment variables:

```powershell
$env:AZURE_OPENAI_ENDPOINT="https://aif-critical-thinking.openai.azure.com/"
$env:AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4-1"
$env:AZURE_FOUNDRY_PROJECT_ENDPOINT="https://aif-critical-thinking.services.ai.azure.com/api/projects/critical-thinking"
$env:AZURE_FOUNDRY_PROJECT_DEPLOYMENT_NAME="gpt-4-1-mini"
```
