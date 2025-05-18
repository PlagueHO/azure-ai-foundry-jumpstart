"""
Retail-Product Prompt Builder
=============================

Concrete :class:`data_generator.tool.DataGeneratorTool` implementation that
creates realistic retail-product catalogue entries.
"""

from __future__ import annotations

import argparse
import json
import logging
import random
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

import yaml

from ..tool import DataGeneratorTool

_logger = logging.getLogger(__name__)


class RetailProductTool(DataGeneratorTool):
    """Generate synthetic retail-product catalogue items."""

    # ------------------------------------------------------------------ #
    # Identification / registry key                                      #
    # ------------------------------------------------------------------ #
    name: str = "retail-product"
    toolName: str = "RetailProduct"
    
    # ------------------------------------------------------------------ #
    # Output formats                                                     #
    # ------------------------------------------------------------------ #
    def supported_output_formats(self) -> List[str]:
        """Return the list of output formats this tool can generate."""
        return ["yaml", "json", "text"]

    # ------------------------------------------------------------------ #
    # CLI contract                                                       #
    # ------------------------------------------------------------------ #
    def __init__(self, *, industry: str | None = None) -> None:
        """Create a new tool instance with an optional *industry* override."""
        super().__init__()
        self.industry = industry or "general"

    def cli_arguments(self) -> List[Dict[str, Any]]:
        """Argparse specification consumed by the top-level CLI wrapper."""
        return [
            {
                "flags": ["-i", "--industry"],
                "kwargs": {
                    "required": False,
                    "metavar": "TEXT",
                    "default": "general",
                    "help": "Industry/theme for the products (e.g. electronics, fashion).",
                },
            }
        ]

    def validate_args(self, ns: argparse.Namespace) -> None:
        """Persist validated CLI arguments onto the instance."""
        self.industry = ns.industry or "general"

    def examples(self) -> List[str]:
        """Representative usage snippets for `--help` output."""
        return [
            "python -m generate_data "
            "--scenario retail-product "
            "--count 100 "
            "--industry electronics "
            "--output-format json"
        ]

    # ------------------------------------------------------------------ #
    # Prompt construction                                                #
    # ------------------------------------------------------------------ #
    _CURRENCIES: List[str] = ["USD", "EUR", "GBP", "AUD", "CAD"]

    @staticmethod
    def _random_price() -> float:
        """Return a random realistic product price."""
        return round(random.uniform(5.0, 500.0), 2)

    @staticmethod
    def _random_stock() -> int:
        """Return a random realistic stock quantity."""
        return random.randint(0, 500)

    def _prompt_common(self) -> str:
        """Common immutable prompt section shared by all output formats."""
        product_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        return (
            f"Product ID (immutable): {product_id}\n"
            f"Created At: {created_at}\n"
            f"Industry Theme: {self.industry}\n\n"
        )

    def build_prompt(self, output_format: str) -> str:
        """Return the full prompt for the requested *output_format*."""
        base = (
            "You are a seasoned e-commerce copy-writer producing REALISTIC BUT "
            "ENTIRELY FICTIONAL retail-product catalogue entries.\n\n"
            f"{self._prompt_common()}"
            "Always output ONLY the requested data structure – no markdown fences, "
            "no commentary.\n\n"
        )

        if output_format == "yaml":
            return base + self._yaml_skeleton()
        if output_format == "json":
            return base + self._json_skeleton()
        # TEXT
        return base + self._text_skeleton()

    # ------------------------------------------------------------------ #
    # Static prompt fragments                                            #
    # ------------------------------------------------------------------ #
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

    @staticmethod
    def _text_skeleton() -> str:
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

    # ------------------------------------------------------------------ #
    # Post-processing                                                    #
    # ------------------------------------------------------------------ #
    def post_process(self, raw: str) -> Any:  # noqa: ANN401
        """Attempt to enrich & deserialize where applicable."""
        data: Any = raw
        if raw.lstrip().startswith("{"):
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                return raw
        elif ":" in raw and "\n" in raw:
            try:
                data = yaml.safe_load(raw)
            except yaml.YAMLError:
                return raw

        # Enrich JSON/YAML outputs with defaults (price/stock/currency/rating)
        if isinstance(data, dict):
            data.setdefault("price", self._random_price())
            data.setdefault("currency", random.choice(self._CURRENCIES))
            data.setdefault("stock_quantity", self._random_stock())
            if "rating" not in data and random.choice([True, False]):
                data["rating"] = round(random.uniform(1.0, 5.0), 1)
        return data

    # ------------------------------------------------------------------ #
    # Misc.                                                              #
    # ------------------------------------------------------------------ #
    def get_system_description(self) -> str:
        """Return a sentence describing the target retail catalogue."""
        return f"Retail catalogue for {self.industry} products"
