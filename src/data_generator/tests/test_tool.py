"""
Tests for the data_generator.tool module.

Tests the DataGeneratorTool abstract class and its functionality.
"""

import argparse
import uuid
from typing import Any

import pytest

from data_generator.tool import DataGeneratorTool


class MockTool(DataGeneratorTool):
    """Mock implementation of DataGeneratorTool for testing."""

    name = "mock-tool"
    toolName = "MockTool"

    def build_prompt(
        self, output_format: str, *, unique_id: str | None = None
    ) -> str:
        """Return a test prompt for the specified output format."""
        return f"Generate a {output_format} sample with ID {unique_id or 'default'}"

    def cli_arguments(self) -> list[dict[str, Any]]:
        """Return test CLI arguments specification."""
        return [{"dest": "test_arg", "help": "Test argument"}]

    def validate_args(self, ns: argparse.Namespace) -> None:
        """Validate the CLI arguments."""
        pass

    def examples(self) -> list[str]:
        """Return usage examples."""
        return ["Example usage: mock-tool --test-arg value"]

    def get_system_description(self) -> str:
        """Return system description."""
        return "Mock tool system description"


class DuplicateMockTool(DataGeneratorTool):
    """Mock tool with duplicate name for testing registration validation."""

    name = "mock-tool"  # Same as MockTool
    toolName = "DuplicateMockTool"

    def build_prompt(
        self, output_format: str, *, unique_id: str | None = None
    ) -> str:
        return ""

    def cli_arguments(self) -> list[dict[str, Any]]:
        return []

    def validate_args(self, ns: argparse.Namespace) -> None:
        pass

    def examples(self) -> list[str]:
        return []

    def get_system_description(self) -> str:
        return ""


def test_tool_registry() -> None:
    """Test that tools are correctly registered in the registry."""
    # MockTool should be in the registry
    assert "mock-tool" in DataGeneratorTool._REGISTRY
    assert DataGeneratorTool._REGISTRY["mock-tool"] == MockTool


def test_tool_duplicate_registration() -> None:
    """Test that duplicate tool names are rejected."""
    with pytest.raises(
        ValueError, match="Duplicate tool registration for name 'mock-tool'"
    ):
        # This should raise ValueError due to duplicate name
        type(
            "TempDuplicateTool",
            (DataGeneratorTool,),
            {
                "name": "mock-tool",
                "toolName": "TempDuplicate",
                "build_prompt": lambda self, fmt, **_: "",
                "cli_arguments": lambda self: [],
                "validate_args": lambda self, ns: None,
                "examples": lambda self: [],
                "get_system_description": lambda self: "",
            },
        )


def test_tool_missing_name() -> None:
    """Test that tools without a name attribute are rejected."""
    with pytest.raises(
        AttributeError,
        match="DataGeneratorTool subclasses must define a unique `name` attribute",
    ):
        # This should raise AttributeError due to missing name
        type(
            "NoNameTool",
            (DataGeneratorTool,),
            {
                "toolName": "NoName",
                "build_prompt": lambda self, fmt, **_: "",
                "cli_arguments": lambda self: [],
                "validate_args": lambda self, ns: None,
                "examples": lambda self: [],
                "get_system_description": lambda self: "",
            },
        )


def test_from_name() -> None:
    """Test the from_name factory method."""
    tool = DataGeneratorTool.from_name("mock-tool")
    assert isinstance(tool, MockTool)
    assert tool.name == "mock-tool"
    assert tool.toolName == "MockTool"
    with pytest.raises(
        KeyError, match="No DataGeneratorTool registered with name 'non-existent'"
    ):
        DataGeneratorTool.from_name("non-existent")


def test_supported_output_formats() -> None:
    """Test the supported_output_formats method."""
    tool = MockTool()
    formats = tool.supported_output_formats()
    assert isinstance(formats, list)
    assert "json" in formats
    assert "yaml" in formats
    assert "txt" in formats


def test_get_unique_id() -> None:
    """Test the get_unique_id method."""
    tool = MockTool()
    unique_id = tool.get_unique_id()
    assert isinstance(unique_id, str)
    # Should be a valid UUID
    uuid_obj = uuid.UUID(unique_id)
    assert str(uuid_obj) == unique_id


def test_post_process_json() -> None:
    """Test the post_process method with JSON format."""
    tool = MockTool()
    json_str = '{"name": "Test", "value": 123}'

    # Test with output_format="json"
    result = tool.post_process(json_str, output_format="json")
    assert isinstance(result, dict)
    assert result["name"] == "Test"
    assert result["value"] == 123


def test_post_process_yaml() -> None:
    """Test the post_process method with YAML format."""
    tool = MockTool()
    yaml_str = "name: Test\nvalue: 123"

    # Test with output_format="yaml"
    result = tool.post_process(yaml_str, output_format="yaml")
    assert isinstance(result, dict)
    assert result["name"] == "Test"
    assert result["value"] == 123


def test_post_process_text() -> None:
    """Test the post_process method with text format."""
    tool = MockTool()
    text = "This is plain text"

    # Test with output_format="txt"
    result = tool.post_process(text, output_format="txt")
    assert isinstance(result, str)
    assert result == text


def test_post_process_invalid_json() -> None:
    """Test post_process with invalid JSON returns the raw string."""
    tool = MockTool()
    invalid_json = '{"name": "Test", value: 123}'  # Missing quotes around value

    # Should return the raw string when parsing fails
    result = tool.post_process(invalid_json, output_format="json")
    assert isinstance(result, str)
    assert result == invalid_json


def test_post_process_invalid_yaml() -> None:
    """Test post_process with invalid YAML returns the raw string."""
    tool = MockTool()
    invalid_yaml = "name: Test\n  value: 123"  # Invalid indentation

    # Should return the raw string when parsing fails
    result = tool.post_process(invalid_yaml, output_format="yaml")
    assert isinstance(result, str)
    assert result == invalid_yaml


def test_post_process_unsupported_format() -> None:
    """Test post_process with an unsupported format returns the raw string."""
    tool = MockTool()
    text = "Some text"

    # Should return the raw string for unsupported formats
    result = tool.post_process(text, output_format="unsupported")
    assert isinstance(result, str)
    assert result == text
