"""
Unit tests for the cli.py module in create_ai_search_index package.
"""

import sys
from unittest.mock import patch, MagicMock
import pytest

# Patch sys.argv and dependencies for CLI tests

@patch("create_ai_search_index.cli.CreateAISearchIndex")
def test_cli_main_success(mock_engine: MagicMock, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test main() runs successfully with required arguments."""
    from create_ai_search_index import cli
    # Prepare mock engine
    mock_instance = MagicMock()
    mock_engine.return_value = mock_instance
    # Prepare arguments
    argv = [
        "--storage-account", "acct",
        "--storage-container", "cont",
        "--search-service", "svc",
        "--index-name", "idx"
    ]
    monkeypatch.setattr(sys, "argv", ["prog"] + argv)
    cli.main()
    mock_engine.assert_called_once()
    mock_instance.run.assert_called_once()

@patch("create_ai_search_index.cli.CreateAISearchIndex")
def test_cli_main_with_all_args(mock_engine: MagicMock, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test main() with all optional arguments."""
    from create_ai_search_index import cli
    mock_instance = MagicMock()
    mock_engine.return_value = mock_instance
    argv = [
        "--storage-account", "acct",
        "--storage-container", "cont",
        "--search-service", "svc",
        "--index-name", "idx",
        "--azure-openai-endpoint", "https://example.com",
        "--embedding-model", "model",
        "--embedding-deployment", "deploy",
        "--delete-existing"
    ]
    monkeypatch.setattr(sys, "argv", ["prog"] + argv)
    cli.main()
    mock_engine.assert_called_once()
    mock_instance.run.assert_called_once()
    # Check config values
    config = mock_engine.call_args[0][0]
    assert config.azure_openai_endpoint == "https://example.com"
    assert config.embedding_model == "model"
    assert config.embedding_deployment == "deploy"
    assert config.delete_existing is True

@patch("create_ai_search_index.cli.CreateAISearchIndex")
def test_cli_main_runtime_error(
    mock_engine: MagicMock, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test main() handles RuntimeError and exits with code 1."""
    from create_ai_search_index import cli
    mock_instance = MagicMock()
    mock_instance.run.side_effect = RuntimeError("fail")
    mock_engine.return_value = mock_instance
    argv = [
        "--storage-account", "acct",
        "--storage-container", "cont",
        "--search-service", "svc",
        "--index-name", "idx"
    ]
    monkeypatch.setattr(sys, "argv", ["prog"] + argv)
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "ERROR: fail" in captured.err

@pytest.mark.parametrize("missing_arg,expected", [
    ("--storage-account", "storage_account"),
    ("--storage-container", "storage_container"),
    ("--search-service", "search_service"),
    ("--index-name", "index_name"),
])
def test_cli_main_missing_required(
    monkeypatch: pytest.MonkeyPatch, missing_arg: str, expected: str
) -> None:
    """Test main() exits with error if required argument is missing."""
    from create_ai_search_index import cli
    argv = [
        "--storage-account", "acct",
        "--storage-container", "cont",
        "--search-service", "svc",
        "--index-name", "idx"
    ]
    # Remove the required argument
    idx = argv.index(missing_arg)
    del argv[idx : idx + 2]
    monkeypatch.setattr(sys, "argv", ["prog"] + argv)
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code != 0
