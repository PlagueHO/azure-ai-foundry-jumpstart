# FOLDERS.md

This document describes the folder structure of the Azure AI Foundry Jumpstart Solution Accelerator repository. Each folder is organized to support modularity, clarity, and ease of navigation.

---

## Root Folders

- **.azure/**
  - Azure Developer CLI environment files and configuration (auto-generated).
- **.devcontainer/**
  - Configuration for development containers (e.g., VS Code Dev Containers).
- **.github/**
  - GitHub-specific files, including workflows, issue templates, and actions.
- **.vscode/**
  - Visual Studio Code workspace settings and configuration files.
- **docs/**
  - Project documentation, including:
    - `CONFIGURATION_OPTIONS.md`: Configuration options for deployment and customization.
    - **design/**: Architecture, overview, and technology documentation.
    - **diagrams/**: Architecture and solution diagrams (e.g., drawio files).
    - **images/**: Project-related images and graphics.
- **infra/**
  - Infrastructure as Code (IaC) assets for Azure deployment:
    - `main.bicep`, `main.bicepparam`: Main Bicep templates and parameters.
    - `bicepconfig.json`: Bicep configuration.
    - `abbreviations.json`: Abbreviations used in Bicep modules.
    - `sample-model-deployments.json`: List of model deployments to deploy (includes OpenAI and other AI models).
    - **core/**: Core Bicep modules (e.g., AI, security).
    - **types/**: Custom Bicep type definitions (e.g., for AI resources).
- **sample-data/**
  - Example datasets for testing and demonstration:
    - **retail-product/**: Sample product data in various formats (YAML, JSON, TXT).
    - **tech-support/**: Example tech support data (JSON, TXT).
- **scripts/**
  - Automation and utility scripts:
    - `upload_sample_data.ps1`, `upload_sample_data.sh`: Scripts to upload sample data.
    - **generators/**: Scripts for generating sample data.
    - **quickdeploy/**: Quick deployment scripts and helpers.
- **src/**
  - Source code for solution samples and reference implementations:
    - **samples/**: Example source code and sample projects.

---

## Root Files

- `azure.yaml`: Azure Developer CLI project configuration.
- `GitVersion.yml`: GitVersion configuration for versioning.
- `LICENSE`: License for the repository.
- `README.md`: Main project readme.

---

> **Note:** Some folders (e.g., `.git`, `.azure`) are auto-generated and should not be manually edited.
