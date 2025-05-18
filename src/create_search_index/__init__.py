"""
create_search_index
===================

Synchronous, secure builder for Azure AI Search indexing pipelines.
"""

from .engine import CreateSearchIndex, CreateSearchIndexConfig

__all__: list[str] = ["CreateSearchIndex", "CreateSearchIndexConfig"]
