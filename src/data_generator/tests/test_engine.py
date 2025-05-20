"""
Tests for the data_generator.engine module.

Tests the DataGenerator class and its core functionality.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch, call, AsyncMock

import pytest
import yaml
from semantic_kernel.prompt_template import PromptTemplateConfig

from data_generator.engine import DataGenerator
from data_generator.tool import DataGeneratorTool


class SimpleTestTool(DataGeneratorTool):
    """Simple implementation of DataGeneratorTool for testing."""

    name = "test-tool"
    toolName = "TestTool"

    def build_prompt(self, output_format: str, *, unique_id: str | None = None) -> str:
        """Return a test prompt for the specified output format."""
        return f"Generate a {output_format} sample with ID {unique_id or 'default'}"

    def cli_arguments(self) -> List[Dict[str, Any]]:
        """Return test CLI arguments specification."""
        return [
            {"dest": "test_arg", "help": "Test argument"}
        ]

    def validate_args(self, ns: Any) -> None:
        """Validate the CLI arguments."""
        pass

    def examples(self) -> List[str]:
        """Return usage examples."""
        return ["Example usage: test-tool --test-arg value"]

    def get_system_description(self) -> str:
        """Return system description."""
        return "Test tool system description"


def test_env_or_override():
    """Test the _env_or_override static method."""
    # Test with override provided
    assert (
        DataGenerator._env_or_override("override-value", "NON_EXISTENT_ENV")
        == "override-value"
    )

    # Test with no override, should use env var
    with patch.dict("os.environ", {"TEST_ENV_VAR": "env-value"}):
        assert DataGenerator._env_or_override(None, "TEST_ENV_VAR") == "env-value"

    # Test with no override and no env var
    assert DataGenerator._env_or_override(None, "NON_EXISTENT_ENV") is None


def test_init_with_explicit_params():
    """Test initialization with explicit parameters."""
    tool = SimpleTestTool()
    generator = DataGenerator(
        tool,
        azure_openai_endpoint="https://test-endpoint.openai.azure.com",
        azure_openai_deployment="test-deployment",
        azure_openai_api_key="test-api-key"
    )

    assert generator.tool == tool
    assert generator.azure_openai_endpoint == "https://test-endpoint.openai.azure.com"
    assert generator.azure_openai_deployment == "test-deployment"
    assert generator.azure_openai_api_key == "test-api-key"


def test_init_with_env_vars(mock_env_vars):
    """Test initialization using environment variables."""
    tool = SimpleTestTool()
    generator = DataGenerator(tool)

    assert generator.tool == tool
    assert generator.azure_openai_endpoint == mock_env_vars["AZURE_OPENAI_ENDPOINT"]
    assert generator.azure_openai_deployment == mock_env_vars["AZURE_OPENAI_DEPLOYMENT"]
    assert generator.azure_openai_api_key == mock_env_vars["AZURE_OPENAI_API_KEY"]


def test_init_missing_required_vars():
    """Test initialization fails when required variables are missing."""
    tool = SimpleTestTool()

    # Clear environment variables
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(
            EnvironmentError,
            match="Azure OpenAI endpoint and deployment must be specified"
        ):
            DataGenerator(tool)


def test_create_kernel(mock_kernel):
    """Test the _create_kernel method."""
    tool = SimpleTestTool()

    with patch("semantic_kernel.Kernel", return_value=mock_kernel):
        generator = DataGenerator(
            tool,
            azure_openai_endpoint="https://test-endpoint.openai.azure.com",
            azure_openai_deployment="test-deployment",
            azure_openai_api_key="test-api-key"
        )

        kernel = generator._create_kernel()
        assert kernel == mock_kernel


@pytest.mark.parametrize("api_key", ["test-api-key", None])
def test_create_kernel_auth_methods(api_key, mock_kernel):
    """Test _create_kernel with different authentication methods."""
    tool = SimpleTestTool()

    with patch("semantic_kernel.Kernel", return_value=mock_kernel):
        with patch("data_generator.engine.AzureChatCompletion") as mock_chat_completion:
            generator = DataGenerator(
                tool,
                azure_openai_endpoint="https://test-endpoint.openai.azure.com",
                azure_openai_deployment="test-deployment",
                azure_openai_api_key=api_key
            )

            generator._create_kernel()

            # Verify the correct authentication method is used
            if api_key:
                # Should use API key
                mock_chat_completion.assert_called_once()
                _, kwargs = mock_chat_completion.call_args
                assert "api_key" in kwargs
            else:
                # Should use DefaultAzureCredential
                mock_chat_completion.assert_called_once()
                _, kwargs = mock_chat_completion.call_args
                assert "token_provider" in kwargs


def test_create_prompt_function(mock_kernel):
    """Test the create_prompt_function method."""
    tool = SimpleTestTool()

    with patch("semantic_kernel.Kernel", return_value=mock_kernel):
        generator = DataGenerator(
            tool,
            azure_openai_endpoint="https://test-endpoint.openai.azure.com",
            azure_openai_deployment="test-deployment",
            azure_openai_api_key="test-api-key"
        )

        prompt_fn = generator.create_prompt_function(
            template="Test template with {{$index}}",
            function_name="test_function",
            plugin_name="test_plugin",
            prompt_description="Test description",
            input_variables=[{"name": "index", "description": "Index value"}],
            max_tokens=100
        )

        # Verify the function was created and kernel.add_function was called
        assert callable(prompt_fn)
        mock_kernel.add_function.assert_called_once()

        # Test calling the function
        result = prompt_fn(index=1)
        assert result == "Mocked completion result"


@pytest.mark.asyncio
async def test_run(mock_kernel, temp_output_dir):
    """Test the run method."""
    tool = SimpleTestTool()

    with patch("semantic_kernel.Kernel", return_value=mock_kernel):
        generator = DataGenerator(
            tool,
            azure_openai_endpoint="https://test-endpoint.openai.azure.com",
            azure_openai_deployment="test-deployment",
            azure_openai_api_key="test-api-key"
        )

        # Mock the _run_async method
        with patch.object(
            generator, "_run_async", new_callable=AsyncMock
        ) as mock_run_async:
            # Create the output directory
            temp_output_dir.mkdir(exist_ok=True)

            # Run the method
            generator.run(
                count=5,
                out_dir=temp_output_dir,
                output_format="json",
                concurrency=4,
                timeout_seconds=30.0
            )

            # Verify _run_async was called with the correct parameters
            mock_run_async.assert_awaited_once_with(
                count=5,
                out_dir=temp_output_dir,
                output_format="json",
                concurrency=4,
                timeout_seconds=30.0
            )


@pytest.mark.asyncio
async def test_run_async(mock_kernel, temp_output_dir):
    """Test the _run_async method."""
    tool = SimpleTestTool()

    with patch("semantic_kernel.Kernel", return_value=mock_kernel):
        generator = DataGenerator(
            tool,
            azure_openai_endpoint="https://test-endpoint.openai.azure.com",
            azure_openai_deployment="test-deployment",
            azure_openai_api_key="test-api-key"
        )

        # Mock _generate_one_async to avoid actual generation
        with patch.object(
            generator, "_generate_one_async", new_callable=AsyncMock
        ) as mock_generate:
            # Create the output directory
            temp_output_dir.mkdir(exist_ok=True)

            # Run the method - with a small count to keep the test fast
            await generator._run_async(
                count=3,
                out_dir=temp_output_dir,
                output_format="json",
                concurrency=2,
                timeout_seconds=None
            )

            # Verify _generate_one_async was called for each count
            assert mock_generate.await_count == 3

            # Verify the calls had the correct parameters
            expected_calls = [
                call(
                    index=1,
                    out_dir=temp_output_dir,
                    output_format="json",
                    semaphore=pytest.ANY
                ),
                call(
                    index=2,
                    out_dir=temp_output_dir,
                    output_format="json",
                    semaphore=pytest.ANY
                ),
                call(
                    index=3,
                    out_dir=temp_output_dir,
                    output_format="json",
                    semaphore=pytest.ANY
                ),
            ]
            mock_generate.assert_has_awaits(expected_calls, any_order=True)


def test_generate_data(mock_kernel, temp_output_dir):
    """Test the generate_data method."""
    tool = SimpleTestTool()

    with patch("semantic_kernel.Kernel", return_value=mock_kernel):
        generator = DataGenerator(
            tool,
            azure_openai_endpoint="https://test-endpoint.openai.azure.com",
            azure_openai_deployment="test-deployment",
            azure_openai_api_key="test-api-key"
        )

        # Mock the run method
        with patch.object(generator, "run") as mock_run:
            # Create the output directory
            temp_output_dir.mkdir(exist_ok=True)

            # Call generate_data
            generator.generate_data(
                count=10,
                out_dir=temp_output_dir,
                output_format="json"
            )

            # Verify run was called with default concurrency and timeout
            mock_run.assert_called_once_with(
                count=10,
                out_dir=temp_output_dir,
                output_format="json",
                concurrency=8,
                timeout_seconds=300.0
            )


def test_persist_json(temp_output_dir):
    """Test the _persist method with JSON output."""
    tool = SimpleTestTool()
    generator = DataGenerator(
        tool,
        azure_openai_endpoint="https://test-endpoint.openai.azure.com",
        azure_openai_deployment="test-deployment",
        azure_openai_api_key="test-api-key"
    )

    # Create the output directory
    temp_output_dir.mkdir(exist_ok=True)

    # Test data to persist
    data = {"name": "Test", "value": 123}

    # Call _persist
    generator._persist(
        data=data,
        out_dir=temp_output_dir,
        output_format="json",
        unique_id="test-id",
        index=1
    )

    # Verify the file was created
    expected_file = temp_output_dir / "test-id.json"
    assert expected_file.exists()

    # Verify the content
    with open(expected_file, "r") as f:
        content = json.load(f)
        assert content == data


def test_persist_yaml(temp_output_dir):
    """Test the _persist method with YAML output."""
    tool = SimpleTestTool()
    generator = DataGenerator(
        tool,
        azure_openai_endpoint="https://test-endpoint.openai.azure.com",
        azure_openai_deployment="test-deployment",
        azure_openai_api_key="test-api-key"
    )

    # Create the output directory
    temp_output_dir.mkdir(exist_ok=True)

    # Test data to persist
    data = {"name": "Test", "value": 123}

    # Call _persist
    generator._persist(
        data=data,
        out_dir=temp_output_dir,
        output_format="yaml",
        unique_id="test-id",
        index=1
    )

    # Verify the file was created
    expected_file = temp_output_dir / "test-id.yaml"
    assert expected_file.exists()

    # Verify the content
    with open(expected_file, "r") as f:
        content = yaml.safe_load(f)
        assert content == data


def test_persist_txt(temp_output_dir):
    """Test the _persist method with text output."""
    tool = SimpleTestTool()
    generator = DataGenerator(
        tool,
        azure_openai_endpoint="https://test-endpoint.openai.azure.com",
        azure_openai_deployment="test-deployment",
        azure_openai_api_key="test-api-key"
    )

    # Create the output directory
    temp_output_dir.mkdir(exist_ok=True)

    # Test data to persist (plain text)
    data = "This is plain text content"

    # Call _persist
    generator._persist(
        data=data,
        out_dir=temp_output_dir,
        output_format="txt",
        unique_id="test-id",
        index=1
    )

    # Verify the file was created
    expected_file = temp_output_dir / "test-id.txt"
    assert expected_file.exists()

    # Verify the content
    with open(expected_file, "r") as f:
        content = f.read()
        assert content == data
