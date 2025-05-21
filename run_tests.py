#!/usr/bin/env python3
"""
Setup and run tech support tool tests.
"""

import os
import shutil
import sys
import tempfile
import importlib.util
from pathlib import Path

# Create a temporary directory for tests
test_dir = tempfile.mkdtemp()
print(f"Created temporary test directory: {test_dir}")

# Create necessary directory structure
os.makedirs(os.path.join(test_dir, 'data_generator', 'tools'), exist_ok=True)

# Copy the necessary source files
src_dir = Path('/home/runner/work/azure-ai-foundry-jumpstart/azure-ai-foundry-jumpstart/src')

# Copy tool.py (base class)
shutil.copy(
    src_dir / 'data_generator' / 'tool.py',
    os.path.join(test_dir, 'data_generator', 'tool.py')
)

# Copy tech_support.py (implementation)
shutil.copy(
    src_dir / 'data_generator' / 'tools' / 'tech_support.py',
    os.path.join(test_dir, 'data_generator', 'tools', 'tech_support.py')
)

# Create empty __init__.py files to make modules importable
with open(os.path.join(test_dir, 'data_generator', '__init__.py'), 'w') as f:
    f.write('# Package init')

with open(os.path.join(test_dir, 'data_generator', 'tools', '__init__.py'), 'w') as f:
    f.write('# Package init')

# Add the temp directory to sys.path so modules can be imported
sys.path.insert(0, test_dir)

# Import and run the tests
try:
    # Try to import the modules to verify they can be found
    from data_generator.tools.tech_support import TechSupportTool
    from data_generator.tool import DataGeneratorTool
    
    print("Successfully imported modules")
    
    # Now run the tests
    import pytest
    
    # Create a test file in the temp directory
    test_file = os.path.join(test_dir, 'test_tech_support.py')
    
    with open('/home/runner/work/azure-ai-foundry-jumpstart/azure-ai-foundry-jumpstart/tests/data_generator/test_tech_support.py', 'r') as src:
        test_content = src.read()
        
    # Modify the import statement
    test_content = test_content.replace(
        "sys.path.append(\"/home/runner/work/azure-ai-foundry-jumpstart/azure-ai-foundry-jumpstart/src\")",
        f"sys.path.insert(0, \"{test_dir}\")"
    )
    
    with open(test_file, 'w') as dest:
        dest.write(test_content)
    
    # Run the tests
    pytest.main([test_file, '-v'])
    
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)
finally:
    # Clean up
    print(f"Removing temporary directory: {test_dir}")
    shutil.rmtree(test_dir)