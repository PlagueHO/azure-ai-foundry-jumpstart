"""
Pytest fixtures for create_ai_search_index tests.
"""
import pytest
from create_ai_search_index.engine import CreateAISearchIndex, CreateAISearchIndexConfig

@pytest.fixture
def sample_config() -> CreateAISearchIndexConfig:
    """Return a sample CreateAISearchIndexConfig for testing."""
    return CreateAISearchIndexConfig(
        storage_account="testaccount",
        storage_container="testcontainer",
        search_service="testsearch",
        index_name="testindex"
    )

@pytest.fixture
def engine(sample_config: CreateAISearchIndexConfig) -> CreateAISearchIndex:
    """Return a CreateAISearchIndex instance for testing."""
    return CreateAISearchIndex(sample_config)
