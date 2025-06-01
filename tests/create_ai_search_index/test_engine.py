"""
Unit tests for the create_ai_search_index.engine module.
"""


import pytest
from pytest import MonkeyPatch
from create_ai_search_index.engine import CreateAISearchIndex, CreateAISearchIndexConfig

def test_config_properties(sample_config: CreateAISearchIndexConfig) -> None:
    """Test CreateAISearchIndexConfig properties."""
    assert sample_config.search_endpoint == "https://testsearch.search.windows.net"

def test_engine_init(engine: CreateAISearchIndex) -> None:
    """Test CreateAISearchIndex initialization."""
    assert engine.cfg.index_name == "testindex"

def test_engine_run(monkeypatch: MonkeyPatch, engine: CreateAISearchIndex) -> None:
    """Test CreateAISearchIndex.run method with all internals monkeypatched."""
    monkeypatch.setattr(engine, "_teardown_pipeline", lambda: None)
    monkeypatch.setattr(engine, "_ensure_index_schema", lambda: None)
    monkeypatch.setattr(engine, "_ensure_data_source", lambda: None)
    monkeypatch.setattr(engine, "_ensure_skillset", lambda: None)
    monkeypatch.setattr(engine, "_ensure_indexer", lambda: None)
    monkeypatch.setattr(engine, "_run_indexer", lambda: None)
    # Should not raise
    engine.run()

@pytest.mark.parametrize("method_name", [
    "_ensure_index_schema",
    "_ensure_data_source",
    "_ensure_skillset",
    "_ensure_indexer",
    "_run_indexer",
    "_teardown_pipeline",
])
def test_engine_methods_stub(
    monkeypatch: MonkeyPatch, engine: CreateAISearchIndex, method_name: str
) -> None:
    """Test that each internal method can be called without error when stubbed."""
    monkeypatch.setattr(engine, method_name, lambda: None)
    getattr(engine, method_name)()

def test_config_repr(sample_config: CreateAISearchIndexConfig) -> None:
    """Test the __repr__ of the config for coverage."""
    assert "testindex" in repr(sample_config)