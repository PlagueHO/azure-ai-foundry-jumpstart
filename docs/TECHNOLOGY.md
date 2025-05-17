# Technology Overview

This solution accelerator leverages a range of Azure services and technologies to deliver a secure, scalable, and well-architected Azure AI Foundry environment.

## Core Azure Services Deployed

- **Azure AI Foundry Hub & Projects**  
  Central workspace for managing AI resources, projects, and collaboration.

- **Azure AI Services (Cognitive Services / OpenAI)**  
  Provides access to Azure OpenAI and Cognitive Services for model deployment and inferencing.

- **Azure AI Search** *(Optional, but recommended)*  
  Enterprise-grade search service for AI-powered indexing and retrieval. Can be excluded from deployment if not required.

- **Azure Storage Account**  
  Secure storage for data, models, and sample datasets.

- **Azure Key Vault**  
  Securely manages secrets, keys, and certificates.

- **Azure Container Registry** *(Optional)*  
  Stores and manages container images for AI workloads. You may use an existing registry, deploy a new one, or skip entirely.

- **Azure Virtual Network (VNet) & Subnets**  
  Provides network isolation and secure communication between resources.

- **Private Endpoints & Private DNS Zones**  
  Ensures all services communicate privately within the VNet, supporting zero-trust architecture.

- **Azure Bastion (Optional)**  
  Secure RDP/SSH access to resources without exposing public IPs.

- **Azure Log Analytics Workspace**  
  Centralized logging and monitoring for all deployed resources.

- **Azure Application Insights**  
  Application performance monitoring and diagnostics.

## Infrastructure as Code

- **Bicep with Azure Verified Modules (AVM)**  
  All resources are provisioned using Bicep and AVM for modular, secure, and repeatable deployments.

## Security & Identity

- **Managed Identities**  
  Used for secure, passwordless authentication between Azure resources.

- **Role-Based Access Control (RBAC)**  
  Fine-grained access management for users and service principals.

---

This technology stack ensures the accelerator is secure, operationally excellent, and ready for enterprise AI workloads.
