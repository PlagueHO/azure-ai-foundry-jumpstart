# Specification: Continuous Delivery Workflow for Azure AI Foundry Jumpstart

**Version:** 1.0  
**Last Updated:** 2025-06-01  
**Owner:** Azure AI Foundry Jumpstart DevOps Team

## 1. Purpose & Scope

This specification defines the requirements, constraints, and interfaces for the continuous delivery (CD) workflow implemented via GitHub Actions in the Azure AI Foundry Jumpstart solution. The CD workflow automates the validation, deployment, and end-to-end (E2E) testing of infrastructure and application components on every push to the `main` branch, on version tags, and on manual invocation. The intended audience includes developers, DevOps engineers, and maintainers of the solution.

## 2. Definitions

- **CD:** Continuous Delivery
- **Bicep:** Domain-specific language (DSL) for deploying Azure resources declaratively
- **E2E:** End-to-End (testing)
- **GitHub Actions:** Automation platform for CI/CD workflows in GitHub repositories
- **Matrix Strategy:** A method to run jobs with different parameter combinations
- **Reusable Workflow:** A GitHub Actions workflow that can be invoked from other workflows using `uses:`

## 3. Requirements, Constraints & Guidelines

* Requirement 1: The workflow must trigger on pushes to the `main` branch, on tags matching `v*`, and on changes to `infra/**`, `src/**`, or `tests/**` paths.
* Requirement 2: The workflow must support manual invocation via `workflow_dispatch`.
* Requirement 3: The workflow must set build variables, lint and publish Bicep files, and validate Bicep templates for multiple versions (v1, v2) using a matrix strategy.
* Requirement 4: The workflow must run E2E tests for both isolated and public network configurations using a matrix strategy.
* Requirement 5: The E2E test workflow must provision infrastructure, run E2E tests, and then delete infrastructure, passing all required secrets and parameters.
* Constraint 1: All secrets (tenant ID, subscription ID, client ID) must be passed securely to reusable workflows.
* Constraint 2: The workflow must use job-level `uses` to reference reusable workflows and pass required inputs explicitly.
* Guideline 1: Use descriptive job names and maintain modularity by leveraging reusable workflows for each major step.
* Pattern to follow: Use matrix strategies for both Bicep validation and E2E test scenarios to ensure coverage of all deployment modes.

## 4. Interfaces & Data Contracts

| Interface/Step                | Type         | Description                                                      |
|-------------------------------|--------------|------------------------------------------------------------------|
| `push` trigger                | Event        | Triggers on push to `main`, tags, or specified paths             |
| `workflow_dispatch` trigger   | Event        | Allows manual workflow runs                                      |
| `set-build-variables`         | Workflow Job | Sets build variables for downstream jobs                         |
| `lint-and-publish-bicep`      | Workflow Job | Lints and publishes Bicep files                                  |
| `validate-bicep`              | Workflow Job | Validates Bicep templates for v1 and v2 using a matrix           |
| `e2e-test-v1`                 | Workflow Job | Runs E2E tests for isolated and public configs using a matrix    |

**Example matrix for E2E tests:**
```yaml
matrix:
  include:
    - name: isolated
      AZURE_NETWORK_ISOLATION: 'true'
      DEPLOY_SAMPLE_OPENAI_MODELS: 'true'
    - name: public
      AZURE_NETWORK_ISOLATION: 'false'
      DEPLOY_SAMPLE_OPENAI_MODELS: 'false'
```

## 5. Rationale & Context

The CD workflow ensures that all infrastructure and application changes are validated, deployed, and tested in a consistent, automated manner. Using matrix strategies and reusable workflows increases coverage, maintainability, and reliability, while reducing manual intervention and risk of human error.

## 6. Examples & Edge Cases

```
# Example: Push to main or tag triggers CD
on:
  push:
    branches:
      - main
    tags:
      - v*
    paths:
      - infra/**
      - src/**
      - tests/**

# Example: E2E test matrix
jobs:
  e2e-test-v1:
    strategy:
      matrix:
        include:
          - name: isolated
            AZURE_NETWORK_ISOLATION: 'true'
            DEPLOY_SAMPLE_OPENAI_MODELS: 'true'
          - name: public
            AZURE_NETWORK_ISOLATION: 'false'
            DEPLOY_SAMPLE_OPENAI_MODELS: 'false'
```

## 7. Validation Criteria

- The workflow runs automatically on every push to `main`, on version tags, and on changes to infrastructure, source, or test files.
- The workflow can be triggered manually via the GitHub Actions UI.
- All jobs complete successfully or fail with actionable errors.
- E2E tests are executed for both isolated and public network configurations.
- The workflow status is reported back to the repository.

## 8. Related Specifications / Further Reading

- [process-continuous-integration.md]  
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Reusable Workflows in GitHub Actions](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
- [Bicep Documentation](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/)
