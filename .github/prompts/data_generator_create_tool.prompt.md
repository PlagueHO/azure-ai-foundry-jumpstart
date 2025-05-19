---
mode: 'edit'
description: 'Generate a new tool for the data_generator'
---
Your goal is to create a new tool for the data_generator for the purpose of generating data for `${input:ToolPurpose}`.
The tool should be a Python class that subclasses the [DataGeneratorTool](../../src/data_generator/tool.py) class. Ensure you use the method signatures as found in the base class.
The new tool should follow the same structure and style as the existing tools in the [src/data_generator/tools](../../src/data_generator/tools) directory, for example, the [retail_product.py](../../src/data_generator/tools/retail_product.py) tool.
The new tool file should be created in the [src/data_generator/tools](../../src/data_generator/tools) directory. The methods and functions should include docstrings and meet clean code standards. 
The methods in the tool should include:
- `__init__`
- `supported_output_formats`
- `cli_arguments`
- `validate_args`
- `examples`
- `build_prompt`
- `post_process`
- `get_system_description`
Specific details for the tool naming:
- Filename: `[a-z_]+.py`
- Class name: Camel Case filename without '_' + 'Tool' (e.g. `RetailProductTool`)
- name property: same as filename, but '-' instead of '_'
- toolName property: same as class name, without Tool at the end (e.g. `RetailProduct`)
