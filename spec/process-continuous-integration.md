# Specification: Continuous Integration Workflow for Azure AI Foundry Jumpstart

**Version:** 1.0  
**Last Updated:** 2025-06-01  
**Owner:** Azure AI Foundry Jumpstart DevOps Team

## 1. Purpose & Scope

This specification defines the requirements, constraints, and interfaces for the continuous integration (CI) workflow implemented via GitHub Actions in the Azure AI Foundry Jumpstart solution. The CI workflow is responsible for validating code quality, enforcing standards, and ensuring the integrity of Bicep infrastructure-as-code and Python application components on every pull request to the `main` branch. The intended audience includes developers, DevOps engineers, and maintainers of the solution.

## 2. Definitions

- **CI:** Continuous Integration
- **Bicep:** Domain-specific language (DSL) for deploying Azure resources declaratively
- **Lint:** Automated code analysis to detect errors, stylistic issues, or suspicious constructs
- **GitHub Actions:** Automation platform for CI/CD workflows in GitHub repositories
- **App Names:** Logical names of Python applications or modules under test (e.g., `data_generator`, `create_ai_search_index`)

## 3. Requirements, Constraints & Guidelines

* Requirement 1: The workflow must trigger on all pull requests targeting the `main` branch and on manual invocation (`workflow_dispatch`).
* Requirement 2: The workflow must run with permissions to read repository contents and write checks and pull request statuses.
* Requirement 3: The workflow must lint and publish Bicep files using a reusable workflow (`lint-and-publish-bicep.yml`).
* Requirement 4: The workflow must lint and test all Python applications listed in the `app_names` input using a reusable workflow (`lint-and-test-python-apps.yml`).
* Constraint 1: The list of Python app names must be explicitly provided as a JSON array string in the `app_names` input.
* Guideline 1: All jobs should be defined as reusable workflows for maintainability and DRY (Don't Repeat Yourself) principles.
* Pattern to follow: Use job-level `uses` to reference reusable workflows and pass required inputs explicitly.

## 4. Interfaces & Data Contracts

| Interface/Step                | Type         | Description                                                      |
|-------------------------------|--------------|------------------------------------------------------------------|
| `pull_request` trigger        | Event        | Triggers on PRs to `main`                                        |
| `workflow_dispatch` trigger   | Event        | Allows manual workflow runs                                      |
| `lint-and-publish-bicep`      | Workflow Job | Lints and publishes Bicep files                                  |
| `lint-and-test-python-apps`   | Workflow Job | Lints and tests Python apps; receives `app_names` as JSON string |

**Example `app_names` input:**
```json
["data_generator","create_ai_search_index"]
```

## 5. Rationale & Context

The CI workflow enforces code quality and infrastructure standards before merging changes to the main branch. By using reusable workflows, the process is modular, maintainable, and consistent across different components. Explicit app name listing ensures only intended Python modules are tested, reducing noise and false positives.

## 6. Examples & Edge Cases

```
# Example: Pull request triggers CI
on:
  pull_request:
    branches:
      - main

# Example: Manual trigger
on:
  workflow_dispatch:

# Example: Lint and test Python apps
jobs:
  lint-and-test-python-apps:
    uses: ./.github/workflows/lint-and-test-python-apps.yml
    with:
      app_names: '["data_generator","create_ai_search_index"]'
```

## 7. Validation Criteria

- The workflow runs automatically on every pull request to `main`.
- The workflow can be triggered manually via the GitHub Actions UI.
- The Bicep linting and publishing job completes successfully or fails with actionable errors.
- The Python linting and testing job completes successfully for all listed apps or fails with actionable errors.
- The workflow status is reported back to the pull request.

## 8. Related Specifications / Further Reading

- [process-continuous-delivery.md]  
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Reusable Workflows in GitHub Actions](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
- [Bicep Documentation](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/)
