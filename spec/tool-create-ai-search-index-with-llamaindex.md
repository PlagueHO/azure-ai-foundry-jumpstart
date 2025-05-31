# Specification: Python CLI Tool for Azure AI Search Index Creation with LlamaIndex

**Version:** 1.0  
**Last Updated:** 2025-05-21  
**Owner:** Azure AI Foundry Jumpstart Team

## 1. Purpose & Scope

This specification defines the requirements, constraints, and interfaces for a Python CLI tool named `create_ai_search_index`. The tool is responsible for building an Azure AI Search index using the LlamaIndex library. It is intended for data engineers, AI developers, and DevOps teams deploying or managing Azure AI Search solutions. The tool will reside in the `src/create_ai_search_index` directory.

## 2. Definitions

- **CLI**: Command-Line Interface
- **Azure AI Search**: A cloud search service provided by Microsoft Azure for indexing and querying data.
- **LlamaIndex**: An open-source library for building and querying search indexes, supporting integration with large language models (LLMs).
- **Index**: A searchable data structure in Azure AI Search.
- **Schema**: The structure defining fields and types in the search index.
- **Document**: A data record to be indexed.

## 3. Requirements, Constraints & Guidelines

* Requirement 1: The tool must be implemented in Python 3.13 or later.
* Requirement 2: The CLI must accept parameters for Azure Search endpoint, API key, index name, and input data location.
* Requirement 3: The tool must use LlamaIndex for index creation and data ingestion.
* Requirement 4: The tool must validate input parameters and provide clear error messages.
* Requirement 5: The tool must log all operations and errors to stdout and optionally to a log file.
* Requirement 6: The tool must support both JSON and CSV input data formats.
* Requirement 7: The tool must be idempotent—re-running with the same parameters should not create duplicate indexes or documents.
* Requirement 8: The tool must support dry-run mode for validation without making changes.
* Constraint 1: Only public, stable APIs of Azure AI Search and LlamaIndex may be used.
* Constraint 2: No sensitive information (e.g., API keys) should be logged or exposed in error messages.
* Guideline 1: Follow PEP8 and project Python style guidelines.
* Guideline 2: Use type hints and docstrings for all public functions.
* Pattern to follow: Use the `argparse` library for CLI argument parsing.

## 4. Interfaces & Data Contracts

### CLI Arguments

| Argument           | Type   | Required | Description                                 |
|--------------------|--------|----------|---------------------------------------------|
| --endpoint         | str    | Yes      | Azure AI Search endpoint URL                 |
| --api-key          | str    | Yes      | Azure AI Search API key                      |
| --index-name       | str    | Yes      | Name of the search index to create/use       |
| --input            | str    | Yes      | Path to input data file (JSON or CSV)        |
| --log-file         | str    | No       | Path to optional log file                    |
| --dry-run          | flag   | No       | Validate only, do not create index           |

### Example Data Schema (JSON)
```json
{
  "id": "string",
  "title": "string",
  "content": "string",
  "tags": ["string"]
}
```

## 5. Rationale & Context

- Using LlamaIndex enables advanced indexing and semantic search capabilities, leveraging LLMs for improved search relevance.
- Idempotency ensures safe repeated executions in CI/CD pipelines.
- Supporting both JSON and CSV formats increases flexibility for data ingestion.
- Explicit parameter validation and logging improve operational excellence and troubleshooting.

## 6. Examples & Edge Cases

```bash
# Basic usage
python -m create_ai_search_index.cli --endpoint https://mysearch.search.windows.net --api-key $API_KEY --index-name my-index --input data.json

# Dry-run validation
python -m create_ai_search_index.cli --endpoint https://mysearch.search.windows.net --api-key $API_KEY --index-name my-index --input data.csv --dry-run

# Edge case: Input file missing required fields
# Should return a clear error message and exit with non-zero status
```

## 7. Validation Criteria

- The tool must exit with status code 0 on success, non-zero on error.
- All required arguments must be validated and missing/invalid arguments must result in a clear error.
- The created index must match the schema of the input data.
- No duplicate indexes or documents should be created on repeated runs.
- Logs must include timestamps and operation details.

## 8. Related Specifications / Further Reading

- [Azure AI Search Documentation](https://learn.microsoft.com/en-us/azure/search/)
- [LlamaIndex Documentation](https://docs.llamaindex.ai/)
- [PEP8 Python Style Guide](https://peps.python.org/pep-0008/)
