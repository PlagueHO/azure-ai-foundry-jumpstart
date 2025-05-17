"""
Generate sample retail-product catalogue items using Azure OpenAI via Semantic Kernel.

Example:
python scripts/generators/generate_retail_product.py -n 100 -i electronics -o ./sample-data/retail-product/

Prerequisites
-------------
1. pip install semantic-kernel python-dotenv pyyaml colorama
2. Provide Azure OpenAI env-vars in .env:
   AZURE_OPENAI_ENDPOINT="https://<your-endpoint>.openai.azure.com/"
   AZURE_OPENAI_DEPLOYMENT="<deployment-name>"
   AZURE_OPENAI_API_KEY="<api-key>"
"""

from __future__ import annotations
import argparse
import os
import uuid
import random
# asyncio is handled by SyntheticDataGenerator
import json
# logging is handled by SyntheticDataGenerator
import datetime as _dt
from pathlib import Path
from typing import Final # Tuple is not used directly here anymore

import yaml
# dotenv, semantic_kernel, AzureChatCompletion, PromptTemplateConfig are handled by SyntheticDataGenerator
from colorama import Fore, Style # Keep for coloring output messages

from synthetic_data_generator import SyntheticDataGenerator # Import the new helper class

# -------------------------------------------------------------------------
# ENV & OpenAI setup - Handled by SyntheticDataGenerator
# -------------------------------------------------------------------------
# load_dotenv() and AZURE_OPENAI_... variables are removed.

# -------------------------------------------------------------------------
# CLI
# -------------------------------------------------------------------------
parser = argparse.ArgumentParser(description="Generate retail product sample data.")
parser.add_argument("-i", "--industry", default="general", help="Industry / theme for products (e.g. electronics, fashion).")
parser.add_argument("-n", "--count",   type=int, default=1, help="Number of products to generate.")
parser.add_argument("-o", "--output",  type=Path, default=Path(__file__).parent / "output", help="Output folder.")
parser.add_argument("-f", "--format",  choices=["yaml", "json", "text"], default="yaml", help="Output format.")
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------------------
# SyntheticDataGenerator setup
# -------------------------------------------------------------------------
# _create_kernel(), kernel, _create_prompt_function() are removed.
# Logging setup is also removed.
generator = SyntheticDataGenerator()
log = generator.logger # Use the logger from the generator instance (aliased as 'log' as per original)

# -------------------------------------------------------------------------
# Prompt templates (Remains script-specific)
# -------------------------------------------------------------------------
def _build_prompt(fmt: str) -> str:
    base = """
You are a seasoned e-commerce copy-writer producing realistic product catalogue entries.
Target industry/theme: {{$industry}}
Always output ONLY the requested data structure, no extra commentary or markdown.
"""
    if fmt == "yaml":
        return base + """
Return valid YAML with the following schema:

product_id: {{$product_id}}
created_at: {{$created_at}}
name: catchy product name
category: sub-category relevant to {{$industry}}
description: persuasive paragraph (60-120 words)
price: realistic decimal number > 1
currency: ISO 4217 e.g. USD
tags: [list, of, keywords]
attributes:
  key: value pairs (e.g. colour: red, size: L)
stock_quantity: integer 0-500
rating: float 0-5 with one decimal (optional)

Do NOT wrap in ```yaml.
"""
    if fmt == "json":
        return base + """
{
  "product_id": "{{$product_id}}",
  "created_at": "{{$created_at}}",
  "name": "Product name",
  "category": "Relevant sub-category",
  "description": "60-120 word paragraph",
  "price": 123.45,
  "currency": "USD",
  "tags": ["tag1","tag2"],
  "attributes": {"key":"value"},
  "stock_quantity": 123,
  "rating": 4.6
}
Return ONLY the JSON.
"""
    # plain text fallback
    return base + """
Product ID: {{$product_id}}
Created At: {{$created_at}}
Name: Product name
Category: Relevant sub-category
Description: 60-120 word paragraph
Price: 123.45 USD
Tags: tag1, tag2
Attributes:
  key: value
Stock Quantity: 123
Rating: 4.6
"""

PROMPT_TEMPLATE_STRING = _build_prompt(args.format)
prompt_function = generator.create_prompt_function(
    template=PROMPT_TEMPLATE_STRING,
    function_name="generate_product",
    plugin_name="retail_product",
    prompt_description="Create realistic retail product entry",
    input_variables=[
        {"name": "industry",    "description": "Product theme", "is_required": True},
        {"name": "product_id",  "description": "UUID",          "is_required": True},
        {"name": "created_at",  "description": "ISO timestamp", "is_required": True},
    ],
    max_tokens=600
)

# -------------------------------------------------------------------------
# Logging (Handled by SyntheticDataGenerator, colorama import kept for messages)
# -------------------------------------------------------------------------
# import colorama, yaml (yaml still needed for parsing)
# colorama.init(autoreset=True) is removed.
# logging.basicConfig and log = logging.getLogger(__name__) are removed.

# -------------------------------------------------------------------------
# Random helpers (Remains script-specific)
# -------------------------------------------------------------------------
CURRENCIES: Final[list[str]] = ["USD","EUR","GBP","AUD","CAD"]
def _random_price() -> float: return round(random.uniform(5.0, 500.0), 2)
def _random_stock() -> int:   return random.randint(0, 500)
def _random_rating() -> float | None: # Allow None for optional rating
    if random.choice([True, False]): # Make it truly optional
        return round(random.uniform(1.0, 5.0),1)
    return None

# -------------------------------------------------------------------------
# Generation loop (Remains script-specific)
# -------------------------------------------------------------------------
def generate_products(count:int, out_dir:Path, industry:str):
    required_fields_json_yaml = {"product_id", "created_at", "name", "category", "description"} # Basic fields expected from LLM

    for idx in range(1, count + 1):
        product_id  = str(uuid.uuid4())
        created_at  = _dt.datetime.now(_dt.timezone.utc).isoformat()
        
        output: str = ""
        data: dict | None = None # For YAML/JSON

        for attempt in range(1, 4):
            log.debug(f"Attempt {attempt}/3 for product {idx}/{count}")
            output = prompt_function(
                industry=industry,
                product_id=product_id,
                created_at=created_at
            ).strip()

            try:
                if args.format == "yaml":
                    data = yaml.safe_load(output)
                elif args.format == "json":
                    data = json.loads(output)
                else: # text format
                    break # No further validation needed for text

                if not isinstance(data, dict):
                    raise ValueError(f"Output is not a dictionary. Got: {type(data)}")
                if not required_fields_json_yaml.issubset(data.keys()):
                    missing = required_fields_json_yaml - set(data.keys())
                    raise ValueError(f"Missing core fields from LLM: {', '.join(missing)}")
                break # Success
            except Exception as e:
                log.error(f"Raw output on error (attempt {attempt}):\n---\n{output}\n---")
                if attempt < 3:
                    log.warning(f"Attempt {attempt}/3 failed for product {idx} - retrying: {e}")
                else:
                    log.error(f"All 3 attempts failed for product {idx}. Error: {e}")
                    # Skip this product if all attempts fail
                    output = "" # Ensure output is empty if all attempts failed
                    data = None
                    break # Break from retry loop

        if not output and args.format != "text": # If all attempts failed for JSON/YAML
            log.error(f"Skipping product {idx} due to persistent errors.")
            continue

        generated_at = _dt.datetime.now(_dt.timezone.utc).isoformat()
        ext = {"yaml":"yaml","json":"json","text":"txt"}[args.format]
        file_path = out_dir / f"{product_id}.{ext}"

        with file_path.open("w",encoding="utf-8") as fp:
            if args.format == "yaml":
                if data: # Ensure data is not None
                    # Enrich with random price/stock if not present or if they are placeholders
                    data.setdefault("price", _random_price())
                    data.setdefault("currency", random.choice(CURRENCIES))
                    data.setdefault("stock_quantity", _random_stock())
                    rating = _random_rating()
                    if rating is not None: data.setdefault("rating", rating)
                    data["generated_at"] = generated_at
                    yaml.safe_dump(data, fp, sort_keys=False)
            elif args.format == "json":
                if data: # Ensure data is not None
                    data.setdefault("price", _random_price())
                    data.setdefault("currency", random.choice(CURRENCIES))
                    data.setdefault("stock_quantity", _random_stock())
                    rating = _random_rating()
                    if rating is not None: data.setdefault("rating", rating)
                    data["generated_at"] = generated_at
                    json.dump(data, fp, indent=2)
            else: # text
                fp.write(f"{output}\nGenerated At: {generated_at}\n") # output is already stripped
        log.info("%s✔ Generated %s%s", Fore.GREEN, file_path, Style.RESET_ALL)

# -------------------------------------------------------------------------
if __name__ == "__main__":
    log.info(f"Starting generation of {args.count} retail product(s) for industry '{args.industry}'...")
    generate_products(args.count, args.output, args.industry)
    log.info("Generation complete.")
