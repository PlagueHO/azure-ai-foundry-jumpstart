---
title: .NET Console Tech Support Chat Agent Sample Project
version: 1.0
date_created: 2025-06-12
last_updated: 2025-06-12
owner: Azure AI Foundry Jumpstart Team
tags: [tool, sample, dotnet, csharp, semantic-kernel, azure-ai-agent-service, chat-agent, tech-support]
---

# Introduction

This specification defines a .NET 8 console application sample project that demonstrates a tech support chat agent using Semantic Kernel and Azure AI Agent Service via Azure AI Foundry. The sample showcases conversational AI capabilities for technical support scenarios, including problem diagnosis, solution recommendations, and escalation workflows.

## 1. Purpose & Scope

The purpose of this specification is to provide requirements, constraints, and interface definitions for a tech support chat agent console application sample. The application demonstrates:

- Interactive console-based chat interface for tech support scenarios
- Integration with Azure AI Agent Service through Azure AI Foundry
- Semantic Kernel framework utilization for AI orchestration
- RAG (Retrieval-Augmented Generation) capabilities using Azure AI Search
- Tech support knowledge base integration
- Conversation state management and context preservation
- Escalation and handoff workflows

Intended audience: .NET developers, AI/ML developers, and solution architects building conversational AI applications for customer support scenarios.

## 2. Definitions

- **Azure AI Agent Service**: Microsoft Azure's service for building and deploying conversational AI agents
- **Azure AI Foundry**: Azure's unified platform for AI application development and deployment
- **Semantic Kernel**: Microsoft's open-source SDK for integrating AI models with conventional programming languages
- **RAG**: Retrieval-Augmented Generation, combining search with generative AI for contextual responses
- **Chat Agent**: An AI-powered conversational interface designed to assist users with technical support
- **Knowledge Base**: A structured repository of technical support information and solutions
- **Conversation Context**: The maintained state and history of user interactions within a chat session
- **Escalation Workflow**: The process of transferring complex issues to human support agents
- **Intent Recognition**: The ability to understand and classify user requests and problems

## 3. Requirements, Constraints & Guidelines

| Type        | ID          | Description |
|-------------|-------------|-------------|
| **REQ-001** | Framework   | The application must be built using .NET 8 and C# with Semantic Kernel SDK. |
| **REQ-002** | Integration | The application must integrate with Azure AI Agent Service via Azure AI Foundry. |
| **REQ-003** | Interface   | The application must provide an interactive console-based chat interface. |
| **REQ-004** | Knowledge   | The application must integrate with Azure AI Search for knowledge base retrieval. |
| **REQ-005** | Context     | The application must maintain conversation context throughout the session. |
| **REQ-006** | Intent      | The application must recognize common tech support intents (problem report, how-to, troubleshooting). |
| **REQ-007** | Responses   | The application must provide contextual, helpful responses based on retrieved knowledge. |
| **REQ-008** | Escalation  | The application must detect when to escalate issues to human agents. |
| **REQ-009** | Config      | The application must support configuration via appsettings.json and environment variables. |
| **REQ-010** | Logging     | The application must implement structured logging for monitoring and debugging. |
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
    "FoundryEndpoint": "https://your-foundry.azure.com",
    "AgentServiceEndpoint": "https://your-agent-service.azure.com",
    "TenantId": "your-tenant-id",
    "ClientId": "your-client-id"
  },
  "AzureSearch": {
    "ServiceName": "your-search-service",
    "IndexName": "tech-support-kb",
    "ApiKey": "your-search-key"
  },
  "ChatAgent": {
    "MaxConversationTurns": 50,
    "ContextWindowSize": 4000,
    "EscalationThreshold": 3,
    "SystemPrompt": "You are a helpful tech support agent..."
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft": "Warning"
    }
  }
}
```

### Chat Message Structure

```csharp
public class ChatMessage
{
    public string Id { get; set; }
    public ChatRole Role { get; set; } // User, Assistant, System
    public string Content { get; set; }
    public DateTime Timestamp { get; set; }
    public Dictionary<string, object> Metadata { get; set; }
}

public enum ChatRole
{
    User,
    Assistant,
    System
}
```

### Agent Response Structure

```csharp
public class AgentResponse
{
    public string ResponseText { get; set; }
    public List<string> RetrievedSources { get; set; }
    public double ConfidenceScore { get; set; }
    public bool RequiresEscalation { get; set; }
    public List<string> SuggestedActions { get; set; }
    public Dictionary<string, object> Metadata { get; set; }
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
- **Semantic Kernel**: Offers robust AI orchestration and plugin architecture for extensible functionality
- **Azure AI Agent Service**: Leverages managed service capabilities for scalable agent deployment
- **RAG Integration**: Ensures responses are grounded in authoritative knowledge base content
- **Escalation Logic**: Demonstrates real-world support scenarios where human intervention is needed
- **Configuration-driven**: Enables easy adaptation to different environments and use cases
- **.NET 8**: Provides modern language features, performance improvements, and long-term support

## 6. Examples & Edge Cases

### Basic Conversation Flow

```
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

```
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
// Network connectivity issues
try
{
    var response = await agentService.GetResponseAsync(userMessage);
}
catch (HttpRequestException ex)
{
    Console.WriteLine("I'm having trouble connecting to our knowledge base right now. Let me try to help you with general guidance...");
    // Fallback to cached responses or basic troubleshooting
}

// Rate limiting
catch (TooManyRequestsException ex)
{
    Console.WriteLine("I'm experiencing high demand right now. Please wait a moment while I process your request...");
    await Task.Delay(ex.RetryAfter);
    // Retry logic
}
```

## 7. Validation Criteria

- The application must successfully authenticate with Azure AI services using configured credentials
- The chat interface must accept user input and provide relevant responses within the specified time limit
- Conversation context must be maintained across multiple turns in a session
- Knowledge base integration must successfully retrieve and cite relevant information
- Escalation logic must trigger appropriately based on defined criteria
- Configuration must be loaded correctly from appsettings.json and environment variables
- All API calls must include proper error handling with user-friendly messages
- The application must log relevant events without exposing sensitive information
- Unit tests must achieve minimum 80% code coverage
- Integration tests must validate end-to-end chat scenarios

## 8. Related Specifications / Further Reading

- [Azure AI Agent Service Documentation](https://learn.microsoft.com/en-us/azure/ai-services/agents/)
- [Azure AI Foundry Documentation](https://learn.microsoft.com/en-us/azure/ai-studio/)
- [Semantic Kernel Documentation](https://learn.microsoft.com/en-us/semantic-kernel/)
- [.NET 8 Documentation](https://learn.microsoft.com/en-us/dotnet/core/whats-new/dotnet-8)
- [Azure AI Search Documentation](https://learn.microsoft.com/en-us/azure/search/)
- [Azure Identity Documentation](https://learn.microsoft.com/en-us/dotnet/azure/sdk/authentication)
- [tool-create-ai-search-index.md](./tool-create-ai-search-index.md)