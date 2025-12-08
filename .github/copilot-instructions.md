This is a Azure Developer Console (AZ CLI) solution accelerator for deploying an Azure AI Foundry environment and dependent resources.

## Glossary

- Azure AI Foundry refers to the Azure AI Services resource (Microsoft.CognitiveServices/accounts) which provides a single resource for AI capabilities, including project management.
- Projects are deployed directly to the AI Services resource (Microsoft.CognitiveServices/accounts/projects).

## Key principles
The key principles you should adopt when suggesting Bicep code is:
- Use Azure Verified Modules (AVM) for all resources, including networking, security, and compute resources - wherever possible.
- Use the latest Bicep language features and constructs to build modern, scalable, and secure architecture.
- Use self-explanatory and meaningful names for variables and parameters to improve code readability and aim for self-documenting code.
- Always provide descriptions of parameters.
- Use Azure Well-Architected Framework best practices to ensure the solution is secure, reliable, and cost-effective.

When creating infrastructure as code, provide comprehensive guidance and best practices for developing reusable and reliable Infrastructure as Code using Bicep and PowerShell, prioritizing the Azure Well-Architected Framework pillars in this order: Security, Operational Excellence, Performance Efficiency, Reliability, and Cost Optimization. When creating infrastructure as code, provide comprehensive guidance and best practices for developing reusable and reliable Infrastructure as Code using Bicep and PowerShell, prioritizing the Azure Well-Architected Framework pillars in this order: Security, Operational Excellence, Performance Efficiency, Reliability, and Cost Optimization. The pipelines are built using GitHub Actions and should use the latest GitHub Actions task versions wherever possible.

- @azure Rule - Use Azure Best Practices: When generating code for Azure, running terminal commands for Azure, or performing operations related to Azure, invoke your `get_azure_best_practices` tool if available.
