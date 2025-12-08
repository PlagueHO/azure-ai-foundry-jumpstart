# Plan: Remove Azure AI Foundry Hub Mode Support

This plan removes the deprecated Azure AI Foundry Hub mode deployment pattern from the repository, simplifying the codebase to support only the modern AI Foundry Project mode (AI Services resource). The Hub mode (`Microsoft.MachineLearningServices/workspaces` with `kind: 'Hub'`) is no longer recommended by Microsoft and adds unnecessary complexity.

## Steps

### 1. Update infrastructure code in main.bicep

Remove Hub-specific parameters, variables, resource deployments, and outputs:

- **Parameters to remove** (lines 27-39):
  - `aiFoundryHubDeploy`
  - `aiFoundryHubProjectDeploy`
  - `aiFoundryHubFriendlyName`
  - `aiFoundryHubDescription`
  - `keyVaultEnablePurgeProtection`

- **Variables to remove** (lines 148, 197, 1076, 1084):
  - `aiFoundryHubName`
  - `aiFoundryHubProjectsList`
  - `aiFoundryHubRoleAssignments`
  - `aiFoundryHubConnections`

- **Resource deployments to remove**:
  - Hub deployment (lines 1125-1183): `aiFoundryHub` module
  - Hub-based projects deployment (lines 1189-1220): `aiFoundryHubProjects` module
  - Hub-specific Key Vault (lines 487-520)
  - Hub-specific Storage Account (lines 522-578)
  - Hub-specific Container Registry (lines 580-680) when Hub-only
  - Hub Private DNS zones (lines 364, 381, 399, 417 for Hub-specific zones)
  - Hub project datastores (lines 1275-1291)
  - Hub role assignments (lines 1224-1271)

- **Outputs to remove** (lines 1309-1366):
  - `AZURE_AI_FOUNDRY_HUB_DEPLOY`
  - `AZURE_AI_FOUNDRY_PROJECT_DEPLOY_TO_HUB`
  - `AZURE_AI_FOUNDRY_HUB_NAME`
  - `AZURE_AI_FOUNDRY_HUB_RESOURCE_ID`
  - `AZURE_AI_FOUNDRY_HUB_PRIVATE_ENDPOINTS`
  - Hub-specific `AZURE_STORAGE_ACCOUNT_NAME`
  - Hub-specific `AZURE_KEY_VAULT_NAME`

- **Conditional logic to simplify**: Remove all conditionals checking `aiFoundryHubDeploy`, `aiFoundryHubProjectDeploy`, or `!aiFoundryHubProjectDeploy && aiFoundryProjectDeploy`

- **Code comments to update**: Remove "BOTH HUB AND PROJECT MODE" references and simplify to just describe Project mode

### 2. Remove Hub-supporting Bicep modules and configurations

- **Delete files**:
  - `infra/core/ai/ai-foundry-project-datastore.bicep` (datastores for Hub projects)
  - `infra/core/security/role_storageaccount.bicep` (Hub storage roles)

- **Update configuration files**:
  - `infra/abbreviations.json`: Remove line 4 (`"aiFoundryHubs": "aihub-"`)
  - `infra/main.bicepparam`: Remove lines 28-31 (Hub-related parameters)
  - `infra/sample-ai-foundry-projects.json`: Update documentation/comments to reflect projects only deploy to AI Services resource

### 3. Delete Hub-specific GitHub Actions workflow configurations

- **`.github/workflows/e2e-test.yml`** (lines 38-60):
  - Remove `hub-public` matrix item (lines 45-52)
  - Remove `hub-isolated` matrix item (lines 53-60)
  - Keep only `project-public` and `project-isolated` configurations

- **`.github/workflows/continuous-delivery.yml`** (lines 29-31):
  - Remove `AZURE_AI_FOUNDRY_HUB_DEPLOY` input parameter

- **`.github/workflows/validate-infrastructure.yml`** (lines 28-31, 82):
  - Remove `AZURE_AI_FOUNDRY_HUB_DEPLOY` input parameter
  - Remove Hub parameter from Bicep validation (line 82)

- **`.github/workflows/provision-infrastructure.yml`** (lines 28-31, 57):
  - Remove `AZURE_AI_FOUNDRY_HUB_DEPLOY` input parameter
  - Remove Hub environment variable (line 57)

- **`.github/workflows/delete-infrastructure.yml`**:
  - Review and remove Hub-specific cleanup logic if any

### 4. Rewrite documentation to remove Hub mode explanations

- **Delete entire file**:
  - `docs/PROJECT_MODES.md` (primary Hub mode documentation)

- **`docs/CONFIGURATION_OPTIONS.md`**:
  - Remove Hub environment variables section (lines 107-181):
    - `AZURE_AI_FOUNDRY_HUB_DEPLOY`
    - `AZURE_AI_FOUNDRY_HUB_FRIENDLY_NAME`
    - `AZURE_AI_FOUNDRY_HUB_DESCRIPTION`
    - `AZURE_AI_FOUNDRY_HUB_PROJECT_DEPLOY`
  - Remove project deployment scenarios that reference Hub (lines 143-147)

- **`docs/QUICK_CONFIGURATIONS.md`**:
  - Remove "Project Mode With Hub" section (lines 34-68)
  - Keep only "Project Mode Without Hub" configuration

- **`docs/ARCHITECTURE.md`**:
  - Remove Hub architecture overview (lines 10-40)
  - Remove Hub vs AI Services project comparison table (lines 164-177)
  - Simplify to show only AI Foundry Project mode architecture
  - Remove references to Hub as optional component

- **`docs/TECHNOLOGY.md`**:
  - Remove Hub from technology stack (lines 10-25)
  - Remove Storage Account, Key Vault, Container Registry as Hub-specific components

- **`docs/OVERVIEW.md`**:
  - Remove Hub mode references (lines 27-34)
  - Remove recommendation against Hub use since it won't be available
  - Simplify to describe only Project mode

- **`docs/FOLDERS.md`**:
  - Update if it references Hub-specific folders or files

### 5. Add deprecation notice to README.md

Add a prominent notice near the top of the README (after the title/description, before getting started):

```markdown
## ⚠️ Hub Mode Removed

**As of December 2025**, Azure AI Foundry Hub mode support has been removed from this repository. Hub mode (`Microsoft.MachineLearningServices/workspaces` with `kind: 'Hub'`) is not recommended for new Azure AI Foundry deployments.

**For existing Hub deployments:**
- Existing Hub-based deployments will continue to function in Azure
- This repository no longer supports provisioning or managing Hub mode deployments
- Users should plan migration to AI Foundry Project mode for new projects

**All new deployments** use the AI Foundry Project mode exclusively.
```

### 6. Clean up supporting files

- **`.vscode/settings.json`**:
  - Remove `aiFoundryHubDeploy` from spell-check dictionary (line 46)

- **`.github/copilot-instructions.md`**:
  - Remove glossary entries about Hub vs Project modes (lines 5-6)
  - Update to clarify only Project mode is supported
  - Remove distinction between Hub and AI Foundry resource

- **Architectural diagrams**: These will need to be updated manually to remove Hub references.
  - `docs/diagrams/azure-ai-foundry-resources.drawio`: Delete or update to remove Hub architecture
  - `docs/diagrams/azure-ai-foundry-jumpstart-public.drawio`: Remove Hub deployment option
  - `docs/diagrams/azure-ai-foundry-jumpstart-zero-trust.drawio`: Remove Hub deployment option

## Further Considerations

### 1. Sample data deployment scripts impact

**Review required**: Check if these scripts have Hub-specific logic:
- `scripts/Upload-SampleData.ps1`
- `scripts/Upload-SampleData.sh`
- `scripts/Compress-SampleData.ps1`

**Questions**:
- Do they access Hub storage accounts versus AI Services storage differently?
- Do they need updating to work only with Project mode storage?
- Do they reference Hub environment variables that will be removed?

### 2. Migration guide for existing users

**Options**:
1. Create `docs/MIGRATION_HUB_TO_PROJECT.md` with detailed migration steps
2. Include migration guidance in the README deprecation notice
3. Provide only a reference to Microsoft's official migration documentation

**Recommendation**: At minimum, provide high-level migration guidance either in README or a separate migration doc explaining:
- How to identify if you're using Hub mode
- Steps to redeploy using Project mode
- Data migration considerations
- What happens to existing Hub resources

### 3. Breaking change versioning

**Impact**: This is a **major breaking change** for users with `AZURE_AI_FOUNDRY_HUB_DEPLOY=true`

**Actions**:
1. Bump major version in `GitVersion.yml` (e.g., from 1.x to 2.0)
2. Create Git tag marking the last Hub-supporting commit (e.g., `v1.x.x-last-hub-support`)
3. Update CHANGELOG or release notes documenting the breaking change
4. Consider creating a GitHub release with migration guidance

### 4. Additional items to check

- **Test files**: Check `tests/` directory for Hub mode tests that need removal
- **Spec files**: Review `spec/` directory for Hub mode references in specifications
- **Sample applications**: Check `src/samples/` for Hub-specific code or configurations
- **Tool implementations**: Check `src/tools/` for Hub mode logic
- **Azure CLI scripts**: Review any `azd` hooks or scripts for Hub-specific logic
- **Container Registry dependency**: Determine if Container Registry is still needed without Hub mode, or if it was Hub-only
- **Key Vault dependency**: Determine if Key Vault is still needed without Hub mode, or if it was Hub-only
- **Storage Account dependency**: Confirm AI Services resource has its own storage and Hub storage is truly unnecessary

### 5. Documentation clarity

After Hub removal, ensure documentation clearly explains:
- What AI Foundry Project mode is and how it works
- The simplified architecture without Hub complexity
- Benefits of the modern approach (fewer resources, simpler management)
- How projects connect to AI Services, OpenAI, AI Search without Hub intermediary

### 6. Code cleanup opportunities

With Hub mode removed:
- Simplify conditional logic throughout `main.bicep`
- Reduce complexity of project deployment (single path instead of two)
- Consolidate role assignments (no Hub-to-project relationships)
- Simplify network isolation (fewer private DNS zones, fewer private endpoints)
- Reduce parameter count and configuration complexity

### 7. Testing validation

After implementation:
- Ensure `project-public` E2E test passes
- Ensure `project-isolated` E2E test passes
- Validate all Bicep deployments succeed without Hub parameters
- Confirm documentation is consistent and complete
- Verify no broken links in documentation
- Check that sample applications work with Project mode only
