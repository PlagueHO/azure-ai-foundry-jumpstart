---
title: .NET Console Tech Support Chat Agent Sample Project
version: 1.0
date_created: 2025-06-12
last_updated: 2025-06-12
owner: Azure AI Foundry Jumpstart Team
tags: [tool, sample, dotnet, csharp, semantic-kernel, azure-ai-agent-service, chat-agent, tech-support]
---

# Introduction

This specification defines a .NET 8 console application sample project that demonstrates a tech support chat agent using the Semantic Kernel Agent Framework with Azure AI Agent type and Azure AI Foundry SDK client libraries. The sample showcases conversational AI capabilities for technical support scenarios, including problem diagnosis, solution recommendations, and escalation workflows using Agent Templates and the Agent Framework's conversation management.

## 1. Purpose & Scope

The purpose of this specification is to provide requirements, constraints, and interface definitions for a tech support chat agent console application sample. The application demonstrates:

- Interactive console-based chat interface for tech support scenarios
- Implementation using Semantic Kernel Agent Framework with Azure AI Agent type
- Azure AI Foundry SDK client libraries integration for AI services
- Agent Templates for structured conversation patterns
- RAG (Retrieval-Augmented Generation) capabilities using Azure AI Search
- Tech support knowledge base integration through Agent Framework
- Conversation state management via Agent Framework's built-in capabilities
- Escalation and handoff workflows using Agent orchestration

Intended audience: .NET developers, AI/ML developers, and solution architects building conversational AI applications for customer support scenarios.

## 2. Definitions

- **Azure AI Agent**: A specialized agent within the Semantic Kernel framework (AzureAIAgent class) that integrates with Azure AI services
- **Azure AI Foundry**: Azure's unified platform for AI application development and deployment
- **Semantic Kernel Agent Framework**: Microsoft's framework for building conversational AI agents with structured conversation management
- **PersistentAgentsClient**: The client class for interacting with Azure AI Agent Service through Azure AI Foundry projects
- **AzureAIAgentThread**: Thread management class for maintaining conversation state in Azure AI Agents
- **PromptTemplateConfig**: Configuration structure for defining agent instructions using templated parameters
- **Azure AI Foundry SDK**: Client libraries for integrating with Azure AI Foundry services
- **RAG**: Retrieval-Augmented Generation, combining search with generative AI for contextual responses
- **Chat Agent**: An AI-powered conversational interface designed to assist users with technical support
- **Knowledge Base**: A structured repository of technical support information and solutions
- **Conversation Context**: The maintained state and history of user interactions within a chat session
- **Escalation Workflow**: The process of transferring complex issues to human support agents
- **Intent Recognition**: The ability to understand and classify user requests and problems

## 3. Requirements, Constraints & Guidelines

| Type        | ID          | Description |
|-------------|-------------|-------------|
| **REQ-001** | Framework   | The application must be built using .NET 8 and C# with Semantic Kernel Agent Framework. |
| **REQ-002** | Agent Type  | The application must use AzureAIAgent from Microsoft.SemanticKernel.Agents.AzureAI package. |
| **REQ-003** | SDK         | The application must use PersistentAgentsClient for Azure AI Foundry project integration. |
| **REQ-004** | Templates   | The application must utilize PromptTemplateConfig for structured agent instructions and YAML-based templates. |
| **REQ-005** | Interface   | The application must provide an interactive console-based chat interface. |
| **REQ-006** | Knowledge   | The application must integrate with Azure AI Search using AzureAISearchToolDefinition via Agent Framework. |
| **REQ-007** | Context     | The application must use AzureAIAgentThread for conversation state management and threading. |
| **REQ-008** | Intent      | The application must recognize common tech support intents using templated agent instructions. |
| **REQ-009** | Responses   | The application must provide contextual, helpful responses using agent streaming capabilities. |
| **REQ-010** | Escalation  | The application must implement escalation workflows using agent orchestration patterns. |
| **REQ-011** | Config      | The application must support configuration via appsettings.json and environment variables. |
| **REQ-012** | Logging     | The application must implement structured logging for monitoring and debugging. |
| **SEC-001** | Auth        | The application must use secure authentication methods (Azure AD, Managed Identity). |
| **SEC-002** | Data        | The application must not log or persist sensitive user information. |
| **SEC-003** | Secrets     | The application must securely manage API keys and connection strings. |
| **CON-001** | Stability   | The application must use stable, production-ready SDK versions. |
| **CON-002** | Performance | Single conversation responses must complete within 10 seconds under normal conditions. |
| **GUD-001** | Patterns    | The application should follow .NET coding standards and best practices. |
| **GUD-002** | Async       | The application should use async/await patterns for all I/O operations. |
| **GUD-003** | DI          | The application should use dependency injection for service management. |
| **PAT-001** | SOLID       | The application should follow SOLID principles for maintainable code architecture. |

## 4. Interfaces & Data Contracts

### Configuration Schema

```json
{
  "AzureAI": {
    "FoundryEndpoint": "https://your-foundry-project.eastus.inference.ml.azure.com",
    "ProjectName": "your-project-name",
    "ModelName": "gpt-4o",
    "TenantId": "your-tenant-id",
    "ClientId": "your-client-id"
  },
  "AzureSearch": {
    "ServiceName": "your-search-service",
    "IndexName": "tech-support-kb",
    "ConnectionId": "your-search-connection-id"
  },
  "AgentFramework": {
    "AgentName": "TechSupportAgent",
    "AgentDescription": "Technical support agent for troubleshooting and assistance",
    "MaxConversationTurns": 50,
    "EscalationThreshold": 3,
    "Instructions": "You are a helpful tech support agent that assists users with technical issues. Use the available knowledge base to provide accurate solutions and escalate complex issues when needed."
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft": "Warning",
      "Microsoft.SemanticKernel": "Debug"
    }
  }
}
```

### Agent Framework Integration

```csharp
// Using Semantic Kernel Agent Framework with Azure AI Agent
using Microsoft.SemanticKernel.Agents.AzureAI;
using Azure.Identity;

public class TechSupportAgentService
{
    private readonly AzureAIAgent _agent;
    private readonly AzureAIAgentThread _agentThread;
    private readonly PersistentAgentsClient _agentsClient;
    
    public async Task<string> ProcessUserMessageAsync(string userMessage)
    {
        // Add user message to the conversation thread
        ChatMessageContent message = new(AuthorRole.User, userMessage);
        
        // Get agent response with streaming
        await foreach (ChatMessageContent response in _agent.InvokeAsync(message, _agentThread))
        {
            return response.Content;
        }
        
        return "I'm sorry, I couldn't process your request.";
    }
}
```

### Agent Configuration and Setup

```csharp
// Agent creation using current Azure AI Agent patterns
using Microsoft.SemanticKernel.Agents.AzureAI;
using Azure.Identity;

public class TechSupportAgentSetup
{
    public static async Task<AzureAIAgent> CreateAgentAsync(IConfiguration configuration)
    {
        // Create agents client for Azure AI Foundry project
        PersistentAgentsClient agentsClient = AzureAIAgent.CreateAgentsClient(
            configuration["AzureAI:FoundryEndpoint"], 
            new DefaultAzureCredential());

        // Define agent with Azure AI Search tool integration
        PersistentAgent agentDefinition = await agentsClient.Administration.CreateAgentAsync(
            configuration["AzureAI:ModelName"], // e.g., "gpt-4o"
            name: configuration["AgentFramework:AgentName"],
            description: configuration["AgentFramework:AgentDescription"],
            instructions: configuration["AgentFramework:Instructions"],
            tools: [new AzureAISearchToolDefinition()],
            toolResources: new()
            {
                AzureAISearch = new()
                {
                    IndexList = { 
                        new AISearchIndexResource(
                            configuration["AzureSearch:ConnectionId"], 
                            configuration["AzureSearch:IndexName"]) 
                    }
                }
            });

        // Create Semantic Kernel agent from definition
        return new AzureAIAgent(agentDefinition, agentsClient);
    }
}
```

### CLI Interface

```bash
# Basic usage
dotnet run

# With custom configuration
dotnet run -- --config path/to/config.json

# With specific log level
dotnet run -- --log-level Debug

# Help
dotnet run -- --help
```

## 5. Rationale & Context

- **Console Application**: Provides a simple, focused demonstration of chat agent capabilities without UI complexity
- **Semantic Kernel Agent Framework**: Offers structured conversation management and agent orchestration patterns
- **AzureAIAgent Type**: Leverages native Azure AI integration with managed capabilities for scalable agent deployment
- **PromptTemplateConfig**: Provides structured, templated instructions and reusable conversation patterns for tech support scenarios
- **PersistentAgentsClient**: Ensures seamless integration with Azure AI Foundry projects and agent lifecycle management
- **AzureAIAgentThread**: Provides automatic conversation state management and thread persistence
- **RAG Integration**: Ensures responses are grounded in authoritative knowledge base content through AzureAISearchToolDefinition
- **Escalation Logic**: Demonstrates real-world support scenarios using agent orchestration capabilities
- **Configuration-driven**: Enables easy adaptation to different environments and use cases
- **.NET 8**: Provides modern language features, performance improvements, and long-term support

## 6. Examples & Edge Cases

### Basic Conversation Flow

```text
User: My laptop won't turn on
Agent: I understand you're having trouble with your laptop not powering on. Let me help you troubleshoot this issue.

Based on our knowledge base, here are the most common causes and solutions:

1. **Power Supply Issues**:
   - Check if the power adapter is properly connected
   - Try a different power outlet
   - Look for any damage to the power cable

2. **Battery Problems**:
   - If using a removable battery, try removing and reinserting it
   - Try powering on with just the power adapter (battery removed)

3. **Hardware Issues**:
   - Check for any loose connections
   - Listen for any beeping sounds or LED indicators

Would you like me to walk you through these steps, or do you have more specific details about what happens when you try to turn it on?
```

### Escalation Scenario

```text
User: I've tried everything you suggested but it's still not working. This is urgent as I have a presentation tomorrow.
Agent: I understand this is urgent and you've already tried the basic troubleshooting steps. Given the complexity of this issue and your time constraints, I recommend escalating this to one of our specialist technicians who can provide immediate assistance.

I'm creating an escalation ticket with the following details:
- Issue: Laptop won't power on after basic troubleshooting
- Priority: High (urgent business need)
- Steps attempted: [Previous troubleshooting steps]

You should receive a call from a specialist within the next 30 minutes. Is the phone number ending in 1234 the best number to reach you?
```

### Error Handling

```csharp
// Agent Framework Error Handling
using Microsoft.SemanticKernel.Agents.AzureAI;
using Azure.Identity;

try
{
    // Process message through Azure AI Agent
    ChatMessageContent message = new(AuthorRole.User, userMessage);
    await foreach (ChatMessageContent response in agent.InvokeAsync(message, agentThread))
    {
        Console.WriteLine(response.Content);
    }
}
catch (RequestFailedException ex) when (ex.Status == 429)
{
    Console.WriteLine("I'm experiencing high demand right now. Please wait a moment...");
    await Task.Delay(TimeSpan.FromSeconds(30), cancellationToken);
    // Retry with exponential backoff
}
catch (Exception ex) when (ex.Message.Contains("agent"))
{
    Console.WriteLine($"Agent error: {ex.Message}");
    // Fallback to basic troubleshooting guidance
    await HandleFallbackScenarioAsync(userMessage);
}
catch (HttpRequestException ex)
{
    Console.WriteLine("I'm having trouble connecting right now. Let me try to help with general guidance...");
    // Use cached responses or offline guidance
}
finally
{
    // Clean up resources when conversation ends
    await agentThread.DeleteAsync();
}
```

## 7. Validation Criteria

- The application must successfully authenticate with Azure AI Foundry using configured credentials
- The AzureAIAgent must be properly instantiated using PersistentAgentsClient
- Agent instructions must be correctly configured using PromptTemplateConfig patterns
- The chat interface must accept user input and provide relevant responses within the specified time limit
- Conversation context must be maintained through AzureAIAgentThread functionality
- Knowledge base integration must successfully retrieve and cite relevant information through AzureAISearchToolDefinition
- Escalation logic must trigger appropriately using agent orchestration patterns
- Configuration must be loaded correctly from appsettings.json and environment variables
- All Azure AI Agent API calls must include proper error handling with user-friendly messages
- The application must log relevant events without exposing sensitive information
- Unit tests must achieve minimum 80% code coverage including Azure AI Agent components
- Integration tests must validate end-to-end Azure AI Agent conversation scenarios

## 8. Related Specifications / Further Reading

- [Semantic Kernel Agent Framework Documentation](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/?pivots=programming-language-csharp)
- [Azure AI Agent Type Documentation](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/agent-types/azure-ai-agent?pivots=programming-language-csharp)
- [Agent Templates Documentation](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/agent-templates?pivots=programming-language-csharp)
- [Azure AI Foundry SDK Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/sdk-overview?pivots=programming-language-csharp)
- [Azure AI Foundry Documentation](https://learn.microsoft.com/en-us/azure/ai-studio/)
- [Semantic Kernel Documentation](https://learn.microsoft.com/en-us/semantic-kernel/)
- [.NET 8 Documentation](https://learn.microsoft.com/en-us/dotnet/core/whats-new/dotnet-8)
- [Azure AI Search Documentation](https://learn.microsoft.com/en-us/azure/search/)
- [Azure Identity Documentation](https://learn.microsoft.com/en-us/dotnet/azure/sdk/authentication)
- [tool-create-ai-search-index.md](./tool-create-ai-search-index.md)