# Backlog Analyzer

A Python application that takes a CSV list of backlog items and analyzes them using Azure AI Foundry's language models. It will look at each backlog item one-by-one and attempt to categorize it against existing initiatives, providing insights and deeper analysis on the impact of the backlog items.

## Overview

This sample demonstrates how to use the Azure AI Projects SDK to create an intelligent conversational agent that:

- Analyzes backlog items using a language model
- Categorizes items against existing initiatives
- Provides insights and deeper analysis on the impact of backlog items
- Maintains conversation context across multiple exchanges
- Supports interactive and single question modes
- Uses function tool calling to associate backlog items with an existing set of initiatives

## Prerequisites

- Python 3.8 or later
- Azure AI Foundry project with a deployed language model (e.g., gpt-4.1, gpt-4.1-mini)
- Access to Azure with appropriate authentication configured

## Installation

1. Navigate to the critical thinking chat directory:

  ```bash
  cd src/samples/python/azure_ai_inference/backlog_analyzer
  ```

1. Install the required dependencies:

  ```bash
  pip install -r requirements.txt
  ```

## Configuration

Set the following environment variables:

- `PROJECT_ENDPOINT` (required): Your Azure AI Foundry project endpoint URL in the format `https://<project-name>.<region>.api.azureml.ms`
- `MODEL_DEPLOYMENT_NAME` (optional): Name of your deployed language model (defaults to "gpt-4o")
- `VERBOSE_LOGGING` (optional): Logging verbosity level (defaults to "ERROR")

You can also create a `.env` file in this directory:

```env
PROJECT_ENDPOINT=https://your-project.eastus.api.azureml.ms
MODEL_DEPLOYMENT_NAME=gpt-4o
VERBOSE_LOGGING=ERROR
```

## Authentication

This application uses `DefaultAzureCredential` for Azure authentication, which automatically selects the most appropriate credential source:

- Azure CLI login (`az login`)
- Managed Identity (when running on Azure)
- Visual Studio Code Azure Account extension
- Environment variables (AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID)

## Backlog Analysis Workflow

The backlog analyzer uses a sophisticated AI-driven workflow to evaluate each backlog item against available initiatives and provide enriched analysis. Here's the detailed process:

### 1. Data Preparation Phase

- **Load Backlog Items**: Parse the CSV file containing backlog items with their categories, goals, streams, and timeline information
- **Load Initiatives**: Parse the CSV file containing available initiatives with their areas, details, KPIs, and current states
- **Data Validation**: Verify required columns exist and data types are correct

### 2. Initiative Matching Analysis

For each backlog item, the AI performs:

#### 2.1 Semantic Analysis

- **Goal Alignment**: Compare the backlog item's goal with initiative descriptions and solutions
- **Category Mapping**: Analyze if the backlog category aligns with initiative areas
- **Stream Compatibility**: Evaluate if the responsible stream has capacity/expertise for the initiative

#### 2.2 Impact Assessment

- **Direct Impact**: Identify initiatives that would be directly advanced by completing the backlog item
- **Indirect Impact**: Discover initiatives that might benefit tangentially from the backlog item
- **Negative Impact**: Assess if the backlog item might conflict with or detract from any initiatives

#### 2.3 Confidence Scoring

- **Category Confidence**: 0-100 score indicating how well the backlog item fits its assigned category
- **Initiative Confidence**: 0-100 score indicating the strength of the match with selected initiatives
- **Reasoning**: Detailed explanation of the matching logic and confidence factors

### 3. Enrichment Process

The AI enhances each backlog item with:

#### 3.1 Initiative Association

- **Primary Initiative**: Best matching initiative (if any) with detailed reasoning
- **Secondary Initiatives**: Additional initiatives that may benefit (with lower confidence scores)
- **Initiative Details**: Full context about matched initiatives including KPIs and current state

#### 3.2 Strategic Analysis

- **Impact Assessment**: Quantitative and qualitative impact analysis on matched initiatives
- **Timeline Alignment**: Evaluation of how the backlog item's timeline aligns with initiative goals
- **Resource Implications**: Analysis of required resources and potential conflicts

#### 3.3 Recommendation Generation

- **Priority Suggestions**: AI-generated priority recommendations based on initiative alignment
- **Implementation Insights**: Suggestions for optimal implementation approach
- **Risk Assessment**: Identification of potential risks or blockers

### 4. Output Generation

The enriched analysis includes:

- **Original backlog data**: Preserved category, title, goal, stream, and timeline information
- **Matched initiatives**: Primary and secondary initiative associations
- **Confidence scores**: Quantitative confidence metrics for category and initiative matches
- **Detailed analysis**: Comprehensive AI-generated insights and recommendations
- **Impact summary**: Clear description of how the backlog item advances organizational initiatives

### 5. Quality Assurance

- **Consistency Checks**: Verify that confidence scores align with reasoning
- **Completeness Validation**: Ensure all required output fields are populated
- **Error Handling**: Graceful handling of parsing errors or missing data

This workflow ensures that each backlog item is thoroughly analyzed against the strategic context provided by the initiatives, resulting in data-driven insights that support better prioritization and resource allocation decisions.

## Usage

## Input

### Backlog CSV Format

- `category`: The high-level category of the backlog item
- `initiative`: An existing initiative for the backlog item (optional)
- `title`: Title of the backlog item
- `goal`: The goal or expected outcome of the backlog item
- `stream`: The stream or team responsible for the backlog item
- Optional columns for each half-year (e.g., `25 H1`, `25 H2`, etc.) to indicate when the item is planned for implementation

#### Example Backlog CSV

```csv
category,initiative,title,goal,stream,25 H1,25 H2,26 H1,26 H2,27 H1,27 H2,28+
"User Experience","Improve onboarding","Simplify onboarding process","Reduce time to onboard new users","Product Team",1,1,0,0,0,0,0
```

### Initiatives CSV Format

- `area`: The area of the initiative (e.g., "Developer Excellence")
- `title`: Title of the initiative
- `details`: Detailed description of the initiative
- `description`: Additional information about the initiative
- `kpi`: Key Performance Indicators for the initiative
- `current_state`: Current status of the initiative
- `solutions`: Proposed solutions for the initiative

#### Example Initiatives CSV

```csv
area,title,details,description,kpi,current_state,solutions
"Developer Excellence","Improve developer onboarding","Streamline the onboarding process for new developers using GitHub Copilot","Create a comprehensive onboarding guide for GitHub Copilot","Time to onboard new developers","GitHub Copilot available, but low adoption","GitHub Copilot bootcamp, workshops, and documentation"
```

### Output

The output will be a CSV file with enriched backlog items, including:

- `category`: The high-level category of the backlog item
- `initiative`: The matched initiative (if any)
- `title`: Title of the backlog item
- `goal`: The goal or expected outcome of the backlog item
- `stream`: The stream or team responsible for the backlog item
- `25 H1`, `25 H2`, etc.: Implementation plans for each half-year
- `impact`: The impact of the initiative on the backlog item
- `analysis`: Insights and deeper analysis provided by the language model
- `category_confidence`: Confidence score for the category match
- `initiative_confidence`: Confidence score for the initiative match
- `initiative_details`: Details about the matched initiative (if any)

### Enrichment

Enrich a backlog CSV file with insights and categorization:

```bash
python backlog_analyzer.py --enrich --backlog backlog.csv --initiatives initiatives.csv --output enriched_backlog.csv
```

#### Filtering Backlog Items by Title

You can filter which backlog items to process using a regex pattern with the `--filter-title` parameter:

```bash
# Process only items with "onboard" in the title (case-insensitive)
python backlog_analyzer.py --enrich --backlog backlog.csv --initiatives initiatives.csv --output filtered_backlog.csv --filter-title ".*onboard.*"

# Process only items starting with "Mobile"
python backlog_analyzer.py --enrich --backlog backlog.csv --initiatives initiatives.csv --output mobile_backlog.csv --filter-title "^Mobile.*"

# Process items ending with "security"
python backlog_analyzer.py --enrich --backlog backlog.csv --initiatives initiatives.csv --output security_backlog.csv --filter-title ".*security$"
```

**Filter Examples:**
- `.*onboard.*` - Matches any title containing "onboard" (case-insensitive)
- `^Mobile.*` - Matches titles starting with "Mobile"
- `.*security$` - Matches titles ending with "security"
- `(API|integration)` - Matches titles containing either "API" or "integration"
- `Setup.*automation` - Matches titles starting with "Setup" and containing "automation"

The filter uses Python's `re` module with case-insensitive matching. Invalid regex patterns will show a clear error message.

## Code Quality

This implementation follows Python best practices and passes ruff linting checks:

```bash
# Run linting
python -m ruff check backlog_analyzer.py

# Apply automatic fixes
python -m ruff check --fix backlog_analyzer.py

# Format code
python -m ruff format backlog_analyzer.py
```

## Troubleshooting

### Common Issues

1. **Authentication Failed**: Ensure you're logged into Azure CLI (`az login`) or have appropriate credentials configured
2. **Endpoint Not Found**: Verify your PROJECT_ENDPOINT is correct and the project exists
3. **Model Not Available**: Check that your MODEL_DEPLOYMENT_NAME matches a deployed model in your project
4. **Network Issues**: Ensure you have internet connectivity and can reach Azure endpoints

### Debug Logging

To enable debug logging, use the `--verbose` command-line option or set the `VERBOSE_LOGGING` environment variable:

```bash
# Command line option
python backlog_analyzer.py --enrich --backlog backlog.csv --initiatives initiatives.csv --output enriched_backlog.csv --verbose DEBUG

# Environment variable
export VERBOSE_LOGGING=DEBUG  # Linux/Mac
$env:VERBOSE_LOGGING="DEBUG"  # Windows PowerShell
```

Valid logging levels: DEBUG, INFO, WARNING, ERROR, CRITICAL (default: ERROR)

## Dependencies

This implementation requires the following key dependencies:

- **Python 3.8+**
- **azure-ai-projects v1.0.0b12+** - Core Azure AI Foundry SDK
- **azure-identity** - DefaultAzureCredential authentication
- **openai** - Chat completions via Azure OpenAI client
- **argparse** - Command line argument parsing
- **json** - Tool response handling
- **logging** - Configurable verbosity control

## Implementation Notes

- Uses Azure AI Projects SDK with AIProjectClient.inference.get_azure_openai_client()
- Implements modular tools architecture with separate modules for logical analysis functions
- Implements function tool calling for syllogism evaluation and fallacy detection with user permission system
- Implements conversation memory with token overflow protection
- Follows Azure SDK security best practices
- Compatible with tool-capable AI models (GPT-4, GPT-4o, etc.)
- Supports Azure AI Foundry project deployments
- Quiet-by-default logging (ERROR level) with configurable verbosity
- Extensible design allows easy addition of new analytical tools

## License

This sample is provided as-is under the same license as the containing repository.
