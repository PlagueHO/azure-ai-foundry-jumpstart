---
title: Continuous Integration Workflow for Azure AI Foundry Jumpstart
version: 1.1
date_created: 2025-06-02
last_updated: 2025-06-02
owner: Azure AI Foundry Jumpstart DevOps Team
tags: [process, ci, github-actions, infrastructure, python, bicep]
---

# Introduction

This specification defines the structure, requirements, and validation criteria for the continuous integration (CI) workflow in the Azure AI Foundry Jumpstart solution. The CI workflow leverages GitHub Actions to ensure code quality, security, and operational excellence for both Bicep infrastructure-as-code and Python application components. It is designed for developers, DevOps engineers, and maintainers contributing to the solution.

## 1. Purpose & Scope

The purpose of this specification is to provide a clear, machine-readable definition of the CI workflow, including its triggers, required jobs, constraints, and validation criteria. The scope covers all automation that validates code and infrastructure changes on pull requests to the `main` branch and on manual workflow dispatches. The intended audience includes contributors to the codebase and DevOps maintainers. Assumptions: contributors are familiar with GitHub Actions and the repository structure.

## 2. Definitions

- **CI:** Continuous Integration
- **Bicep:** Domain-specific language for declarative Azure resource deployment
- **Lint:** Automated code analysis for errors and style
- **GitHub Actions:** GitHub-native automation platform for CI/CD
- **Reusable Workflow:** A workflow defined for reuse across jobs or repositories
- **App Names:** Logical names of Python applications or modules under test (e.g., `data_generator`, `create_ai_search_index`)

## 3. Requirements, Constraints & Guidelines

* Requirement 1: The workflow MUST trigger on all pull requests targeting the `main` branch and on manual invocation (`workflow_dispatch`).
* Requirement 2: The workflow MUST run with permissions to read repository contents and write checks and pull request statuses.
* Requirement 3: The workflow MUST lint and publish Bicep files using a reusable workflow (`lint-and-publish-bicep.yml`).
* Requirement 4: The workflow MUST lint and test all Python applications listed in the `app_names` input using a reusable workflow (`lint-and-test-python-apps.yml`).
* Constraint 1: The list of Python app names MUST be explicitly provided as a JSON array string in the `app_names` input.
* Constraint 2: Only changes to `infra/**`, `src/**`, or `tests/**` paths should trigger the workflow on pull requests.
* Guideline 1: All jobs SHOULD be defined as reusable workflows for maintainability and DRY (Don't Repeat Yourself) principles.
* Guideline 2: Use job-level `uses` to reference reusable workflows and pass required inputs explicitly.
* Pattern to follow: Use explicit, self-documenting job and input names for clarity and maintainability.

## 4. Interfaces & Data Contracts

| Interface/Step                | Type         | Description                                                      |
|-------------------------------|--------------|------------------------------------------------------------------|
| `pull_request` trigger        | Event        | Triggers on PRs to `main` for `infra/**`, `src/**`, `tests/**`   |
| `workflow_dispatch` trigger   | Event        | Allows manual workflow runs                                      |
| `lint-and-publish-bicep`      | Workflow Job | Lints and publishes Bicep files                                  |
| `lint-and-test-python-apps`   | Workflow Job | Lints and tests Python apps; receives `app_names` as JSON string |

**Example `app_names` input:**
```json
["data_generator","create_ai_search_index"]
```

**Example workflow structure:**
```yaml
on:
  pull_request:
    branches:
      - main
    paths:
      - infra/**
      - src/**
      - tests/**
  workflow_dispatch:

permissions:
  checks: write
  pull-requests: write
  contents: read

jobs:
  lint-and-publish-bicep:
    name: Lint and Publish Bicep
    uses: ./.github/workflows/lint-and-publish-bicep.yml

  lint-and-test-python-apps:
    name: Lint and Test Python Apps
    uses: ./.github/workflows/lint-and-test-python-apps.yml
    with:
      app_names: '["data_generator","create_ai_search_index"]'
```

## 5. Rationale & Context

The CI workflow enforces code quality, security, and infrastructure standards before merging changes to the main branch. Using reusable workflows ensures modularity, maintainability, and consistency. Explicit app name listing ensures only intended Python modules are tested, reducing noise and false positives. Path-based triggers optimize workflow runs and resource usage.

## 6. Examples & Edge Cases

```
# Example: Pull request triggers CI only for relevant paths
on:
  pull_request:
    branches:
      - main
    paths:
      - infra/**
      - src/**
      - tests/**

# Example: Manual trigger
on:
  workflow_dispatch:

# Example: Lint and test Python apps with explicit app_names
jobs:
  lint-and-test-python-apps:
    uses: ./.github/workflows/lint-and-test-python-apps.yml
    with:
      app_names: '["data_generator","create_ai_search_index"]'
```

## 7. Validation Criteria

- The workflow runs automatically on every pull request to `main` that modifies `infra/**`, `src/**`, or `tests/**`.
- The workflow can be triggered manually via the GitHub Actions UI.
- The Bicep linting and publishing job completes successfully or fails with actionable errors.
- The Python linting and testing job completes successfully for all listed apps or fails with actionable errors.
- The workflow status is reported back to the pull request.
- The workflow uses only reusable workflows for job definitions.

## 8. Related Specifications / Further Reading

- [process-continuous-delivery.md]
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Reusable Workflows in GitHub Actions](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
- [Bicep Documentation](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/)
