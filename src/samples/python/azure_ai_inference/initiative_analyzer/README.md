# Initiative Analyzer

Analyzes CSV backlog items against organizational initiatives using Azure AI Foundry to generate markdown reports showing how backlog work supports strategic goals.

## Prerequisites

- Python 3.8+
- Azure AI Foundry project with deployed language model
- Azure authentication configured

## Installation

```bash
cd src/samples/python/azure_ai_inference/initiative_analyzer
pip install -r requirements.txt
```

## Configuration

Set environment variables:

- `PROJECT_ENDPOINT` (required): Azure AI Foundry project endpoint
- `MODEL_DEPLOYMENT_NAME` (optional): Model name (default: "gpt-4o")

Or create a `.env` file:

```env
PROJECT_ENDPOINT=https://your-project.eastus.api.azureml.ms
MODEL_DEPLOYMENT_NAME=gpt-4o
```

## Usage

```bash
python initiative_analyzer.py --backlog backlog.csv --initiatives initiatives.csv --output reports/
```

### Options

- `--confidence-threshold 70` - Minimum confidence for associations (default: 60)
- `--filter-title "pattern"` - Filter backlog items by regex pattern
- `--verbose DEBUG` - Enable debug logging

## Input Format

### Backlog CSV

Required columns: `category`, `title`, `goal`, `stream`

```csv
category,title,goal,stream
"User Experience","Simplify onboarding","Reduce onboarding time","Product Team"
```

### Initiatives CSV

Required columns: `area`, `title`, `details`, `description`, `kpi`, `current_state`, `solutions`

```csv
area,title,details,description,kpi,current_state,solutions
"Developer Excellence","Improve onboarding","Streamline dev onboarding","Comprehensive guide","Time to onboard","Low adoption","Bootcamp, workshops"
```

## Output

Generates markdown reports for each initiative with associated backlog items:

- Initiative overview and KPIs
- Associated backlog items with confidence scores
- Impact analysis and strategic recommendations

## Authentication

Uses `DefaultAzureCredential` - ensure you're logged in via:

- Azure CLI (`az login`)
- Visual Studio Code Azure extension
- Environment variables
- Managed Identity (when on Azure)
