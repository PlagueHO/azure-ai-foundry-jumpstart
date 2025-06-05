---
title: Sample Data Deployment Specification
version: 1.0
date_created: 2025-06-05
last_updated: 2025-06-05
owner: Azure AI Foundry Jumpstart Team
tags: [infrastructure, storage, sample-data, bicep, azure-storage]
---

# Introduction

This specification defines the requirements for deploying a dedicated Azure Storage Account for sample data in the Azure AI Foundry Jumpstart solution accelerator, separate from the foundry operational storage account and uploading sample datasets.

## 1. Purpose & Scope

This specification defines the infrastructure requirements, configuration options, and deployment behavior for a dedicated sample data storage account that provides separation of concerns between Azure AI Foundry operational data and sample datasets.

**Intended Audience:** Infrastructure developers, DevOps engineers, and solution architects implementing the Azure AI Foundry Jumpstart solution accelerator.

**Assumptions:**

- Azure Verified Modules (AVM) are used for all storage account deployments
- The solution follows Azure Well-Architected Framework principles
- Bicep is used as the Infrastructure as Code language

## 2. Definitions

- **Foundry Storage Account**: The primary Azure Storage Account used by Azure AI Foundry Hub for operational data, models, and workspace artifacts
- **Sample Data Storage Account**: A dedicated Azure Storage Account specifically for storing sample datasets and training data
- **DEPLOY_SAMPLE_DATA**: Configuration parameter that controls deployment of sample data infrastructure and uploads
- **Sample Data Containers**: Blob containers defined in `sample-data-containers.json` that store categorized sample datasets
- **AVM**: Azure Verified Modules - Microsoft-provided, validated Bicep modules for Azure resources

## 3. Requirements, Constraints & Guidelines

### Core Requirements

- **REQ-001**: The sample data storage account MUST be deployed only when `DEPLOY_SAMPLE_DATA` parameter is set to `true`
- **REQ-002**: The storage account name MUST be derived from the foundry storage account name with a 'sample' postfix
- **REQ-003**: The sample data storage account MUST use the same Azure Verified Module (AVM) as the foundry storage account
- **REQ-004**: The sample data storage account MUST inherit identical RBAC role assignments as the foundry storage account
- **REQ-005**: Sample data containers defined in `sample-data-containers.json` MUST be created in the sample data storage account and not the foundry storage account
- **REQ-006**: The sample data upload process MUST target the sample data storage account when it exists

### Security Requirements

- **SEC-001**: The sample data storage account MUST have the same network access controls as the foundry storage account
- **SEC-002**: When `azureNetworkIsolation` is enabled, the sample data storage account MUST use private endpoints
- **SEC-003**: The sample data storage account MUST disable public blob access (`allowBlobPublicAccess: false`)
- **SEC-004**: The sample data storage account MUST use Azure AD authentication for access control
- **SEC-005**: All role assignments MUST follow the principle of least privilege

### Network Isolation Requirements

- **NET-001**: When `azureNetworkIsolation` is `true`, the sample data storage account MUST deploy private endpoints in the Data subnet
- **NET-002**: The sample data storage account MUST use the same private DNS zone as the foundry storage account
- **NET-003**: Network ACLs MUST match the foundry storage account configuration (`networkDefaultAction`)

### Naming Constraints

- **NAME-001**: The sample data storage account name MUST be ≤ 24 characters (Azure Storage Account limit)
- **NAME-002**: The sample data storage account name MUST follow the pattern: `{foundryStorageAccountName}sample`
- **NAME-003**: If the combined name exceeds 24 characters, the base name MUST be truncated to accommodate the 'sample' suffix

### Configuration Guidelines

- **GUIDE-001**: Use the same SKU (`Standard_LRS`) as the foundry storage account for cost optimization
- **GUIDE-002**: Enable large file shares state for compatibility with AI workloads
- **GUIDE-003**: Configure the same diagnostic settings as the foundry storage account
- **GUIDE-004**: Apply consistent resource tags across both storage accounts

## 4. Interfaces & Data Contracts

### Bicep Parameters

```bicep
@sys.description('Deploy a dedicated storage account for sample data. When true, creates a separate storage account for sample data instead of using the foundry storage account.')
param deploySampleDataStorageAccount bool = false

@sys.description('Override the default sample data storage account name. Use the magic string `default` to fall back to the generated name.')
@minLength(3)
@maxLength(24)
param sampleDataStorageAccountName string = 'default'
```

### Storage Account Configuration Schema

```bicep
// Sample data storage account naming logic
var sampleDataStorageAccountBaseName = deploySampleDataStorageAccount && sampleDataStorageAccountName == 'default'
  ? take(toLower(replace('${storageAccountName}sample', '-', '')), 24)
  : sampleDataStorageAccountName

// Sample data storage account module parameters
module sampleDataStorageAccount 'br/public:avm/res/storage/storage-account:0.19.0' = if (deploySampleDataStorageAccount && deploySampleData) {
  name: 'sample-data-storage-account-deployment'
  scope: rg
  params: {
    name: sampleDataStorageAccountBaseName
    // Inherit all configuration from foundry storage account
    // except containers are for sample data only
  }
}
```

### Role Assignment Schema

The sample data storage account MUST receive identical role assignments as the foundry storage account:

```bicep
// Role assignments must include:
// - Storage Blob Data Contributor (for AI Search if deployed)
// - Contributor (for principal user/service principal)
// - Storage Blob Data Contributor (for principal user/service principal)  
// - Storage File Data Privileged Contributor (for principal user/service principal)
```

### Output Contract

```bicep
// Required outputs for the sample data storage account
output AZURE_SAMPLE_DATA_STORAGE_ACCOUNT_NAME string = deploySampleDataStorageAccount ? sampleDataStorageAccount.outputs.name : ''
output AZURE_SAMPLE_DATA_STORAGE_ACCOUNT_RESOURCE_ID string = deploySampleDataStorageAccount ? sampleDataStorageAccount.outputs.resourceId : ''
output AZURE_SAMPLE_DATA_STORAGE_ACCOUNT_BLOB_ENDPOINT string = deploySampleDataStorageAccount ? sampleDataStorageAccount.outputs.primaryBlobEndpoint : ''
```

## 5. Rationale & Context

### Separation of Concerns

Creating a dedicated sample data storage account provides clear separation between:

- **Operational Data**: Models, artifacts, and workspace data in the foundry storage account
- **Sample Data**: Training datasets, demo data, and sample content in the dedicated storage account

### Cost Management

- Enables independent cost tracking and governance for sample data vs operational data
- Allows different retention policies and lifecycle management
- Supports separate backup and archival strategies

### Security & Compliance

- Reduces the attack surface by isolating sample data from operational AI assets
- Enables different access patterns and permission models
- Supports data classification and governance requirements

### Development Experience

- Simplifies cleanup of sample data without affecting operational storage
- Enables independent scaling and performance tuning
- Provides clearer data organization for developers and data scientists

## 6. Examples & Edge Cases

### Standard Deployment Example

```yaml
# Environment configuration
DEPLOY_SAMPLE_DATA: true
AZURE_NETWORK_ISOLATION: true
AZURE_STORAGE_ACCOUNT_NAME: default
```

Result:

- Foundry storage account: `staifjumpstart12345abc` (generated)
- Sample data storage account: `staifjumpstart12345sample` (automatically derived)

### Custom Naming Example

```yaml
# Environment configuration  
DEPLOY_SAMPLE_DATA: true
AZURE_STORAGE_ACCOUNT_NAME: mycustomstorage
```

Result:

- Foundry storage account: `mycustomstorage`
- Sample data storage account: `mycustomstoragesample`

### Name Length Edge Case

When the combined name would exceed 24 characters:

```bicep
// Input: foundryStorageAccountName = "verylongstorageaccountname" (27 chars)
// Combined with "sample" = 33 characters (exceeds limit)
// Resolution: Truncate base name to fit within 24 character limit
var truncatedBaseName = take('verylongstorageaccountname', 24 - 6) // 18 chars
var finalName = '${truncatedBaseName}sample' // = "verylongstorageacsample" (24 chars)
```

### Network Isolation Scenario

```bicep
// When azureNetworkIsolation is true
privateEndpoints: [
  {
    privateDnsZoneGroup: {
      privateDnsZoneGroupConfigs: [
        {
          privateDnsZoneResourceId: storageBlobPrivateDnsZone.outputs.resourceId
        }
      ]
    }
    service: 'blob'
    subnetResourceId: virtualNetwork.outputs.subnetResourceIds[2] // Data subnet
    tags: tags
  }
]
```

## 7. Validation Criteria

### Deployment Validation

- **VAL-001**: When `DEPLOY_SAMPLE_DATA` is `false`, no sample data storage account is created
- **VAL-002**: When `DEPLOY_SAMPLE_DATA` is `true`, the sample data storage account is successfully deployed
- **VAL-003**: The sample data storage account name follows the specified naming convention
- **VAL-004**: All sample data containers are created in the sample data storage account, not the foundry storage account

### Security Validation

- **VAL-005**: RBAC role assignments on the sample data storage account match the foundry storage account
- **VAL-006**: When network isolation is enabled, private endpoints are correctly configured
- **VAL-007**: Network access controls match between both storage accounts
- **VAL-008**: Public blob access is disabled on the sample data storage account

### Integration Validation

- **VAL-009**: Sample data upload scripts target the sample data storage account when it exists
- **VAL-010**: AI Foundry project datastores connect to the appropriate storage containers
- **VAL-011**: Diagnostic settings are correctly configured and logs are flowing to Log Analytics

### Performance Validation

- **VAL-012**: The sample data storage account does not impact foundry storage account performance
- **VAL-013**: Private endpoint resolution works correctly for both storage accounts
- **VAL-014**: Sample data upload process completes successfully within expected timeframes

## 8. Related Specifications / Further Reading

- [Azure Storage Account Best Practices](https://docs.microsoft.com/azure/storage/common/storage-account-overview)
- [Azure Private Endpoints Documentation](https://docs.microsoft.com/azure/private-link/private-endpoint-overview)
- [Azure Verified Modules - Storage Account](https://github.com/Azure/bicep-registry-modules/tree/main/avm/res/storage/storage-account)
- [Azure AI Foundry Storage Architecture](../docs/ARCHITECTURE.md)
- [Configuration Options Documentation](../docs/CONFIGURATION_OPTIONS.md)
- [Azure Well-Architected Framework](https://docs.microsoft.com/azure/architecture/framework/)
