---
title: Critical Thinking Chat Assistant Python Sample with Tool Calling using Azure AI Projects SDK
version: 2.0
date_created: 2025-01-22
last_updated: 2025-01-22
owner: Azure AI Foundry Jumpstart Team
tags: [sample, python, azure-ai-projects, critical-thinking, chat, interactive, tools, function-calling, syllogism]
---

# Critical Thinking Chat Assistant Python Sample with Tool Calling

A Python sample that provides an interactive conversational assistant designed to challenge user assumptions, promote critical thinking, and facilitate deeper analysis of topics through structured questioning techniques, enhanced with function tool calling capabilities for logical reasoning and syllogism evaluation using the Azure AI Projects SDK.

## 1. Purpose & Scope

This specification defines the requirements for a Python sample application that creates an intelligent conversational agent using the Azure AI Projects SDK with function tool calling capabilities. The assistant is specifically designed to:

- Challenge user assumptions through Socratic questioning
- Promote critical thinking by asking probing questions
- Facilitate deeper analysis of complex topics through structured questioning
- Provide alternative perspectives on user statements
- Guide users through structured problem-solving approaches
- **Evaluate logical reasoning using function tools including syllogism validation**
- **Demonstrate tool calling patterns for critical thinking enhancement**

**Intended Audience**: Developers learning to implement conversational AI applications with Azure AI Foundry, Azure AI Projects SDK, and function tool calling capabilities.

**Assumptions**: Users have basic Python knowledge and access to Azure AI Foundry resources with deployed language models.

## 2. Definitions

- **Azure AI Projects SDK**: The `azure-ai-projects` Python package that provides unified access to Azure AI Foundry project operations including inference, model management, and tool calling capabilities
- **Azure AI Foundry**: Microsoft's unified AI development platform for building, deploying, and managing AI applications
- **Critical Thinking**: The objective analysis and evaluation of an issue to form a judgment, involving questioning assumptions and examining evidence
- **Socratic Method**: A form of inquiry and discussion that involves asking probing questions to stimulate critical thinking
- **Default Azure Credential**: Azure's recommended authentication method that automatically selects appropriate credentials from multiple sources
- **PROJECT_ENDPOINT**: The Azure AI Foundry project endpoint URL in the format `https://<project-name>.<region>.api.azureml.ms`
- **Function Tools**: AI model capabilities that allow the model to call predefined functions to perform specific tasks or retrieve information
- **Tool Calling**: The process by which AI models can invoke external functions during conversation to enhance responses with computed results
- **Syllogism**: A form of logical reasoning consisting of a major premise, minor premise, and conclusion
- **OpenAI Function Calling**: The standard format for defining and executing function calls in compatible AI models

## 3. Requirements, Constraints & Guidelines

### Core Requirements

- **REQ-001**: The application SHALL use the `azure-ai-projects` Python SDK version 1.0.0b12 or later for AI project client operations
- **REQ-002**: The application SHALL use the Azure OpenAI client obtained via AIProjectClient.inference.get_azure_openai_client() for AI model interactions
- **REQ-003**: The application SHALL support both single-question and interactive conversation modes
- **REQ-004**: The application SHALL authenticate using DefaultAzureCredential as the primary method
- **REQ-005**: The application SHALL accept Azure AI Foundry project endpoint via environment variable or command-line argument
- **REQ-006**: The application SHALL implement conversation memory to maintain context across multiple exchanges
- **REQ-007**: The application SHALL provide structured critical thinking prompts and questioning techniques
- **REQ-008**: The application SHALL implement function tool calling capabilities using OpenAI function calling patterns
- **REQ-009**: The application SHALL provide a syllogism evaluation tool that validates logical reasoning structures
- **REQ-010**: The application SHALL handle tool call responses and integrate them into conversation flow
- **REQ-011**: The application SHALL support models that have tool calling capabilities (e.g., GPT-4, GPT-4o)

### Critical Thinking Requirements

- **CRT-001**: The assistant SHALL challenge user assumptions by asking clarifying questions
- **CRT-002**: The assistant SHALL provide alternative perspectives on user statements
- **CRT-003**: The assistant SHALL guide users through evidence-based reasoning
- **CRT-004**: The assistant SHALL ask follow-up questions to deepen analysis
- **CRT-005**: The assistant SHALL encourage users to examine their own biases and preconceptions
- **CRT-006**: The assistant SHALL use tool calling to validate logical arguments when appropriate
- **CRT-007**: The assistant SHALL demonstrate proper syllogistic reasoning through the evaluate_syllogism tool

### Tool Calling Requirements

- **TOOL-001**: The application SHALL implement an evaluate_syllogism function tool using OpenAI function calling patterns
- **TOOL-002**: The syllogism tool SHALL accept major premise, minor premise, and conclusion parameters
- **TOOL-003**: The syllogism tool SHALL validate logical structure and return detailed analysis
- **TOOL-004**: The application SHALL handle function call responses appropriately
- **TOOL-005**: The application SHALL append tool responses to conversation history
- **TOOL-006**: The application SHALL support multiple tool calls within a single conversation
- **TOOL-007**: Tool definitions SHALL include comprehensive parameter descriptions and validation
- **TOOL-008**: The application SHALL gracefully handle tool execution errors and timeouts

### User Experience Requirements

- **UX-001**: The application SHALL provide clear command-line argument parsing with help text
- **UX-002**: The application SHALL support graceful exit commands ('quit', 'exit', 'q')
- **UX-003**: The application SHALL display conversation history in a readable format
- **UX-004**: The application SHALL provide informative error messages for common issues
- **UX-005**: The application SHALL support keyboard interrupt (Ctrl+C) for clean exit

### Authentication & Configuration Requirements

- **AUTH-001**: The application SHALL use DefaultAzureCredential for Azure authentication
- **AUTH-002**: The application SHALL support PROJECT_ENDPOINT environment variable
- **AUTH-003**: The application SHALL support MODEL_DEPLOYMENT_NAME environment variable with default fallback
- **AUTH-004**: The application SHALL validate connection before proceeding with conversations
- **AUTH-005**: The application SHALL support .env file loading when available

### Technical Constraints

- **CON-001**: The application MUST be compatible with Python 3.8 or later
- **CON-002**: The application MUST handle network failures gracefully
- **CON-003**: The application MUST implement proper resource cleanup
- **CON-004**: The application MUST follow PEP 8 style guidelines
- **CON-005**: The application MUST not store sensitive authentication information in logs

### Implementation Guidelines

- **GUD-001**: Use type hints for all function parameters and return values
- **GUD-002**: Provide comprehensive docstrings following PEP 257 conventions
- **GUD-003**: Implement error handling for common failure scenarios
- **GUD-004**: Use structured logging for debugging and monitoring
- **GUD-005**: Follow the established project structure and naming conventions

### Critical Thinking Patterns

- **PAT-001**: Implement Socratic questioning patterns to guide deeper inquiry
- **PAT-002**: Use structured frameworks like "5 Whys" or "Devil's Advocate" approaches
- **PAT-003**: Provide prompts that encourage evidence-based reasoning
- **PAT-004**: Implement conversation flows that build upon previous exchanges

## 4. Interfaces & Data Contracts

### Command Line Interface

```python
def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments for the critical thinking assistant."""
    # --question: Initial question/statement to analyze
    # --interactive: Enable interactive mode
    # --endpoint: Override PROJECT_ENDPOINT
    # --model: Override MODEL_DEPLOYMENT_NAME
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PROJECT_ENDPOINT` | Yes | None | Azure AI Foundry project endpoint URL |
| `MODEL_DEPLOYMENT_NAME` | No | "gpt-4o" | Name of the deployed language model (must support tool calling) |

### Azure AI Projects Client Configuration

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

async with DefaultAzureCredential() as credential:
    async with AIProjectClient(endpoint=project_endpoint, credential=credential) as project_client:
        # Get Azure OpenAI client for inference operations
        async with await project_client.inference.get_azure_openai_client(
            api_version="2024-10-21"
        ) as client:
            # Use the client for chat completions with tool calling
            response = await client.chat.completions.create(...)
```

### Tool Calling Implementation

```python
# Define syllogism evaluation tool using OpenAI function calling format
tools = [
    {
        "type": "function",
        "function": {
            "name": "evaluate_syllogism",
            "description": "Evaluates the logical validity of a syllogism consisting of major premise, minor premise, and conclusion",
            "parameters": {
                "type": "object",
                "properties": {
                    "major_premise": {
                        "type": "string",
                        "description": "The major premise of the syllogism"
                    },
                    "minor_premise": {
                        "type": "string", 
                        "description": "The minor premise of the syllogism"
                    },
                    "conclusion": {
                        "type": "string",
                        "description": "The conclusion of the syllogism"
                    }
                },
                "required": ["major_premise", "minor_premise", "conclusion"]
            }
        }
    }
]

# Make completion with tools
response = await client.chat.completions.create(
    model=model_deployment_name,
    messages=conversation,
    tools=tools,
    tool_choice="auto"
)
```

### Tool Function Implementation

```python
def evaluate_syllogism(major_premise: str, minor_premise: str, conclusion: str) -> str:
    """
    Evaluate the logical validity of a syllogism.
    
    Args:
        major_premise: The major premise statement
        minor_premise: The minor premise statement  
        conclusion: The conclusion statement
        
    Returns:
        JSON string containing validity analysis
    """
    # Implementation returns structured analysis
    return json.dumps({
        "valid": True|False,
        "form": "categorical|conditional|disjunctive",
        "analysis": "Detailed logical analysis",
        "errors": ["List of logical errors if any"]
    })
```

### Message Structure

```python
# System message for critical thinking behavior with tool usage
system_message = {"role": "system", "content": "Critical thinking assistant with logical reasoning tools..."}

# User input
user_message = {"role": "user", "content": "User's statement or question..."}

# Assistant response with tool calls
assistant_message = {"role": "assistant", "tool_calls": [...]}

# Tool response
tool_message = {"role": "tool", "content": function_result, "tool_call_id": tool_call.id}
```

### Conversation Memory Schema

```python
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class ConversationTurn:
    """Represents a single conversation exchange."""
    user_input: str
    assistant_response: str
    timestamp: str
    thinking_techniques_used: List[str]
```

## 5. Acceptance Criteria

- **AC-001**: Given a user provides a statement, When the assistant processes it, Then it SHALL ask at least one probing question that challenges assumptions
- **AC-002**: Given the user starts interactive mode, When they type 'quit', Then the application SHALL terminate gracefully
- **AC-003**: Given an invalid PROJECT_ENDPOINT, When the application initializes, Then it SHALL display a clear error message and exit
- **AC-004**: Given a conversation with multiple exchanges, When the user asks a follow-up question, Then the assistant SHALL reference previous context
- **AC-005**: Given the user provides a controversial statement, When the assistant responds, Then it SHALL present alternative viewpoints without taking sides
- **AC-006**: Given the application is running interactively, When the user presses Ctrl+C, Then it SHALL exit cleanly without error
- **AC-007**: Given environment variables are not set, When using command-line arguments, Then the application SHALL use the provided values
- **AC-008**: Given the AI model deployment is unavailable, When making a request, Then the application SHALL handle the error gracefully
- **AC-009**: Given a user provides a logical argument, When the model decides to use tools, Then it SHALL call the evaluate_syllogism function with appropriate parameters
- **AC-010**: Given the evaluate_syllogism tool is called with valid parameters, When executed, Then it SHALL return a JSON analysis of logical validity
- **AC-011**: Given a tool call response, When received, Then the assistant SHALL integrate the results into its critical thinking guidance
- **AC-012**: Given the model supports tool calling, When initialized, Then the application SHALL register the syllogism evaluation tool successfully
- **AC-013**: Given multiple tool calls in a conversation, When processing responses, Then each tool result SHALL be properly attributed and contextualized
- **AC-014**: Given an invalid syllogism structure, When evaluated by the tool, Then it SHALL identify specific logical fallacies or errors

## 6. Test Automation Strategy

### Test Levels

- **Unit Tests**: Individual function validation, argument parsing, message formatting
- **Integration Tests**: Azure AI Inference client interaction, authentication flow
- **End-to-End Tests**: Complete conversation flows, interactive mode testing

### Frameworks

- **pytest**: Primary testing framework for Python
- **pytest-asyncio**: For testing asynchronous functionality if implemented
- **pytest-mock**: For mocking Azure AI Inference client responses
- **python-dotenv**: For test environment configuration

### Test Data Management

- Mock conversation examples with various critical thinking scenarios
- Simulated API responses for different questioning techniques
- Test cases covering edge cases like empty input, long conversations

### CI/CD Integration

- Automated testing in GitHub Actions pipelines
- Linting with pylint, flake8, and mypy
- Code formatting validation with black or ruff

### Coverage Requirements

- Minimum 85% code coverage for core functionality
- 100% coverage for argument parsing and configuration
- Exception handling paths must be tested

### Performance Testing

- Response time validation for typical conversation exchanges
- Memory usage monitoring for long-running interactive sessions

## 7. Rationale & Context

The critical thinking assistant addresses a growing need for AI applications that don't just provide answers but help users develop analytical skills. By implementing Socratic questioning techniques, the application serves as a learning tool that promotes intellectual growth.

The choice of Azure AI Inference SDK over Azure AI Projects SDK provides more direct control over model interactions and simplifies the implementation for conversational scenarios. The unified client interface supports multiple deployment targets including Azure AI Foundry, Azure OpenAI, and GitHub Models.

The interactive mode design encourages extended engagement, allowing users to explore topics deeply through multiple conversation turns. This approach is more effective for developing critical thinking skills than single-shot Q&A interactions.

## 8. Dependencies & External Integrations

### External Systems

- **EXT-001**: Azure AI Foundry - Hosts the deployed language model and provides the inference endpoint
- **EXT-002**: Tool-capable AI Models - Models that support function calling (GPT-4, GPT-4o, Claude-3, etc.)

### Third-Party Services

- **SVC-001**: Azure Active Directory - Provides authentication and authorization services
- **SVC-002**: Azure AI Project API - REST API for project operations and model inference with tool calling support
- **SVC-003**: Function Tool Runtime - Local execution environment for syllogism evaluation functions

### Infrastructure Dependencies

- **INF-001**: Azure AI Foundry Project - Container for AI resources and model deployments
- **INF-002**: Language Model Deployment - Tool-capable conversational AI model (GPT-4, GPT-4o recommended)
- **INF-003**: Network Connectivity - HTTPS access to Azure services
- **INF-004**: Python Function Environment - Runtime support for tool function execution

### Technology Platform Dependencies

- **PLT-001**: Python Runtime - Version 3.8 or later with pip package manager
- **PLT-002**: Azure AI Projects SDK - Version 1.0.0b12 or compatible with OpenAI client support
- **PLT-003**: Azure Identity SDK - For DefaultAzureCredential support
- **PLT-004**: OpenAI Python SDK - For chat completions with function calling support
- **PLT-005**: JSON Processing - Built-in json module for tool argument parsing and response formatting
- **PLT-006**: Type Hinting - typing-extensions for enhanced type safety with tool definitions

### Compliance Dependencies

- **COM-001**: Azure Security Standards - Application must follow Azure SDK security practices
- **COM-002**: Data Privacy - Conversation data handling must comply with privacy requirements
- **COM-003**: Tool Execution Security - Function tools must validate inputs and handle errors safely

## 9. Examples & Edge Cases

### Basic Usage Example

```python
# Single question mode
python critical_thinking_chat.py --question "I think social media is bad for society"

# Interactive mode
python critical_thinking_chat.py --interactive

# Custom endpoint and model (with tool support)
python critical_thinking_chat.py --interactive --endpoint "https://my-project.eastus.api.azureml.ms" --model "gpt-4o"
```

### Critical Thinking with Tool Calling Conversation Flow

```python
# User: "All politicians are corrupt. John is a politician. Therefore John is corrupt."
# Assistant: "I notice you've presented what appears to be a logical argument. Let me evaluate the structure of this reasoning for you."
# [Tool Call: evaluate_syllogism("All politicians are corrupt", "John is a politician", "John is corrupt")]
# Tool Response: {"valid": false, "form": "categorical", "analysis": "The major premise 'All politicians are corrupt' is an overgeneralization...", "errors": ["hasty generalization", "sweeping statement"]}
# Assistant: "The logical analysis reveals this syllogism has structural issues. While the form is valid, the major premise contains a hasty generalization. What evidence supports the claim that 'all politicians are corrupt'? Could there be exceptions to this sweeping statement?"
```

### Syllogism Tool Usage Examples

```python
# Valid syllogism
evaluate_syllogism("All humans are mortal", "Socrates is a human", "Socrates is mortal")
# Returns: {"valid": true, "form": "categorical", "analysis": "Classic valid syllogism...", "errors": []}

# Invalid syllogism - affirming the consequent
evaluate_syllogism("If it rains, the ground gets wet", "The ground is wet", "It rained")
# Returns: {"valid": false, "form": "conditional", "analysis": "Fallacy of affirming consequent...", "errors": ["affirming_consequent"]}

# Incomplete syllogism
evaluate_syllogism("Some cats are black", "Fluffy is a cat", "Fluffy is black")
# Returns: {"valid": false, "form": "categorical", "analysis": "Invalid distribution...", "errors": ["undistributed_middle"]}
```

### Tool Calling Implementation Pattern

```python
# Check if model wants to use tools
if response.choices[0].finish_reason == "tool_calls":
    # Process each tool call
    messages.append({
        "role": "assistant", 
        "tool_calls": response.choices[0].message.tool_calls
    })
    
    for tool_call in response.choices[0].message.tool_calls:
        if tool_call.function.name == "evaluate_syllogism":
            # Parse arguments and execute function
            function_args = json.loads(tool_call.function.arguments)
            result = evaluate_syllogism(**function_args)
            
            # Add tool response to conversation
            messages.append({
                "role": "tool",
                "content": result,
                "tool_call_id": tool_call.id
            })
    
    # Get final response incorporating tool results
    final_response = await client.chat.completions.create(
        model=model_deployment_name,
        messages=messages,
        tools=tools
    )
```

### Edge Cases

```python
# Empty user input
if not user_input.strip():
    print("Please provide a statement or question to analyze.")
    continue

# Tool execution error
try:
    result = evaluate_syllogism(**function_args)
except Exception as e:
    result = json.dumps({"error": f"Tool execution failed: {str(e)}"})

# Multiple simultaneous tool calls
if len(response.choices[0].message.tool_calls) > 1:
    for tool_call in response.choices[0].message.tool_calls:
        # Process each tool call independently

# Model without tool support
try:
    response = await client.chat.completions.create(
        model=model_deployment_name,
        messages=conversation,
        tools=tools
    )
except Exception as e:
    # Fall back to non-tool mode
    response = await client.chat.completions.create(
        model=model_deployment_name,
        messages=conversation
    )
    print("Note: Tool calling not supported by this model")

# Malformed tool arguments
try:
    function_args = json.loads(tool_call.function.arguments)
except json.JSONDecodeError:
    result = json.dumps({"error": "Invalid tool arguments provided"})
```

## 10. Validation Criteria

- **VAL-001**: The application successfully connects to Azure AI Foundry endpoint via AIProjectClient and obtains Azure OpenAI client
- **VAL-002**: Critical thinking prompts generate meaningful follow-up questions
- **VAL-003**: Interactive mode maintains conversation context across multiple turns including tool calls
- **VAL-004**: Authentication works with DefaultAzureCredential in various Azure environments
- **VAL-005**: Error handling provides actionable feedback for common issues and tool execution errors
- **VAL-006**: Command-line interface is intuitive and well-documented
- **VAL-007**: Application follows Python best practices and coding standards
- **VAL-008**: Resource cleanup prevents memory leaks in long-running sessions
- **VAL-009**: Tool calling functionality integrates seamlessly with conversational flow using OpenAI patterns
- **VAL-010**: Syllogism evaluation tool provides accurate logical analysis
- **VAL-011**: Tool definitions follow OpenAI function calling specifications
- **VAL-012**: Multiple tool calls in single conversation are handled correctly
- **VAL-013**: Tool execution errors are gracefully handled and reported
- **VAL-014**: Tool responses enhance critical thinking guidance effectively

## 11. Related Specifications / Further Reading

- [Azure AI Projects SDK Documentation](https://pypi.org/project/azure-ai-projects/)
- [Azure AI Projects SDK Chat Completions Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/inference/async_samples/sample_chat_completions_with_azure_openai_client_async.py)
- [Azure AI Foundry Project Documentation](https://learn.microsoft.com/azure/ai-studio/)
- [OpenAI Function Calling Documentation](https://platform.openai.com/docs/guides/function-calling)
- [Critical Thinking Framework Reference](https://www.criticalthinking.org/pages/defining-critical-thinking/766)
- [Socratic Method Implementation Guide](https://plato.stanford.edu/entries/socrates/)
- [Syllogistic Logic and Validity](https://plato.stanford.edu/entries/logic-ancient/#Syl)
- [Python Argument Parsing Best Practices](https://docs.python.org/3/library/argparse.html)
- [Azure SDK for Python Authentication](https://learn.microsoft.com/python/api/overview/azure/identity-readme)
- [OpenAI Python SDK Documentation](https://github.com/openai/openai-python)
- [JSON Schema Validation for Tool Parameters](https://json-schema.org/understanding-json-schema/)
