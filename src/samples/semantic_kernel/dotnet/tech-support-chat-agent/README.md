# Tech Support Chat Agent - Semantic Kernel Sample

A .NET 8 console application demonstrating a tech support chat agent using the Semantic Kernel Agent Framework with Azure AI Agent type and Azure AI Foundry Agent Service.

## Overview

This sample showcases:

- Interactive console-based chat interface for tech support scenarios
- Implementation using Semantic Kernel Agent Framework with Azure AI Agent type
- Azure AI Foundry Agent Service providing complete agent functionality and RAG capabilities
- Agent Templates for structured conversation patterns
- Built-in RAG (Retrieval-Augmented Generation) capabilities through Azure AI Foundry Agent Service
- Tech support knowledge base integration via Azure AI Foundry's managed vector stores and file search
- Conversation state management via Agent Framework's built-in capabilities
- Escalation and handoff workflows using Agent orchestration

## Prerequisites

- .NET 8.0 SDK
- Azure subscription with Azure AI Foundry access
- Azure AI Foundry project with configured:
  - AI model deployment (e.g., GPT-4)
  - Vector store for knowledge base
  - Knowledge base files uploaded and indexed

## Configuration

1. **Copy and configure settings:**

   ```bash
   cp appsettings.json appsettings.local.json
   ```

2. **Update `appsettings.local.json` with your Azure AI Foundry details:**

   ```json
   {
     "AzureAI": {
       "FoundryEndpoint": "https://your-foundry-project.eastus.inference.ml.azure.com",
       "ProjectName": "your-project-name",
       "ModelName": "gpt-4o",
       "TenantId": "your-tenant-id",
       "ClientId": "your-client-id"
     },
     "AgentFramework": {
       "VectorStoreId": "your-vector-store-id",
       "KnowledgeBaseFiles": [
         "your-kb-file-1-id",
         "your-kb-file-2-id"
       ]
     }
   }
   ```

3. **Or use environment variables:**

   ```bash
   export AzureAI__FoundryEndpoint="https://your-foundry-project.eastus.inference.ml.azure.com"
   export AzureAI__ModelName="gpt-4o"
   export AgentFramework__VectorStoreId="your-vector-store-id"
   ```

4. **Or use User Secrets (recommended for development):**

   ```bash
   dotnet user-secrets set "AzureAI:FoundryEndpoint" "https://your-foundry-project.eastus.inference.ml.azure.com"
   dotnet user-secrets set "AzureAI:ModelName" "gpt-4o"
   dotnet user-secrets set "AgentFramework:VectorStoreId" "your-vector-store-id"
   ```

## Building and Running

1. **Restore dependencies:**

   ```bash
   dotnet restore
   ```

2. **Build the project:**

   ```bash
   dotnet build
   ```

3. **Validate configuration:**

   ```bash
   dotnet run -- validate
   ```

4. **Set up the agent (placeholder for future implementation):**

   ```bash
   dotnet run -- setup
   ```

5. **Start interactive chat:**

   ```bash
   dotnet run -- chat
   ```

   Or simply:

   ```bash
   dotnet run
   ```

## Usage

### Interactive Chat Commands

- **General conversation**: Just type your technical issue or question
- **`help`**: Show available commands and usage tips
- **`status`**: Display current session information
- **`escalate`**: Request escalation to a human specialist
- **`exit`**, **`quit`**, **`bye`**: End the chat session

### Example Conversation

```text
🔧 Tech Support Chat Agent
═══════════════════════════

Welcome! I'm here to help you with technical issues.
Please describe your problem, and I'll do my best to assist you.

Let's get started! What technical issue are you experiencing?

You: My computer is running very slowly

🔧 Agent: I understand you're experiencing performance issues. Let me suggest some optimization steps.

Suggested actions:
  • Restart your device to clear temporary files
  • Close unnecessary programs and browser tabs
  • Check available disk space (should have at least 15% free)
  • Run a disk cleanup utility

You: I've tried restarting but it's still slow

🔧 Agent: Since restarting didn't resolve the issue, let's try some additional troubleshooting steps...
```

## Architecture

### Key Components

- **`Program.cs`**: Application entry point with command-line interface
- **`ChatService`**: Manages interactive chat sessions and user interactions
- **`AgentSetupService`**: Handles Azure AI Agent configuration and setup
- **`ConversationManager`**: Manages conversation state and message history
- **`EscalationService`**: Handles escalation workflows and ticket management
- **`Configuration/`**: Strongly-typed configuration classes
- **`Models/`**: Data models for chat messages, sessions, and responses

### Services Architecture

```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ChatService   │    │ ConversationMgr │    │ EscalationSvc   │
│                 │────│                 │────│                 │
│ - User I/O      │    │ - Session State │    │ - Ticket Mgmt   │
│ - Chat Loop     │    │ - Message Hist  │    │ - Notifications │
│ - Commands      │    │ - Analytics     │    │ - Queue Mgmt    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐
│ AgentSetupSvc   │    │  Azure AI Agent │
│                 │────│                 │
│ - Agent Config  │    │ - SK Framework  │
│ - Validation    │    │ - RAG via Files │
│ - Setup Logic   │    │ - Vector Store  │
└─────────────────┘    └─────────────────┘
```

## Features

### Current Implementation

✅ **Command-line interface** with multiple commands  
✅ **Configuration management** via appsettings.json, environment variables, and user secrets  
✅ **Interactive chat interface** with rich console output  
✅ **Conversation management** with session tracking and history  
✅ **Escalation workflows** with ticket management and notifications  
✅ **Mock responses** for demonstration without requiring full Azure setup  
✅ **Structured logging** with configurable log levels  
✅ **Error handling** with graceful degradation  

### Planned Implementation (Pending Azure AI Foundry SDK Updates)

🚧 **Azure AI Agent integration** using Semantic Kernel Agent Framework  
🚧 **RAG capabilities** via Azure AI Foundry File Search tool  
🚧 **Vector store integration** for knowledge base queries  
🚧 **Agent Templates** for structured conversation patterns  
🚧 **Knowledge base file upload** and management  

## Development Status

**Current State**: The project provides a complete interactive chat interface with mock responses and escalation workflows. The Azure AI Agent integration is implemented as a placeholder due to evolving Azure AI Foundry SDK APIs.

**Next Steps**:

1. Update `AgentSetupService.cs` with actual Azure AI Agent instantiation when stable SDK is available
2. Implement RAG integration using Azure AI Foundry File Search tool
3. Add knowledge base file upload and vector store management
4. Replace mock responses with actual agent interactions

## Troubleshooting

### Common Issues

1. **Configuration validation fails**:
   - Check that all required configuration values are set
   - Verify Azure AI Foundry endpoint URL format
   - Ensure Azure credentials are properly configured

2. **Authentication errors**:
   - Verify Azure AD tenant and client IDs
   - Check that the application has proper permissions in Azure
   - Try using `az login` to authenticate Azure CLI

3. **Agent setup placeholder message**:
   - This is expected behavior - the Azure AI Agent creation is not yet implemented
   - The application will use mock responses for demonstration

### Logging

Enable debug logging to see detailed operation information:

```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Debug",
      "Microsoft.SemanticKernel": "Trace"
    }
  }
}
```

## Contributing

This is a sample project demonstrating Azure AI Foundry integration. When contributing:

1. Follow the established code structure and patterns
2. Update tests for any new functionality
3. Ensure configuration remains flexible for different environments
4. Update documentation for any new features or changes

## Related Documentation

- [Semantic Kernel Agent Framework](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/)
- [Azure AI Agent Type](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/agent-types/azure-ai-agent)
- [Azure AI Foundry Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/)
- [Azure AI Agent Service](https://learn.microsoft.com/en-us/azure/ai-services/agents/overview)

## License

This sample is provided under the same license as the parent Azure AI Foundry Jumpstart project.
