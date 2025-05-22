"""
Tests for the direct implementation of RetailProductTool in src/data_generator/tools/retail_product.py
"""
import os
import sys
from unittest.mock import patch, Mock

# Add data_generator to Python path for direct imports
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), "../../src/data_generator")))

# Create mock module for the parent module
mock_tool_module = Mock()
mock_tool_module.DataGeneratorTool = type('MockDataGeneratorTool', (), {
    '__init__': lambda self: None,
})
sys.modules['tool'] = mock_tool_module

# Test direct import of the actual module code
from tools.retail_product import RetailProductTool


def test_retail_product_module_import():
    """Test that the retail_product module can be imported directly."""
    assert RetailProductTool is not None
    assert RetailProductTool.name == "retail-product"
    assert RetailProductTool.toolName == "RetailProduct"


def test_retail_product_basic_methods():
    """Test the basic methods of RetailProductTool."""
    tool = RetailProductTool(industry="test_industry")
    assert tool.industry == "test_industry"
    assert "test_industry" in tool.get_system_description()


def test_supported_output_formats():
    """Test the supported output formats."""
    tool = RetailProductTool()
    formats = tool.supported_output_formats()
    assert set(formats) == {"yaml", "json", "text"}


@patch('tools.retail_product.RetailProductTool._random_price')
@patch('tools.retail_product.RetailProductTool._random_stock')
@patch('random.choice')
def test_post_process(mock_choice, mock_stock, mock_price):
    """Test the post_process method with data enrichment."""
    mock_price.return_value = 99.99
    mock_stock.return_value = 42
    mock_choice.return_value = "USD"

    tool = RetailProductTool()
    
    # Test with valid JSON
    result = tool.post_process('{"name":"Test"}', "json")
    assert isinstance(result, dict)
    assert result["name"] == "Test"
    assert result["price"] == 99.99
    assert result["currency"] == "USD"
    assert result["stock_quantity"] == 42

    # Test with text format
    assert tool.post_process("plain text", "text") == "plain text"