"""
Command-line interface for the create_ai_search_index package.

Usage (once the project is installed in the active Python environment):

    create_ai_search_index --storage-account mystorage --storage-container docs \
        --search-service mysearch --index-name myindex

This script parses CLI arguments, validates them, and invokes the CreateSearchIndex engine.
"""

import argparse
import sys
from .engine import CreateAISearchIndex, CreateAISearchIndexConfig

from typing import List, Optional

def main(argv: Optional[List[str]] = None):
    """
    Main entry point for the create_ai_search_index CLI.

    Parses command-line arguments, constructs the CreateSearchIndexConfig dataclass,
    and invokes the CreateSearchIndex engine. Exits with code 1 on error.

    Args:
        argv (list, optional): List of arguments to parse. Defaults to sys.argv[1:].
    """
    parser = argparse.ArgumentParser(
        prog="create_ai_search_index",
        description="Azure AI Search index pipeline builder for RAG scenarios.",
    )
    parser.add_argument("--storage-account", required=True, help="Azure Storage account name.")
    parser.add_argument("--storage-container", required=True, help="Blob container with documents.")
    parser.add_argument("--search-service", required=True, help="Azure AI Search service name.")
    parser.add_argument("--index-name", required=True, help="Name of the search index to create or update.")
    parser.add_argument("--azure-openai-endpoint", help="Azure OpenAI endpoint URL.")
    parser.add_argument("--embedding-model", help="Azure OpenAI embedding model name.")
    parser.add_argument("--embedding-deployment", help="Azure OpenAI embedding deployment name.")
    parser.add_argument("--delete-existing", action="store_true", help="Delete and re-create pipeline resources if they exist.")
    # ...add more arguments as needed (chunk-size, overlap, etc.)...

    args = parser.parse_args(argv or sys.argv[1:])

    config = CreateAISearchIndexConfig(
        storage_account=args.storage_account,
        storage_container=args.storage_container,
        search_service=args.search_service,
        index_name=args.index_name,
        azure_openai_endpoint=args.azure_openai_endpoint,
        embedding_model=args.embedding_model,
        embedding_deployment=args.embedding_deployment,
        delete_existing=args.delete_existing,
    )

    try:
        CreateAISearchIndex(config).run()
    except Exception as ex:
        print(f"ERROR: {ex}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
