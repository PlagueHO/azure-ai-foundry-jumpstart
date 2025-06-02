---
title: Continuous Delivery Workflow for Azure AI Foundry Jumpstart
version: 1.1
date_created: 2025-06-02
last_updated: 2025-06-02
owner: Azure AI Foundry Jumpstart DevOps Team
tags: [process, continuous-delivery, github-actions, azure, infrastructure]
---

# Introduction

This specification defines the structure, requirements, constraints, and interfaces for the Continuous Delivery (CD) workflow in the Azure AI Foundry Jumpstart solution. The workflow is implemented using GitHub Actions and leverages modular, reusable workflows to automate validation, deployment, and end-to-end (E2E) testing of infrastructure and application components. The workflow is triggered on code changes, version tags, and manual invocations, ensuring robust, repeatable, and secure delivery to Azure environments.

## 1. Purpose & Scope

The purpose of this specification is to provide a clear, machine-readable definition of the CD workflow for Azure AI Foundry Jumpstart. It covers:

- Automated validation and deployment of Bicep-based infrastructure as code (IaC)
- End-to-end testing of deployed environments
- Secure handling of secrets and environment variables
- Use of matrix strategies and modular, reusable workflows

Intended audience: Developers, DevOps engineers, maintainers, and automated agents consuming this specification for workflow generation or validation.

## 2. Definitions

| Term                        | Definition                                                                 |
|-----------------------------|----------------------------------------------------------------------------|
| CD                          | Continuous Delivery                                                        |
| Bicep                       | Domain-specific language for declarative Azure resource deployment          |
| E2E                         | End-to-End (testing)                                                       |
| GitHub Actions              | Automation platform for CI/CD workflows in GitHub repositories             |
| Matrix Strategy             | Method to run jobs with different parameter combinations                   |
| Reusable Workflow           | GitHub Actions workflow invoked from other workflows using `uses:`         |
| Job-level `uses`            | Pattern for referencing reusable workflows at the job level                |
| Secret                      | Sensitive value (e.g., credentials) passed securely to workflows           |
| Environment Variable        | Key-value pair used to configure workflow jobs                             |

## 3. Requirements, Constraints & Guidelines

* **Requirement 1:** The workflow MUST trigger on:
  * Pushes to the `main` branch
  * Tags matching `v*`
  * Changes to any file under `infra/**`, `src/**`, or `tests/**`
* **Requirement 2:** The workflow MUST support manual invocation via `workflow_dispatch`.
* **Requirement 3:** The workflow MUST set build variables, lint and publish Bicep files, and validate Bicep templates for multiple versions (v1, v2) using a matrix strategy.
* **Requirement 4:** The workflow MUST run E2E tests for both isolated and public network configurations using a matrix strategy.
* **Requirement 5:** The E2E test workflow MUST provision infrastructure, run E2E tests, and then delete infrastructure, passing all required secrets and parameters.
* **Constraint 1:** All secrets (tenant ID, subscription ID, client ID) MUST be passed securely to reusable workflows using the `secrets` block.
* **Constraint 2:** The workflow MUST use job-level `uses` to reference reusable workflows and pass required inputs explicitly.
* **Constraint 3:** The workflow MUST NOT expose secrets in logs or outputs.
* **Guideline 1:** Use descriptive job names and maintain modularity by leveraging reusable workflows for each major step.
* **Guideline 2:** Use matrix strategies for both Bicep validation and E2E test scenarios to ensure coverage of all deployment modes.
* **Pattern to follow:** Reference reusable workflows via relative paths and pass all required `with` and `secrets` inputs explicitly.

## 4. Interfaces & Data Contracts

| Interface/Step                | Type         | Description                                                      |
|-------------------------------|--------------|------------------------------------------------------------------|
| `push` trigger                | Event        | Triggers on push to `main`, tags, or specified paths             |
| `workflow_dispatch` trigger   | Event        | Allows manual workflow runs                                      |
| `set-build-variables`         | Workflow Job | Sets build variables for downstream jobs (reusable workflow)     |
| `lint-and-publish-bicep`      | Workflow Job | Lints and publishes Bicep files (reusable workflow)              |
| `validate-bicep`              | Workflow Job | Validates Bicep templates for v1 and v2 using a matrix           |
| `e2e-test-v1`                 | Workflow Job | Runs E2E tests for isolated and public configs using a matrix    |

**Example: Matrix for Bicep Validation**
```yaml
strategy:
  matrix:
    include:
      - name: v1
        BICEP_VERSION: v1
      - name: v2
        BICEP_VERSION: v2
```

**Example: Matrix for E2E Tests**
```yaml
strategy:
  max-parallel: 1
  matrix:
    include:
      - name: public
        AZURE_NETWORK_ISOLATION: 'false'
        DEPLOY_SAMPLE_OPENAI_MODELS: 'true'
      - name: isolated
        AZURE_NETWORK_ISOLATION: 'true'
        DEPLOY_SAMPLE_OPENAI_MODELS: 'false'
```

## 5. Rationale & Context

The CD workflow is designed to ensure that all infrastructure and application changes are validated, deployed, and tested in a consistent, automated, and secure manner. Modular, reusable workflows and matrix strategies maximize coverage, maintainability, and reliability, while reducing manual intervention and risk of human error. Secure handling of secrets and explicit parameter passing are critical for compliance and operational excellence.

## 6. Examples & Edge Cases

```yaml
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
      max-parallel: 1
      matrix:
        include:
          - name: public
            AZURE_NETWORK_ISOLATION: 'false'
            DEPLOY_SAMPLE_OPENAI_MODELS: 'true'
          - name: isolated
            AZURE_NETWORK_ISOLATION: 'true'
            DEPLOY_SAMPLE_OPENAI_MODELS: 'false'
```

## 7. Validation Criteria

- The workflow runs automatically on every push to `main`, on version tags, and on changes to infrastructure, source, or test files.
- The workflow can be triggered manually via the GitHub Actions UI.
- All jobs complete successfully or fail with actionable errors.
- E2E tests are executed for both isolated and public network configurations.
- The workflow status is reported back to the repository.
- All secrets are handled securely and are not exposed in logs or outputs.

## 8. Related Specifications / Further Reading

- [process-continuous-integration.md]
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Reusable Workflows in GitHub Actions](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
- [Bicep Documentation](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/)
