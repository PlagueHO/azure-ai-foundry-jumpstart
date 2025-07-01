---
mode: 'agent'
description: Update an existing implementation plan file with new or update requirements to provide new features, refactoring existing code or upgrading packages, design, architecture or infrastructure.
tools: ['changes', 'codebase', 'editFiles', 'extensions', 'fetch', 'githubRepo', 'openSimpleBrowser', 'problems', 'runTasks', 'search', 'searchResults', 'terminalLastCommand', 'terminalSelection', 'testFailure', 'usages', 'vscodeAPI']
---
## Update Plan Prompt

Your goal is to update the existing implementation plan file `${file}` based on new or updated requirements to provide new features, refactoring existing code or upgrading packages, design, architecture or infrastructure.

The plan file must define the implementation details, including specific tasks, dependencies, and testing strategies, in a manner that is clear, unambiguous, and structured for effective use by Generative AIs. Follow established documentation standards and ensure the content is machine-readable and self-contained.

**Best Practices for AI-Ready Specifications:**
- Use precise, explicit, and unambiguous language.
- Clearly distinguish between requirements, constraints, and recommendations.
- Use structured formatting (headings, lists, tables) for easy parsing.
- Avoid idioms, metaphors, or context-dependent references.
- Define all acronyms and domain-specific terms.
- Include examples and edge cases where applicable.
- Ensure the document is self-contained and does not rely on external context.

The plan file should be saved in the [/plan/](/plan/) directory and named according to the following convention: `[a-z0-9-]+.md`, where the name should be descriptive of the plan's goal, such as `upgrade-system-command-4.md` or `refactor-lodash-4.md` and and starting with the highlevel purpose, which is one of [upgrade, refactor, feature, data, infrastructure, process, architecture, or design].

The plan file must be formatted in well formed Markdown.

Plan files must follow the template below, ensuring that all sections are filled out appropriately. The front matter and structure of the markdown for the plan should be structured correctly as per the example following:

```md
---
goal: [Concise Title Describing the Package Plan's Goal]
version: [Optional: e.g., 1.0, Date]
date_created: [YYYY-MM-DD]  
last_updated: [Optional: YYYY-MM-DD]  
owner: [Optional: Team/Individual responsible for this spec]
tags: [Optional: List of relevant tags or categories, e.g., `feature`, `upgrade`, `chore`, `architecture`, `migration`, `bug` etc]
---

# Introduction

[A short concise introduction to the plan and the goal it is intended to achieve.]

## 1. Requirements & Constraints

[Explicitly list all requirements & constraints that affect the plan and constrain how it is implemented. Use bullet points or tables for clarity.]

- **REQ-001**: Requirement 1
- **SEC-001**: Security Requirement 1
- **[3 LETTERS]-001**: Other Requirement 1
- **CON-001**: Constraint 1
- **GUD-001**: Guideline 1
- **PAT-001**: Pattern to follow 1

## 2. Implementation Steps

[Describe the steps/tasks required to achieve the goal.]

## 3. Alternatives

[A bullet point list of any alternative approaches that were considered and why they were not chosen. This helps to provide context and rationale for the chosen approach.]

- **ALT-001**: Alternative approach 1
- **ALT-002**: Alternative approach 2

## 4. Dependencies

[List any dependencies that need to be addressed, such as libraries, frameworks, or other components that the plan relies on.]

- **DEP-001**: Dependency 1
- **DEP-002**: Dependency 2

## 5. Files

[List the files that will be affected by the feature or refactoring task.]

- **FILE-001**: Description of file 1
- **FILE-002**: Description of file 2

## 6. Testing

[List the tests that need to be implemented to verify the feature or refactoring task.]

- **TEST-001**: Description of test 1
- **TEST-002**: Description of test 2

## 7. Risks & Assumptions

[List any risks or assumptions related to the implementation of the plan.]

- **RISK-001**: Risk 1
- **ASSUMPTION-001**: Assumption 1

## 8. Related Specifications / Further Reading

[Link to related spec 1]  
[Link to relevant external documentation]
```
