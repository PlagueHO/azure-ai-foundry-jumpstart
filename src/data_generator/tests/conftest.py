"""
Common pytest fixtures for data_generator tests.

Provides mocked Semantic Kernel instances and other utilities needed by tests.
"""

import os
from collections.abc import Generator
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from semantic_kernel.kernel import Kernel


@pytest.fixture
def temp_output_dir(tmp_path) -> Path:
    """Return a temporary directory Path for test outputs."""
    return tmp_path / "output"


@pytest.fixture
def mock_kernel() -> Generator[MagicMock, None, None]:
    """
    Provide a mocked Semantic Kernel that doesn't make actual Azure calls.

    The kernel has a predefined add_function that returns a mock KernelFunction.
    """
    mock = MagicMock(spec=Kernel)

    # Create a mock KernelFunction that returns predefined text
    mock_kernel_function = MagicMock()
    mock_kernel_function.invoke.return_value = "Mocked completion result"

    # Set up add_function to return our mock_kernel_function
    mock.add_function.return_value = mock_kernel_function

    with patch("semantic_kernel.Kernel", return_value=mock):
        yield mock


@pytest.fixture
def mock_env_vars() -> Generator[dict[str, str], None, None]:
    """
    Set up mock environment variables for testing.

    This fixture ensures Azure OpenAI credentials are available during tests
    without requiring actual credentials.
    """
    mock_vars = {
        "AZURE_OPENAI_ENDPOINT": "https://mock-endpoint.openai.azure.com",
        "AZURE_OPENAI_DEPLOYMENT": "mock-deployment",
        "AZURE_OPENAI_API_KEY": "mock-api-key",
    }

    # Save original environment
    original_env = {}
    for key in mock_vars:
        original_env[key] = os.environ.get(key)

    # Set mock environment variables
    for key, value in mock_vars.items():
        os.environ[key] = value

    yield mock_vars

    # Restore original environment
    for key, value in original_env.items():
        if value is None:
            if key in os.environ:
                del os.environ[key]
        else:
            os.environ[key] = value
