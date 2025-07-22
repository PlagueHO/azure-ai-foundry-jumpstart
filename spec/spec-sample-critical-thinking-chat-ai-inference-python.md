---
title: Critical Thinking Chat Assistant - AI Implementation Spec
version: 3.1
tags: [python, azure-ai-projects, critical-thinking, tool-calling, syllogism, fallacy-detection, modular-tools]
---

# Critical Thinking Chat Assistant with Tool Calling

Interactive Python chat assistant using Azure AI Projects SDK with function tool calling for critical thinking enhancement, syllogism evaluation, and fallacy detection. Uses modular tools architecture for extensibility.

## Core Purpose

Create a conversational AI that challenges assumptions through Socratic questioning, provides alternative perspectives, and validates logical arguments using tool calling capabilities for syllogism evaluation and fallacy detection.

## Key Definitions

- **Azure AI Projects SDK**: `azure-ai-projects` package for Azure AI Foundry operations
- **PROJECT_ENDPOINT**: Azure AI Foundry project URL `https://<project-name>.<region>.api.azureml.ms`
- **Tool Calling**: OpenAI function calling for logical analysis (syllogism evaluation, fallacy detection)
- **Tools Folder**: Modular directory structure (`tools/`) for organizing analytical functions

## 3. Requirements

### Core Requirements

- **REQ-001**: Use `azure-ai-projects` SDK v1.0.0b12+ with AIProjectClient.inference.get_azure_openai_client()
- **REQ-002**: Support single-question and interactive conversation modes
- **REQ-003**: Authenticate using DefaultAzureCredential
- **REQ-004**: Accept PROJECT_ENDPOINT via environment or command-line
- **REQ-005**: Implement conversation memory for context retention
- **REQ-006**: Provide logical analysis tools using OpenAI function calling (syllogism evaluation, fallacy detection)
- **REQ-007**: Use modular tools architecture with `tools/` directory for extensibility

### Critical Thinking Behavior

- **CRT-001**: Challenge assumptions with clarifying questions
- **CRT-002**: Provide alternative perspectives without bias
- **CRT-003**: Guide evidence-based reasoning
- **CRT-004**: Use logical analysis tools for argument validation and fallacy identification

### Tool Calling Requirements

- **TOOL-001**: Request user permission before tool execution
- **TOOL-002**: Display tool name, purpose, and parameters clearly
- **TOOL-003**: Handle approve/decline responses gracefully
- **TOOL-004**: Continue conversation when tools are declined
- **TOOL-005**: Integrate tool results into critical thinking guidance
- **TOOL-006**: Import tools from modular `tools/` directory structure

### User Experience

- **UX-001**: Support 'quit'/'exit'/'q' commands
- **UX-002**: Handle Ctrl+C cleanly
- **UX-003**: Provide clear error messages
- **UX-004**: Display readable conversation flow

## Implementation Guide

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PROJECT_ENDPOINT` | Yes | None | Azure AI Foundry project endpoint |
| `MODEL_DEPLOYMENT_NAME` | No | "gpt-4o" | Tool-capable model name |
| `VERBOSE_LOGGING` | No | "ERROR" | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |

### Client Setup

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
project_client = AIProjectClient(endpoint=project_endpoint, credential=credential)
client = project_client.inference.get_azure_openai_client(api_version="2024-10-21")
```

### Modular Tools Structure

```
tools/
├── __init__.py
├── syllogism.py         # Syllogism evaluation logic
└── fallacy_detector.py  # Fallacy detection logic
```

Import tools from modular structure:
```python
from tools.syllogism import evaluate_syllogism
from tools.fallacy_detector import detect_fallacies
```

### System Prompt

```python
SYSTEM_PROMPT = """You are a Critical Thinking Assistant. Challenge assumptions through Socratic questioning, provide alternative perspectives, and guide evidence-based reasoning. When users present logical arguments, use logical analysis tools to evaluate validity and identify fallacies. Ask probing questions like: "What evidence supports this?", "What might someone who disagrees say?", "What assumptions are you making?"."""
```

### Tool Definitions

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

FALLACY_DETECTOR_TOOL = {
    "type": "function",
    "function": {
        "name": "detect_fallacies",
        "description": "Identify logical fallacies in argumentative text",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text containing argument to analyze for fallacies"}
            },
            "required": ["text"]
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

### Tool Implementation Functions

Tools are modular and located in respective files:

```python
# tools/syllogism.py
def evaluate_syllogism(major_premise: str, minor_premise: str, conclusion: str) -> str:
    """Analyze syllogism validity and return JSON result."""
    result = {
        "valid": True|False,
        "form": "categorical|conditional|disjunctive", 
        "analysis": "Detailed explanation",
        "errors": ["List of logical fallacies if any"]
    }
    return json.dumps(result)

# tools/fallacy_detector.py  
def detect_fallacies(text: str) -> str:
    """Identify logical fallacies in text and return JSON result."""
    result = {
        "fallacies_detected": ["ad_hominem", "straw_man", "false_dichotomy"],
        "analysis": "Explanation of identified fallacies",
        "confidence": 0.85,
        "suggestions": ["How to improve the argument"]
    }
    return json.dumps(result)
```

Import and use in main application:
```python
from tools.syllogism import evaluate_syllogism
from tools.fallacy_detector import detect_fallacies
```

## 4. Usage Examples

### Command Line Usage

```bash
# Interactive mode
python critical_thinking_chat.py --interactive

# Single question mode  
python critical_thinking_chat.py --question "All politicians are corrupt"

# With custom endpoint and model
python critical_thinking_chat.py --endpoint "https://project.region.api.azureml.ms" --model "gpt-4o-mini"

# With verbose logging
python critical_thinking_chat.py --interactive --verbose DEBUG
```

### Command Line Parameters

| Parameter | Short | Type | Description |
|-----------|-------|------|-------------|
| `--question` | `-q` | string | Initial question/statement to analyze |
| `--interactive` | `-i` | flag | Enable interactive mode for extended conversations |
| `--endpoint` | | string | Override PROJECT_ENDPOINT environment variable |
| `--model` | | string | Override MODEL_DEPLOYMENT_NAME environment variable |
| `--verbose` | `-v` | choice | Set logging verbosity (DEBUG, INFO, WARNING, ERROR, CRITICAL) |

### Tool Calling Examples

```bash
# User: "Politicians are all corrupt because they take money from lobbyists."

# 🔧 Tool Call: detect_fallacies  
# Parameters:
#   - Text: Politicians are all corrupt because they take money from lobbyists.
# Execute tool? (y/n): y

# Tool Result: {"fallacies_detected": ["hasty_generalization"], "analysis": "Sweeping claim about all politicians...", "confidence": 0.92}

# Assistant: "The analysis identified a hasty generalization fallacy. What evidence do you have that ALL politicians are corrupt? Are there any politicians who might be exceptions?"
```

```bash
# User: "All mammals are warm-blooded. Whales are mammals. Therefore, whales are warm-blooded."

# 🔧 Tool Call: evaluate_syllogism
# Parameters:
#   - Major Premise: All mammals are warm-blooded
#   - Minor Premise: Whales are mammals  
#   - Conclusion: Therefore, whales are warm-blooded
# Execute tool? (y/n): y

# Tool Result: {"valid": true, "form": "categorical", "analysis": "Valid categorical syllogism with proper structure", "errors": []}
```

## Key Dependencies

- **azure-ai-projects v1.0.0b12+** - Core Azure AI Foundry SDK
- **azure-identity** - DefaultAzureCredential authentication  
- **openai** - Chat completions via Azure OpenAI client

## Validation Checklist

- [ ] Connects to Azure AI Foundry via AIProjectClient
- [ ] Requests user permission before tool execution
- [ ] Handles tool approval/decline gracefully
- [ ] Integrates logical analysis into conversation
- [ ] Uses modular tools structure with `tools/` directory
- [ ] Tools can be imported and extended independently
