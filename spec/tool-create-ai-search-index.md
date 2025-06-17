---
title: Python CLI Tool for Azure AI Search Index Creation
version: 2.0
date_created: 2025-06-02
last_updated: 2025-06-02
owner: Azure AI Foundry Jumpstart Team
tags: [infrastructure, tool, ai-search, cli, python]
---

# Introduction

This specification defines a Python CLI tool for deploying and managing Azure AI Search indexes, data sources, and skillsets, optimized for RAG (Retrieval-Augmented Generation) scenarios. The tool automates the creation, update, and teardown of Azure AI Search pipelines using Azure SDKs and best practices, and is intended for data engineers, AI developers, and DevOps teams.

## 1. Purpose & Scope

The purpose of this specification is to provide requirements, constraints, and interface definitions for the `create_ai_search_index` CLI tool. The tool enables automated, repeatable, and secure deployment of Azure AI Search resources, including index schema, data source connections, skillsets, and indexers, with support for Azure OpenAI vectorization. The scope includes:

- Building and updating Azure AI Search indexes for RAG scenarios
- Managing data source connections to Azure Blob Storage
- Configuring skillsets for chunking and enrichment
- Running and monitoring indexers
- Supporting idempotent and teardown operations

Intended audience: Data engineers, AI/ML developers, DevOps engineers deploying or managing Azure AI Search solutions.

## 2. Definitions

- **CLI**: Command-Line Interface
- **Azure AI Search**: Microsoft Azure's cloud search service for indexing and querying data.
- **Skillset**: A collection of skills (built-in or custom) that enrich data during indexing.
- **Indexer**: A component that extracts data from a data source and populates the search index.
- **Index**: A searchable data structure in Azure AI Search.
- **Schema**: The structure defining fields and types in the search index.
- **RAG**: Retrieval-Augmented Generation, an AI pattern combining search and generative models.
- **Vectorizer**: A component that generates vector embeddings for search.
- **Blob Container**: Azure Storage container holding documents to be indexed.

## 3. Requirements, Constraints & Guidelines

### Requirements

- **REQ-001**: The tool must be implemented in Python 3.13+ and follow PEP8 style guidelines
- **REQ-002**: The CLI must accept parameters for storage account, storage key or connection string, storage container, search service, index name, Azure OpenAI endpoint, embedding model, deployment, and dimension
- **REQ-003**: The tool must use Azure SDKs to create and configure indexes, indexers, skillsets, and data sources
- **REQ-004**: The tool must validate input parameters and provide clear, actionable error messages
- **REQ-005**: The tool must log all operations and errors to stdout with timestamps
- **REQ-006**: The tool must support idempotent operations and optional teardown of existing resources
- **REQ-007**: The tool must support configuration of chunking and vectorization for RAG scenarios
- **REQ-008**: The tool must exit with code 0 on success, non-zero on error
- **REQ-009**: The tool must support both API key and DefaultAzureCredential authentication
- **REQ-010**: The tool must be executable as a Python module using `python -m` syntax
- **REQ-011**: The tool must include comprehensive unit tests using pytest that achieve adequate code coverage
- **REQ-012**: The tool must pass Ruff linting checks without errors or warnings
- **REQ-013**: The tool must pass pylint code quality checks without errors
- **REQ-014**: The tool must pass Mypy type checking validation without errors

### Security Requirements

- **SEC-001**: The tool must not log or expose sensitive information (e.g., keys, connection strings)
- **SEC-002**: All authentication credentials must be handled securely and not exposed in error messages
- **SEC-003**: The tool must support Azure DefaultAzureCredential for secure authentication

### Constraints

- **CON-001**: Only public, stable Azure SDK APIs may be used
- **CON-002**: No sensitive information should be logged or exposed in error messages
- **CON-003**: The tool must be compatible with Azure AI Search service limitations and quotas

### Guidelines

- **GUD-001**: Use type hints and docstrings for all public functions and classes
- **GUD-002**: Use self-explanatory variable and parameter names
- **GUD-003**: Follow Python logging best practices with appropriate log levels
- **GUD-004**: Implement proper exception handling with meaningful error messages

### Patterns

- **PAT-001**: Use the `argparse` library for CLI argument parsing
- **PAT-002**: Implement the CLI as a main module with proper entry point structure
- **PAT-003**: Use Azure SDK client patterns for resource management

## 4. Interfaces & Data Contracts

### CLI Arguments

| Argument                              | Type   | Required | Description |
|----------------------------------------|--------|----------|-------------|
| --storage-account                      | str    | Cond.    | Azure Storage account name. Required if not using connection string. |
| --storage-account-key                  | str    | Cond.    | Azure Storage account key. Required if not using connection string. |
| --storage-account-connection-string    | str    | Cond.    | Azure Storage account connection string. If provided, overrides account/key. |
| --storage-container                    | str    | Yes      | Blob container with documents. |
| --search-service                       | str    | Yes      | Azure AI Search service name. |
| --index-name                           | str    | Yes      | Name of the search index to create or update. |
| --azure-openai-endpoint                | str    | Yes      | Azure OpenAI endpoint URL. |
| --embedding-model                      | str    | No       | Azure OpenAI embedding model name. Default: 'text-embedding-ada-002'. |
| --embedding-deployment                 | str    | No       | Azure OpenAI embedding deployment name. Default: 'text-embedding-ada-002'. |
| --embedding-dimension                  | int    | No       | Embedding vector dimension. Default: 1536. |
| --delete-existing                      | flag   | No       | Delete and re-create pipeline resources if they exist. |

### Example CLI Usage

```bash
create_ai_search_index --storage-account mystorage --storage-account-key $KEY --storage-container docs \
    --search-service mysearch --index-name myindex --azure-openai-endpoint https://myopenai.openai.azure.com/
```

## 5. Rationale & Context

- The tool automates secure, repeatable deployment of Azure AI Search pipelines for RAG and vector search scenarios.
- Idempotency and teardown support enable safe CI/CD and iterative development.
- Explicit parameter validation and logging improve operational excellence and troubleshooting.
- Using Azure SDKs and DefaultAzureCredential supports secure, flexible authentication.
- Chunking and vectorization are required for modern AI search and RAG workloads.

## 6. Examples & Edge Cases

```bash
# Basic usage
python -m create_ai_search_index.cli --storage-account mystorage --storage-account-key $KEY --storage-container docs \
    --search-service mysearch --index-name myindex --azure-openai-endpoint https://myopenai.openai.azure.com/

# Using a connection string
python -m create_ai_search_index.cli --storage-account-connection-string "$CONN_STR" --storage-container docs \
    --search-service mysearch --index-name myindex --azure-openai-endpoint https://myopenai.openai.azure.com/

# Edge case: Missing required storage key
python -m create_ai_search_index.cli --storage-account mystorage --storage-container docs \
    --search-service mysearch --index-name myindex --azure-openai-endpoint https://myopenai.openai.azure.com/
# Should return a clear error message and exit with non-zero status

# Edge case: Invalid Azure OpenAI endpoint
python -m create_ai_search_index.cli --storage-account mystorage --storage-account-key $KEY --storage-container docs \
    --search-service mysearch --index-name myindex --azure-openai-endpoint not-a-url
# Should return a clear error message and exit with non-zero status
```

## 7. Validation Criteria

- The tool must exit with status code 0 on success, non-zero on error.
- All required arguments must be validated; missing/invalid arguments must result in a clear error.
- The created index, indexer, and skillset must match the provided configuration.
- No duplicate indexes or documents should be created on repeated runs.
- Logs must include timestamps and operation details.
- No sensitive information is logged or exposed.
- All unit tests must pass with `pytest tests/`
- Ruff linting must pass with `python -m ruff check src/`
- Pylint code quality checks must pass with `pylint src/`
- Mypy type checking must pass with `mypy src/`

## 8. Related Specifications / Further Reading

- [Azure AI Search Documentation](https://learn.microsoft.com/en-us/azure/search/)
- [Azure Cognitive Skills Documentation](https://learn.microsoft.com/en-us/azure/search/cognitive-search-skillset)
- [PEP8 Python Style Guide](https://peps.python.org/pep-0008/)
