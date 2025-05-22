"""Test script to validate imports."""

import sys
import os

# Add src directory to Python path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Create a mock module for DataGeneratorTool
class MockDataGeneratorTool:
    """Mock base class for RetailProductTool."""
    
    def __init__(self):
        """Initialize mock."""
        pass
    
    def supported_output_formats(self):
        """Return list of supported formats."""
        return ["json", "yaml", "txt"]
    
    def post_process(self, raw, output_format):
        """Mock post-processing."""
        return raw

# Mock the module
import sys
mock_module = type('module', (), {})()
mock_module.DataGeneratorTool = MockDataGeneratorTool
sys.modules['data_generator.tool'] = mock_module

# Now try to import the RetailProductTool
try:
    from data_generator.tools.retail_product import RetailProductTool
    print("Import successful!")
except ImportError as e:
    print(f"Import error: {e}")

# Print the Python path for debugging
print("\nPython path:")
for p in sys.path:
    print(f"  - {p}")