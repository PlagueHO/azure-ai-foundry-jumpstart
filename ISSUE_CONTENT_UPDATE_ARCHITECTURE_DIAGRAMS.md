# Chore: Update Architecture Images and Drawio Files to Remove Hub Mode

## Issue Information

**Title**: [Chore]: Update architecture images and drawio files to remove hub mode references

**Labels**: chore

## Issue Details

### Area
Documentation

### Chore Type
Documentation update

### Description
Update the architecture diagrams (both .drawio source files and exported .svg/.png images) to remove references to Azure AI Foundry Hub mode, which has been deprecated as of December 2025. 

The repository has already removed Hub mode support from the infrastructure code and updated text documentation, but the architecture diagrams still contain visual references to Hub mode components that need to be removed or updated to reflect the current AI Services-based architecture.

The following files need to be reviewed and updated:
- `docs/diagrams/azure-ai-foundry-jumpstart-public.drawio`
- `docs/diagrams/azure-ai-foundry-jumpstart-zero-trust.drawio`
- `docs/diagrams/azure-ai-foundry-resources.drawio`
- `docs/images/azure-ai-foundry-jumpstart-public.svg`
- `docs/images/azure-ai-foundry-jumpstart-zero-trust.svg`
- `docs/images/azure-ai-foundry-resources.png`

### Justification
Keeping diagrams synchronized with the codebase and documentation ensures that:
1. Users have accurate visual representations of the deployed architecture
2. The documentation remains consistent and doesn't confuse users with deprecated Hub mode references
3. The solution accelerator presents a clear, unified message about the supported deployment model (AI Services-based projects only)
4. New users are not misled into thinking Hub mode is still supported when viewing the architecture diagrams

The text documentation has already been updated with deprecation notices (as seen in README.md and .github/copilot-instructions.md), but visual diagrams may still show Hub-related components that should be removed.

### Acceptance Criteria
- [ ] Review all three .drawio files in `docs/diagrams/` for Hub mode references
- [ ] Update .drawio files to remove or update any Hub mode components, replacing them with AI Services-based architecture where appropriate
- [ ] Export updated diagrams to their corresponding image formats (.svg and .png files in `docs/images/`)
- [ ] Ensure all diagram labels, component names, and descriptions reflect the current AI Services-based architecture
- [ ] Verify that no visual references to "Hub" or deprecated Hub mode components remain in the diagrams
- [ ] Update ARCHITECTURE.md if diagram changes require corresponding text updates
- [ ] Verify all diagrams render correctly and are readable

### Priority
Medium - Should be addressed in next few releases

### Additional Context
The Hub mode deprecation is documented in:
- README.md (line 8): Contains Hub mode deprecation notice
- .github/copilot-instructions.md: States "Hub Mode Deprecated (Dec 2025)"
- plan/plan-remove-hub-mode-support.prompt.md: Contains the full plan for Hub mode removal

The architecture has transitioned from:
- **Old (Hub mode)**: `Microsoft.MachineLearningServices/workspaces` with `kind: 'Hub'` and supporting resources (Key Vault, Storage Account, Container Registry)
- **New (AI Services mode)**: `Microsoft.CognitiveServices/accounts` with projects deployed directly to the AI Services resource

Any visual representations in the diagrams showing Hub resources, Hub-based project relationships, or Hub mode configuration should be updated to show the AI Services-based architecture instead.

Reference Issues:
- This work is part of the larger Hub mode removal effort
- The infrastructure code changes have already been completed
- Text documentation has been updated with deprecation notices
- This issue completes the documentation update by addressing the visual diagrams
