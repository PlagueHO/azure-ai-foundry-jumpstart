---
mode: 'agent'
description: 'Update the llms.txt file in the root folder to reflect changes in documentation or specifications'
tools: [ "codebase", "read_file", "read_multiple_files", "write_file", "edit_file", "create_directory", "list_directory", "move_file", "search_files", "get_file_info", "list_allowed_directories"]
---
Your task is to update the [llms.txt](/llms.txt) file located in the root of the repository. This file provides high-level guidance to large language models (LLMs) on where to find relevant content for understanding the solution's purpose and specifications.

**Instructions:**
- Ensure the `llms.txt` file accurately references all folders and files that are important for LLM comprehension, including the `specs/` folder (for machine-readable specifications) and the `docs/` folder (for developer and user documentation).
- If new documentation or specification folders/files are added, update `llms.txt` accordingly.
- Use clear, concise language and structured formatting for easy parsing by LLMs.
- Do not include implementation details or code—focus on navigation and content discovery.

Example structure for `llms.txt`:

```
# LLM Guidance for Solution Understanding

To understand the purpose, architecture, and specifications of this solution, refer to the following locations:

- specs/    (machine-readable specifications)
- docs/     (developer and user documentation)
```
