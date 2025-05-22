"""
Tests for the RetailProductTool in data_generator.tools.retail_product.

This test suite uses mocking to test the RetailProductTool class directly from 
the module, ensuring it's included in coverage metrics.
"""

import argparse
import json
import sys
import os
import uuid
from unittest.mock import Mock, patch

import yaml

# Make sure we can directly import the data_generator module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../src")))

# Setup the mock for DataGeneratorTool first
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
        if output_format == "json":
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return raw
        elif output_format == "yaml":
            try:
                return yaml.safe_load(raw)
            except yaml.YAMLError:
                return raw
        return raw

# Create a mock module to hold our mock class
mock_module = Mock()
mock_module.DataGeneratorTool = MockDataGeneratorTool
sys.modules['data_generator.tool'] = mock_module

# Now import the actual module to test
from data_generator.tools.retail_product import RetailProductTool


class TestRetailProductTool:
    """Test suite for RetailProductTool functionality."""

    # ------------------------------------------------------------------ #
    # Initialization Tests                                               #
    # ------------------------------------------------------------------ #
    def test_default_initialization(self) -> None:
        """Test default initialization with no parameters."""
        tool = RetailProductTool()
        assert tool.industry == "general"

    def test_custom_industry_initialization(self) -> None:
        """Test initialization with custom industry."""
        tool = RetailProductTool(industry="electronics")
        assert tool.industry == "electronics"

    # ------------------------------------------------------------------ #
    # CLI Interface Tests                                                #
    # ------------------------------------------------------------------ #
    def test_cli_arguments(self) -> None:
        """Test cli_arguments method returns expected structure."""
        tool = RetailProductTool()
        args = tool.cli_arguments()
        
        assert len(args) == 1
        assert args[0]["flags"] == ["-i", "--industry"]
        assert not args[0]["kwargs"]["required"]
        assert args[0]["kwargs"]["default"] == "general"

    def test_validate_args(self) -> None:
        """Test validate_args persists args correctly."""
        tool = RetailProductTool()
        
        # Test with industry set
        ns = argparse.Namespace(industry="fashion")
        tool.validate_args(ns)
        assert tool.industry == "fashion"
        
        # Test with industry None (should default to "general")
        ns = argparse.Namespace(industry=None)
        tool.validate_args(ns)
        assert tool.industry == "general"

    def test_examples(self) -> None:
        """Test examples method returns non-empty list of strings."""
        tool = RetailProductTool()
        examples = tool.examples()
        
        assert isinstance(examples, list)
        assert len(examples) > 0
        assert all(isinstance(ex, str) for ex in examples)
        assert all("retail-product" in ex for ex in examples)

    # ------------------------------------------------------------------ #
    # Output Format Tests                                                #
    # ------------------------------------------------------------------ #
    def test_supported_output_formats(self) -> None:
        """Test supported_output_formats returns expected formats."""
        tool = RetailProductTool()
        formats = tool.supported_output_formats()
        
        assert isinstance(formats, list)
        assert set(formats) == {"yaml", "json", "text"}

    # ------------------------------------------------------------------ #
    # Prompt Generation Tests                                            #
    # ------------------------------------------------------------------ #
    def test_prompt_common(self) -> None:
        """Test _prompt_common includes expected elements."""
        tool = RetailProductTool(industry="sports")
        test_id = "test-123"
        
        result = tool._prompt_common(unique_id=test_id)
        
        assert test_id in result
        assert "Created At:" in result
        assert "Industry Theme: sports" in result

    def test_prompt_common_generates_uuid(self) -> None:
        """Test _prompt_common generates UUID when not provided."""
        tool = RetailProductTool()
        
        result = tool._prompt_common()
        
        # Check that the method ran and returned a result
        assert "Product ID" in result
        assert "Created At:" in result
        assert "Industry Theme:" in result

    def test_build_prompt_yaml(self) -> None:
        """Test build_prompt for YAML output format."""
        tool = RetailProductTool(industry="electronics")
        test_id = "test-uuid-yaml"
        
        result = tool.build_prompt("yaml", unique_id=test_id)
        
        assert test_id in result
        assert "Return valid YAML ONLY" in result
        assert "category: sub-category relevant to electronics" in result

    def test_build_prompt_json(self) -> None:
        """Test build_prompt for JSON output format."""
        tool = RetailProductTool(industry="books")
        test_id = "test-uuid-json"
        
        result = tool.build_prompt("json", unique_id=test_id)
        
        assert test_id in result
        assert "Return valid JSON ONLY" in result
        assert "Relevant sub-category for books" in result

    def test_build_prompt_text(self) -> None:
        """Test build_prompt for plain text output format."""
        tool = RetailProductTool()
        test_id = "test-uuid-text"
        
        result = tool.build_prompt("text", unique_id=test_id)
        
        assert test_id in result
        assert "Return plain text WITHOUT YAML/JSON markers" in result
        assert "60-120 word paragraph" in result

    # ------------------------------------------------------------------ #
    # Helper Method Tests                                                #
    # ------------------------------------------------------------------ #
    def test_random_price(self) -> None:
        """Test _random_price returns float in expected range."""
        price = RetailProductTool._random_price()
        
        assert isinstance(price, float)
        assert 5.0 <= price <= 500.0
        assert str(price).split('.')[-1] != ""  # Has decimal component

    def test_random_stock(self) -> None:
        """Test _random_stock returns int in expected range."""
        stock = RetailProductTool._random_stock()
        
        assert isinstance(stock, int)
        assert 0 <= stock <= 500

    # ------------------------------------------------------------------ #
    # Post-processing Tests                                              #
    # ------------------------------------------------------------------ #
    def test_post_process_json_valid(self) -> None:
        """Test post_process handles valid JSON correctly."""
        tool = RetailProductTool()
        valid_json = '{"product_id": "123", "name": "Test Product"}'
        
        result = tool.post_process(valid_json, "json")
        
        assert isinstance(result, dict)
        assert result["product_id"] == "123"
        assert result["name"] == "Test Product"
        assert "price" in result  # Check for data enrichment
        assert "currency" in result
        assert "stock_quantity" in result

    def test_post_process_yaml_valid(self) -> None:
        """Test post_process handles valid YAML correctly."""
        tool = RetailProductTool()
        valid_yaml = "product_id: 123\nname: Test Product"
        
        result = tool.post_process(valid_yaml, "yaml")
        
        assert isinstance(result, dict)
        assert result["product_id"] == 123
        assert result["name"] == "Test Product"
        assert "price" in result  # Check for data enrichment
        assert "currency" in result
        assert "stock_quantity" in result

    def test_post_process_text(self) -> None:
        """Test post_process with text format returns raw string."""
        tool = RetailProductTool()
        text = "Product details in plain text format"
        
        result = tool.post_process(text, "text")
        assert result == text
        
        # Also test with "txt" format alias
        result = tool.post_process(text, "txt")
        assert result == text

    def test_post_process_json_invalid(self) -> None:
        """Test post_process handles invalid JSON gracefully."""
        tool = RetailProductTool()
        invalid_json = '{product_id: "missing quotes"}'
        
        result = tool.post_process(invalid_json, "json")
        assert result == invalid_json  # Should return raw string

    def test_post_process_yaml_invalid(self) -> None:
        """Test post_process handles invalid YAML gracefully."""
        tool = RetailProductTool()
        
        # Use a truly invalid YAML string that will cause an error
        invalid_yaml = ": invalid: yaml: format:"
        
        result = tool.post_process(invalid_yaml, "yaml")
        assert result == invalid_yaml  # Should return raw string

    def test_post_process_unknown_format(self) -> None:
        """Test post_process handles unknown formats gracefully."""
        tool = RetailProductTool()
        data = "Some data"
        
        result = tool.post_process(data, "unknown_format")
        assert result == data  # Should return raw string

    # ------------------------------------------------------------------ #
    # Other Method Tests                                                 #
    # ------------------------------------------------------------------ #
    def test_get_system_description(self) -> None:
        """Test get_system_description returns expected string."""
        tool = RetailProductTool(industry="fashion")
        
        result = tool.get_system_description()
        
        assert "Retail catalogue for fashion products" == result

    # ------------------------------------------------------------------ #
    # Data Enrichment Tests                                              #
    # ------------------------------------------------------------------ #
    def test_data_enrichment_adds_missing_fields(self) -> None:
        """Test data enrichment adds missing fields."""
        tool = RetailProductTool()
        minimal_json = '{"product_id": "123", "name": "Test"}'
        
        result = tool.post_process(minimal_json, "json")
        
        assert "price" in result
        assert "currency" in result
        assert "stock_quantity" in result

    def test_data_enrichment_preserves_existing_fields(self) -> None:
        """Test data enrichment preserves existing fields."""
        tool = RetailProductTool()
        json_with_fields = '{"product_id": "123", "name": "Test", "price": 99.99, "currency": "EUR"}'
        
        result = tool.post_process(json_with_fields, "json")
        
        assert result["price"] == 99.99
        assert result["currency"] == "EUR"
        assert "stock_quantity" in result  # Should add missing fields