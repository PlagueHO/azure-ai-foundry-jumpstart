# Critical Thinking Chat Assistant

A Python application that provides an interactive conversational assistant designed to challenge user assumptions, promote critical thinking, and facilitate deeper analysis of topics through structured questioning techniques.

## Overview

This sample demonstrates how to use the Azure AI Inference SDK to create an intelligent conversational agent that:
- Challenges user assumptions through Socratic questioning
- Promotes critical thinking by asking probing questions  
- Facilitates deeper analysis of complex topics
- Provides alternative perspectives on user statements
- Guides users through structured problem-solving approaches

## Prerequisites

- Python 3.8 or later
- Azure AI Foundry project with a deployed language model (e.g., GPT-4, GPT-4o-mini)
- Access to Azure with appropriate authentication configured

## Installation

1. Navigate to the critical thinking chat directory:
   ```bash
   cd src/samples/python/azure_ai_inference/critical_thinking_chat
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Set the following environment variables:

- `PROJECT_ENDPOINT` (required): Your Azure AI Foundry project endpoint URL in the format `https://<project-name>.<region>.api.azureml.ms`
- `MODEL_DEPLOYMENT_NAME` (optional): Name of your deployed language model (defaults to "gpt-4o-mini")

You can also create a `.env` file in this directory:
```
PROJECT_ENDPOINT=https://your-project.eastus.api.azureml.ms
MODEL_DEPLOYMENT_NAME=gpt-4o-mini
```

## Authentication

This application uses `DefaultAzureCredential` for Azure authentication, which automatically selects the most appropriate credential source:
- Azure CLI login (`az login`)
- Managed Identity (when running on Azure)
- Visual Studio Code Azure Account extension
- Environment variables (AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID)

## Usage

### Interactive Mode
Start a conversation that maintains context across multiple exchanges:
```bash
python critical_thinking_chat.py --interactive
```

### Single Question Mode
Analyze a single statement or question:
```bash
python critical_thinking_chat.py --question "I think social media is bad for society"
```

### Interactive Mode with Initial Question
Start with a question and continue the conversation:
```bash
python critical_thinking_chat.py --question "Remote work is always better" --interactive
```

### Command Line Options

- `--question, -q`: Initial question/statement to analyze
- `--interactive, -i`: Enable interactive mode for extended conversations
- `--endpoint`: Override PROJECT_ENDPOINT environment variable
- `--model`: Override MODEL_DEPLOYMENT_NAME environment variable
- `--help`: Show help message

## Example Conversations

### Single Question Analysis
```
> python critical_thinking_chat.py --question "All politicians are corrupt"

=== CRITICAL THINKING ANALYSIS ===
Your statement: All politicians are corrupt
==================================================

Critical Thinking Assistant:
That's a strong generalization. Let's examine this more deeply. What specific evidence led you to conclude that ALL politicians are corrupt? Are there any politicians, either currently serving or historically, that you would consider honest? What would you say to someone who argues that corruption varies significantly across different political systems and cultures?

Also, how are you defining "corrupt" in this context? Sometimes people use this term broadly, but it can mean different things - from financial misconduct to simply making decisions we disagree with.
```

### Interactive Conversation
```
> python critical_thinking_chat.py --interactive

============================================================
           CRITICAL THINKING CHAT ASSISTANT
============================================================
I'm here to help you think more deeply about complex topics.
I'll challenge your assumptions and guide you through critical analysis.

Type 'quit', 'exit', or 'q' to end our conversation.
Press Ctrl+C at any time to exit cleanly.
============================================================

--------------------------------------------------

Your response or new statement: I think AI will replace all human jobs

Critical Thinking Assistant:
That's a significant prediction about the future of work. Let's break this down systematically. When you say "all human jobs," are you including every type of work - from caregivers and therapists to artists and leaders? What evidence are you basing this prediction on?

Consider this: What unique human capabilities might be difficult for AI to replicate? And what new types of jobs might emerge as AI develops, just as previous technological revolutions created jobs we couldn't imagine before?

What timeframe are you thinking about for this complete replacement?
```

## Critical Thinking Techniques

The assistant employs various techniques to promote deeper analysis:

1. **Socratic Questioning**: Asking probing questions to examine assumptions
2. **Evidence-Based Reasoning**: Requesting supporting evidence for claims
3. **Alternative Perspectives**: Presenting different viewpoints on topics
4. **Assumption Challenging**: Identifying and questioning underlying beliefs
5. **5 Whys Approach**: Drilling down to root causes and reasoning
6. **Devil's Advocate**: Respectfully challenging positions to strengthen arguments

## Features

- **Context Maintenance**: Conversation memory across multiple exchanges
- **Graceful Exit**: Support for 'quit', 'exit', 'q', or Ctrl+C
- **Error Handling**: Robust error handling with informative messages
- **Logging**: Structured logging for debugging and monitoring
- **Type Safety**: Comprehensive type hints and validation
- **Authentication**: Secure Azure authentication using best practices

## Code Quality

This implementation follows Python best practices and passes ruff linting checks:

```bash
# Run linting
python -m ruff check critical_thinking_chat.py

# Apply automatic fixes
python -m ruff check --fix critical_thinking_chat.py

# Format code
python -m ruff format critical_thinking_chat.py
```

## Troubleshooting

### Common Issues

1. **Authentication Failed**: Ensure you're logged into Azure CLI (`az login`) or have appropriate credentials configured
2. **Endpoint Not Found**: Verify your PROJECT_ENDPOINT is correct and the project exists
3. **Model Not Available**: Check that your MODEL_DEPLOYMENT_NAME matches a deployed model in your project
4. **Network Issues**: Ensure you have internet connectivity and can reach Azure endpoints

### Debug Logging
To enable debug logging, set the logging level in the Python script or use environment variables.

## Implementation Notes

- Uses Azure AI Inference SDK for direct model interaction
- Implements conversation memory with token overflow protection
- Follows Azure SDK security best practices
- Compatible with multiple AI model types (GPT-4, Claude, Llama, etc.)
- Supports both Azure AI Foundry and Azure OpenAI deployments

## License

This sample is provided as-is under the same license as the containing repository.
