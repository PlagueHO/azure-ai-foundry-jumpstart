---
mode: 'agent'
description: 'Create GitHub Issues for each requirement in a specification file that is not already implemented in the codebase using the GitHub Issue template feature_request.yml.'
tools: ['changes', 'codebase', 'editFiles', 'extensions', 'fetch', 'githubRepo', 'openSimpleBrowser', 'problems', 'runTasks', 'search', 'searchResults', 'terminalLastCommand', 'terminalSelection', 'testFailure', 'usages', 'vscodeAPI', 'github', 'add_issue_comment', 'create_issue', 'get_issue', 'list_issues', 'search_issues', 'update_issue']
---
You task is to review the specification file [${input:SpecFile}](../spec/${input:SpecFile}) and identify any requirements that are not implemented in the codebase, then create GitHub Issues using the `create_issue` tool for each missing issue, using the GitHub Issue template [feature_request.yml](../ISSUE_TEMPLATE/feature_request.yml).

You must follow these steps:
1. From the specification file [${input:SpecFile}](../spec/${input:SpecFile}), create a table of requirements that are listed in the specification, as well as an instruction on how to determine if the requirement is implemented. The table should have the following columns:
   - Requirement ID: A unique identifier for the requirement.
   - Description: A brief description of the requirement.
   - Implementation Method: A brief description of how to determine if the requirement is implemented in the codebase.
2. For each requirement in the table, review the codebase to determine if the requirement is already implemented using the Implementation Method provided in the table. If the requirement is implemented, you do not need to create a GitHub Issue for it.
> [!NOTE]
> If you are unsure if a requirement is implemented, you can ask for clarification or look for additional information in the codebase, such as comments, documentation, or related files.
3. If the requirement is not implemented, look through the other specification files in the [spec](../spec) directory of the ${workspaceFolder} to determine if a similar or related requirement can be found in them.
> [!NOTE]
> If you find a similar or related requirement in another specification file, you should ask the user to confirm if it is related to the requirement you are trying to implement.
4. Search the existing GitHub Issues using the `search_issues` tool in this repository to see if there is already an issue that matches the requirement.
5. If no similar or related requirement is found in the other specification files or existing GitHub Issues, create a new GitHub Issue using the `create_issue` tool with the title and description based on the requirement details from the specification file.
