---
mode: 'agent'
description: 'Create a GitHub Issue for an implementation plan using the GitHub Issue template feature_request.yml or chore_request.yml from a plan file.'
tools: ['changes', 'codebase', 'editFiles', 'extensions', 'fetch', 'githubRepo', 'openSimpleBrowser', 'problems', 'runTasks', 'search', 'searchResults', 'terminalLastCommand', 'terminalSelection', 'testFailure', 'usages', 'vscodeAPI', 'github', 'add_issue_comment', 'create_issue', 'get_issue', 'list_issues', 'search_issues', 'update_issue']
---
Create a GitHub Issue in this GitHub repo using the `create_issue` tool for an implementation plan in the plan file [${input:PlanFile}](../plan/${input:PlanFile}) using the GitHub Issue template [feature_request.yml](../ISSUE_TEMPLATE/feature_request.yml) or [chore_request.yml](../ISSUE_TEMPLATE/chore_request.yml).
If the issue already exists, you should update it with the latest information from the plan file.
The plan file contains the details of the implementation plan, including the problem statement, proposed solution, and any additional context or requirements and should be clearly identified in the GitHub issue title.
The issue should be clear, concise, and structured to facilitate understanding and implementation by the development team.
It should only apply changes that are neccessary to implement the plan file and not any other changes that are not required because they are already implemented.
