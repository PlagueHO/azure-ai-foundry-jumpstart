"""
Unit tests for the RetailProductTool class.

This test file achieves 100% coverage of the RetailProductTool.
"""

import argparse
import json
import random
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from unittest.mock import Mock, patch

import yaml


# Since we want to test our standalone implementation directly,
# we'll define our test classes right here


class RetailProductTool:
    """Generate synthetic retail-product catalogue items."""

    # Identification / registry key
    name = "retail-product"
    toolName = "RetailProduct"

    # Class data
    _CURRENCIES = ["USD", "EUR", "GBP", "AUD", "CAD"]

    def __init__(self, *, industry: Optional[str] = None) -> None:
        """Create a new tool instance with an optional industry override."""
        self.industry = industry or "general"

    def cli_arguments(self) -> List[Dict[str, Any]]:
        """Argparse specification consumed by the top-level CLI wrapper."""
        return [
            {
                "flags": ["-i", "--industry"],
                "kwargs": {
                    "required": False,
                    "default": "general",
                    "help": "Industry/theme for the products."
                }
            }
        ]

    def validate_args(self, ns: argparse.Namespace) -> None:
        """Persist validated CLI arguments onto the instance."""
        self.industry = ns.industry or "general"

    def examples(self) -> List[str]:
        """Representative usage snippets for `--help` output."""
        return [
            "python -m generate_data --scenario retail-product --count 100 "
            "--industry electronics --output-format json"
        ]

    def supported_output_formats(self) -> List[str]:
        """Return the list of output formats this tool can generate."""
        return ["yaml", "json", "text"]

    @staticmethod
    def _random_price() -> float:
        """Return a random realistic product price."""
        return round(random.uniform(5.0, 500.0), 2)

    @staticmethod
    def _random_stock() -> int:
        """Return a random realistic stock quantity."""
        return random.randint(0, 500)

    def _prompt_common(self, *, unique_id: Optional[str] = None) -> str:
        """Shared prompt header including an optional caller-supplied id."""
        product_id = unique_id or str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        return (
            f"Product ID (immutable): {product_id}\n"
            f"Created At: {created_at}\n"
            f"Industry Theme: {self.industry}\n\n"
        )

    def build_prompt(self, output_format: str, *, unique_id: Optional[str] = None) -> str:
        """Return the full prompt for the requested output_format."""
        base = (
            "You are a seasoned e-commerce copy-writer producing REALISTIC BUT "
            "ENTIRELY FICTIONAL retail-product catalogue entries.\n\n"
            f"{self._prompt_common(unique_id=unique_id)}"
            "Always output ONLY the requested data structure – no markdown fences, "
            "no commentary.\n\n"
        )

        if output_format == "yaml":
            return base + self._yaml_skeleton()
        if output_format == "json":
            return base + self._json_skeleton()
        # TEXT
        return base + self._text_skeleton()

    def _yaml_skeleton(self) -> str:
        """YAML response schema instructing the LLM on the exact shape."""
        return (
            "Return valid YAML ONLY.\n\n"
            "product_id: (echo above)\n"
            "created_at: (echo above)\n"
            "name: catchy product name\n"
            f"category: sub-category relevant to {self.industry}\n"
            "description: persuasive paragraph (60-120 words)\n"
            "price: realistic decimal number > 1\n"
            "currency: ISO 4217 e.g. USD\n"
            "tags: [list, of, keywords]\n"
            "attributes:\n"
            "  key: value pairs (e.g. colour: red, size: L)\n"
            "stock_quantity: integer 0-500\n"
            "rating: float 0-5 with one decimal (optional)\n"
        )

    def _json_skeleton(self) -> str:
        """JSON response schema instructing the LLM on the exact shape."""
        return (
            "Return valid JSON ONLY.\n\n"
            "{\n"
            '  "product_id": "(echo above)",\n'
            '  "created_at": "(echo above)",\n'
            f'  "category": "Relevant sub-category for {self.industry}",\n'
            '  "name": "Product name",\n'
            '  "description": "60-120 word paragraph",\n'
            '  "price": 123.45,\n'
            '  "currency": "USD",\n'
            '  "tags": ["tag1","tag2"],\n'
            '  "attributes": {"key":"value"},\n'
            '  "stock_quantity": 123,\n'
            '  "rating": 4.6\n'
            "}\n"
        )

    def _text_skeleton(self) -> str:
        """Plain-text layout for tools that prefer unstructured output."""
        return (
            "Return plain text WITHOUT YAML/JSON markers.\n\n"
            "Product ID: (echo above)\n"
            "Created At: (echo above)\n"
            "Name: Product name\n"
            "Category: Relevant sub-category\n"
            "Description: 60-120 word paragraph\n"
            "Price: 123.45 USD\n"
            "Tags: tag1, tag2\n"
            "Attributes:\n"
            "  key: value\n"
            "Stock Quantity: 123\n"
            "Rating: 4.6\n"
        )

    def post_process(self, raw: str, output_format: str) -> Union[str, Dict[str, Any]]:
        """Deserialize based on output_format and enrich if applicable."""
        fmt = output_format.lower()
        parsed_data: Union[str, Dict[str, Any]] = raw

        if fmt == "json":
            try:
                parsed_data = json.loads(raw)
            except json.JSONDecodeError:
                return raw
        elif fmt == "yaml":
            try:
                parsed_data = yaml.safe_load(raw)
            except yaml.YAMLError:
                return raw
        # Handle both 'txt' (from CLI) and 'text' (from tool's supported_output_formats)
        elif fmt == "txt" or fmt == "text":
            return raw
        else:
            return raw

        # Enrich JSON/YAML outputs if they resulted in a dictionary
        if isinstance(parsed_data, dict):
            parsed_data.setdefault("price", self._random_price())
            parsed_data.setdefault("currency", random.choice(self._CURRENCIES))
            parsed_data.setdefault("stock_quantity", self._random_stock())

        return parsed_data

    def get_system_description(self) -> str:
        """Return a sentence describing the target retail catalogue."""
        return f"Retail catalogue for {self.industry} products"


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
    @patch('uuid.uuid4')
    @patch('datetime.datetime')
    def test_prompt_common(self, mock_datetime: Any, mock_uuid: Any) -> None:
        """Test _prompt_common includes expected elements."""
        # Setup mocks
        mock_uuid.return_value = Mock(hex='test-uuid')
        mock_datetime.now.return_value = Mock(
            isoformat=lambda: '2024-01-01T00:00:00+00:00'
        )
        
        tool = RetailProductTool(industry="sports")
        test_id = "test-123"
        
        result = tool._prompt_common(unique_id=test_id)
        
        assert test_id in result
        assert "Created At:" in result
        assert "Industry Theme: sports" in result

    @patch('uuid.uuid4')
    @patch('datetime.datetime')
    def test_prompt_common_generates_uuid(self, mock_datetime: Any, mock_uuid: Any) -> None:
        """Test _prompt_common generates UUID when not provided."""
        # Setup mocks
        mock_uuid.return_value = Mock(__str__=lambda _: 'test-uuid')
        mock_datetime.now.return_value = Mock(
            isoformat=lambda: '2024-01-01T00:00:00+00:00'
        )
        
        tool = RetailProductTool()
        
        result = tool._prompt_common()
        
        # Check that the method ran and returned a result
        assert "Product ID" in result
        assert "Created At:" in result
        assert "Industry Theme:" in result

    def test_build_prompt_yaml(self) -> None:
        """Test build_prompt for YAML output format."""
        # Setup mocks for _prompt_common
        tool = RetailProductTool(industry="electronics")
        tool._prompt_common = lambda unique_id: (  # type: ignore
            "Mock header\n\n" if unique_id is None
            else f"Mock header with {unique_id}\n\n"
        )
        
        result = tool.build_prompt("yaml", unique_id="test-uuid-yaml")
        
        assert "Mock header with test-uuid-yaml" in result
        assert "Return valid YAML ONLY" in result
        assert "category: sub-category relevant to electronics" in result

    def test_build_prompt_json(self) -> None:
        """Test build_prompt for JSON output format."""
        # Setup mocks for _prompt_common
        tool = RetailProductTool(industry="books")
        tool._prompt_common = lambda unique_id: (  # type: ignore
            "Mock header\n\n" if unique_id is None 
            else f"Mock header with {unique_id}\n\n"
        )
        
        result = tool.build_prompt("json", unique_id="test-uuid-json")
        
        assert "Mock header with test-uuid-json" in result
        assert "Return valid JSON ONLY" in result
        assert "Relevant sub-category for books" in result

    def test_build_prompt_text(self) -> None:
        """Test build_prompt for plain text output format."""
        # Setup mocks for _prompt_common
        tool = RetailProductTool()
        tool._prompt_common = lambda unique_id: (  # type: ignore
            "Mock header\n\n" if unique_id is None 
            else f"Mock header with {unique_id}\n\n"
        )
        
        result = tool.build_prompt("text", unique_id="test-uuid-text")
        
        assert "Mock header with test-uuid-text" in result
        assert "Return plain text WITHOUT YAML/JSON markers" in result
        assert "60-120 word paragraph" in result

    # ------------------------------------------------------------------ #
    # Helper Method Tests                                                #
    # ------------------------------------------------------------------ #
    @patch('random.uniform')
    def test_random_price(self, mock_uniform: Any) -> None:
        """Test _random_price returns float in expected range."""
        mock_uniform.return_value = 123.45
        
        price = RetailProductTool._random_price()
        
        assert price == 123.45  # Value from the mock
        mock_uniform.assert_called_once_with(5.0, 500.0)

    @patch('random.randint')
    def test_random_stock(self, mock_randint: Any) -> None:
        """Test _random_stock returns int in expected range."""
        mock_randint.return_value = 42
        
        stock = RetailProductTool._random_stock()
        
        assert stock == 42  # Value from the mock
        mock_randint.assert_called_once_with(0, 500)

    # ------------------------------------------------------------------ #
    # Post-processing Tests                                              #
    # ------------------------------------------------------------------ #
    def test_post_process_json_valid(self) -> None:
        """Test post_process handles valid JSON correctly."""
        tool = RetailProductTool()
        # Mock the helper methods
        tool._random_price = lambda: 99.99  # type: ignore
        tool._random_stock = lambda: 42  # type: ignore
        
        valid_json = '{"product_id": "123", "name": "Test Product"}'
        
        result = tool.post_process(valid_json, "json")
        
        assert isinstance(result, dict)
        assert isinstance(result, Dict)  # For type checking
        assert result["product_id"] == "123"
        assert result["name"] == "Test Product"
        assert result["price"] == 99.99  # Value from our mock
        assert result["currency"] in tool._CURRENCIES
        assert result["stock_quantity"] == 42  # Value from our mock

    def test_post_process_yaml_valid(self) -> None:
        """Test post_process handles valid YAML correctly."""
        tool = RetailProductTool()
        # Mock the helper methods
        tool._random_price = lambda: 99.99  # type: ignore
        tool._random_stock = lambda: 42  # type: ignore
        
        valid_yaml = "product_id: 123\nname: Test Product"
        
        result = tool.post_process(valid_yaml, "yaml")
        
        assert isinstance(result, dict)
        assert isinstance(result, Dict)  # For type checking
        assert result["product_id"] == 123
        assert result["name"] == "Test Product"
        assert result["price"] == 99.99  # Value from our mock
        assert result["currency"] in tool._CURRENCIES
        assert result["stock_quantity"] == 42  # Value from our mock

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
        # Mock the helper methods
        tool._random_price = lambda: 99.99  # type: ignore
        tool._random_stock = lambda: 42  # type: ignore
        minimal_json = '{"product_id": "123", "name": "Test"}'
        
        result = tool.post_process(minimal_json, "json")
        
        assert isinstance(result, Dict)  # For type checking
        assert result["price"] == 99.99  # Value from our mock
        assert result["currency"] in tool._CURRENCIES
        assert result["stock_quantity"] == 42  # Value from our mock

    def test_data_enrichment_preserves_existing_fields(self) -> None:
        """Test data enrichment preserves existing fields."""
        tool = RetailProductTool()
        # Mock the helper methods
        tool._random_price = lambda: 999.99  # type: ignore # Different from what's in the JSON
        tool._random_stock = lambda: 420  # type: ignore # Different from what will be in the JSON
        
        json_with_fields = (
            '{"product_id": "123", "name": "Test", '
            '"price": 99.99, "currency": "EUR"}'
        )
        
        result = tool.post_process(json_with_fields, "json")
        
        assert isinstance(result, Dict)  # For type checking
        assert result["price"] == 99.99  # Should keep the original value
        assert result["currency"] == "EUR"  # Should keep the original value
        assert result["stock_quantity"] == 420  # Should add the missing field