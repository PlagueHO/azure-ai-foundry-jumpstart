"""
Minimal pytest fixtures for data_generator tests.
"""

import pytest
from pathlib import Path


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """Return a temporary directory Path for test outputs."""
    return tmp_path / "output"
