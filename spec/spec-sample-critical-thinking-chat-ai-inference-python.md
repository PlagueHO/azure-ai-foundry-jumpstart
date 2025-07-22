---
title: Critical Thinking Chat Assistant - AI Implementation Spec
version: 3.0
tags: [python, azure-ai-projects, critical-thinking, tool-calling, syllogism]
---

# Critical Thinking Chat Assistant with Tool Calling

Interactive Python chat assistant using Azure AI Projects SDK with function tool calling for critical thinking enhancement and syllogism evaluation.

## Core Purpose

Create a conversational AI that challenges assumptions through Socratic questioning, provides alternative perspectives, and validates logical arguments using tool calling capabilities.

## Key Definitions

- **Azure AI Projects SDK**: `azure-ai-projects` package for Azure AI Foundry operations
- **PROJECT_ENDPOINT**: Azure AI Foundry project URL `https://<project-name>.<region>.api.azureml.ms`
- **Tool Calling**: OpenAI function calling for syllogism evaluation
- **Critical Thinking**: Socratic questioning to challenge assumptions and examine evidence

## 3. Requirements

### Core Requirements

- **REQ-001**: Use `azure-ai-projects` SDK v1.0.0b12+ with AIProjectClient.inference.get_azure_openai_client()
- **REQ-002**: Support single-question and interactive conversation modes
- **REQ-003**: Authenticate using DefaultAzureCredential
- **REQ-004**: Accept PROJECT_ENDPOINT via environment or command-line
- **REQ-005**: Implement conversation memory for context retention
- **REQ-006**: Provide syllogism evaluation tool using OpenAI function calling
- **REQ-007**: Support configurable logging levels (default: ERROR)

### Critical Thinking Behavior

- **CRT-001**: Challenge assumptions with clarifying questions
- **CRT-002**: Provide alternative perspectives without bias
- **CRT-003**: Guide evidence-based reasoning
- **CRT-004**: Use syllogism tool for logical argument validation

### Tool Calling Requirements

- **TOOL-001**: Request user permission before tool execution
- **TOOL-002**: Display tool name, purpose, and parameters clearly
- **TOOL-003**: Handle approve/decline responses gracefully
- **TOOL-004**: Continue conversation when tools are declined
- **TOOL-005**: Integrate tool results into critical thinking guidance

### User Experience

- **UX-001**: Support 'quit'/'exit'/'q' commands
- **UX-002**: Handle Ctrl+C cleanly
- **UX-003**: Provide clear error messages
- **UX-004**: Display readable conversation flow

## 4. Implementation Guide

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PROJECT_ENDPOINT` | Yes | None | Azure AI Foundry project endpoint |
| `MODEL_DEPLOYMENT_NAME` | No | "gpt-4o" | Tool-capable model name |
| `VERBOSE_LOGGING` | No | "ERROR" | Logging level |

### Client Setup

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
project_client = AIProjectClient(endpoint=project_endpoint, credential=credential)
client = project_client.inference.get_azure_openai_client(api_version="2024-10-21")
```

### System Prompt

```python
SYSTEM_PROMPT = """You are a Critical Thinking Assistant. Challenge assumptions through Socratic questioning, provide alternative perspectives, and guide evidence-based reasoning. When users present logical arguments, use the evaluate_syllogism tool to analyze validity. Ask probing questions like: "What evidence supports this?", "What might someone who disagrees say?", "What assumptions are you making?"."""
```

### Syllogism Tool Definition

```python
SYLLOGISM_TOOL = {
    "type": "function",
    "function": {
        "name": "evaluate_syllogism",
        "description": "Evaluate logical validity of major premise, minor premise, conclusion",
        "parameters": {
            "type": "object", 
            "properties": {
                "major_premise": {"type": "string", "description": "Major premise statement"},
                "minor_premise": {"type": "string", "description": "Minor premise statement"},
                "conclusion": {"type": "string", "description": "Conclusion statement"}
            },
            "required": ["major_premise", "minor_premise", "conclusion"]
        }
    }
}
```

### Tool Permission Handler

```python
def request_tool_permission(tool_name: str, parameters: dict) -> bool:
    print(f"\n🔧 Tool Call: {tool_name}")
    print("Parameters:")
    for key, value in parameters.items():
        print(f"  - {key.replace('_', ' ').title()}: {value}")
    
    while True:
        response = input("\nExecute tool? (y/n): ").strip().lower()
        if response in ['y', 'yes']: return True
        if response in ['n', 'no']: return False
        print("Please respond with 'y' or 'n'")
```

### Syllogism Evaluation Function

```python
def evaluate_syllogism(major_premise: str, minor_premise: str, conclusion: str) -> str:
    """Analyze syllogism validity and return JSON result."""
    # Implementation logic for analyzing logical structure
    result = {
        "valid": True|False,
        "form": "categorical|conditional|disjunctive", 
        "analysis": "Detailed explanation",
        "errors": ["List of logical fallacies if any"]
    }
    return json.dumps(result)
```

## 5. Usage Examples

### Command Line Usage

```bash
# Single question mode
python critical_thinking_chat.py --question "All politicians are corrupt"

# Interactive mode
python critical_thinking_chat.py --interactive

# With verbose logging
python critical_thinking_chat.py --interactive --verbose DEBUG
```

### Tool Calling Flow

```python
# User: "All politicians are corrupt. John is a politician. Therefore John is corrupt."

# 🔧 Tool Call: evaluate_syllogism
# Parameters:
#   - Major Premise: All politicians are corrupt
#   - Minor Premise: John is a politician  
#   - Conclusion: John is corrupt
# Execute tool? (y/n): y

# Tool Result: {"valid": false, "analysis": "Contains hasty generalization...", "errors": ["hasty_generalization"]}

# Assistant: "The analysis reveals logical issues with this argument. The major premise makes a sweeping generalization. What evidence supports the claim that ALL politicians are corrupt? Could there be exceptions?"
```

### Error Handling

```python
# Handle tool execution errors
try:
    result = evaluate_syllogism(**function_args)
except Exception as e:
    result = json.dumps({"error": f"Tool execution failed: {str(e)}"})

# Handle user declining tool permission
if not permission_granted:
    result = json.dumps({"declined": True, "message": "Continuing without tool analysis"})
```

## 6. Key Dependencies

- **Python 3.8+**
- **azure-ai-projects v1.0.0b12+** - Core Azure AI Foundry SDK
- **azure-identity** - DefaultAzureCredential authentication  
- **openai** - Chat completions via Azure OpenAI client
- **argparse** - Command line argument parsing
- **json** - Tool response handling
- **logging** - Configurable verbosity control

## 7. Validation Checklist

- [ ] Connects to Azure AI Foundry via AIProjectClient
- [ ] Challenges assumptions through Socratic questioning
- [ ] Requests user permission before tool execution
- [ ] Handles tool approval/decline gracefully
- [ ] Integrates syllogism analysis into conversation
- [ ] Supports both single-question and interactive modes
- [ ] Maintains conversation context across turns
- [ ] Provides clear error messages and clean exit
- [ ] Follows Python coding standards with type hints
- [ ] Implements quiet-by-default logging (ERROR level)
