"""
Generate sample retail-product catalogue items using Azure OpenAI via Semantic Kernel.

Example:
python scripts/generators/generate-retail-product.py -n 100 -i electronics -o ./sample-data/retail-product/

Prerequisites
-------------
1. pip install semantic-kernel python-dotenv pyyaml
2. Provide Azure OpenAI env-vars in .env:
   AZURE_OPENAI_ENDPOINT="https://<your-endpoint>.openai.azure.com/"
   AZURE_OPENAI_DEPLOYMENT="<deployment-name>"
   AZURE_OPENAI_API_KEY="<api-key>"
"""

from __future__ import annotations
# ...existing imports block identical to the tech-support script...
import argparse, os, uuid, random, asyncio, json, logging, datetime as _dt
from pathlib import Path
from typing import Final, Tuple

import yaml
from dotenv import load_dotenv
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.prompt_template import PromptTemplateConfig
from colorama import Fore, Style
# -------------------------------------------------------------------------
# ENV & OpenAI setup (identical to tech-support script)
# -------------------------------------------------------------------------
load_dotenv()
load_dotenv(".env", override=True)
AZURE_OPENAI_ENDPOINT     = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT   = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_API_KEY      = os.getenv("AZURE_OPENAI_API_KEY")
if not all([AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_API_KEY]):
    raise EnvironmentError("Azure OpenAI environment variables are not fully configured.")

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
# Kernel
# -------------------------------------------------------------------------
def _create_kernel() -> sk.Kernel:
    k = sk.Kernel()
    k.add_service(AzureChatCompletion(
        deployment_name=AZURE_OPENAI_DEPLOYMENT,
        endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        service_id="azure_open_ai",
    ))
    return k
kernel = _create_kernel()

# -------------------------------------------------------------------------
# Prompt helpers
# -------------------------------------------------------------------------
def _create_prompt_function(kernel: sk.Kernel, template: str, *, max_tokens: int = 600):
    """
    Build an inline prompt-function.
    Returns a sync wrapper that can be called like a normal function.
    """

    # 1. Prompt-template configuration
    prompt_cfg = PromptTemplateConfig(
        name="generate_product",
        description="Create realistic retail product entry",
        template=template,
        input_variables=[
            {"name": "industry",    "description": "Product theme", "is_required": True},
            {"name": "product_id",  "description": "UUID",          "is_required": True},
            {"name": "created_at",  "description": "ISO timestamp", "is_required": True},
        ],
        execution_settings={
            "azure_open_ai": {"max_tokens": max_tokens, "temperature": 0.7, "top_p": 0.95}
        },
    )
    
    # 2. Register with the kernel
    kernel_func = kernel.add_function(
        name="generate_product",
        plugin_name="retail_product",
        function_name="generate_product",
        prompt_template_config=prompt_cfg,
    )

    # 3. Helper to invoke the function synchronously
    async def _async_runner(**kwargs):
        result = await kernel.invoke(kernel_func, **kwargs)
        return str(result)

    return lambda **kwargs: asyncio.run(_async_runner(**kwargs))

# -------------------------------------------------------------------------
# Prompt templates
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

PROMPT_TEMPLATE = _build_prompt(args.format)
prompt = _create_prompt_function(kernel, PROMPT_TEMPLATE)

# -------------------------------------------------------------------------
# Logging
# -------------------------------------------------------------------------
import colorama, yaml
colorama.init(autoreset=True)
logging.basicConfig(level=os.getenv("LOG_LEVEL","INFO"), format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

# -------------------------------------------------------------------------
# Random helpers
# -------------------------------------------------------------------------
CURRENCIES: Final[list[str]] = ["USD","EUR","GBP","AUD","CAD"]
def _random_price() -> float: return round(random.uniform(5.0, 500.0), 2)
def _random_stock() -> int:   return random.randint(0, 500)
def _random_rating() -> float: return round(random.uniform(1.0, 5.0),1)

# -------------------------------------------------------------------------
# Generation loop
# -------------------------------------------------------------------------
def generate_products(count:int, out_dir:Path, industry:str):
    for _ in range(count):
        product_id  = str(uuid.uuid4())
        created_at  = _dt.datetime.now(_dt.timezone.utc).isoformat()
        output      = prompt(industry=industry, product_id=product_id, created_at=created_at).strip()

        ext = {"yaml":"yaml","json":"json","text":"txt"}[args.format]
        file_path = out_dir / f"{product_id}.{ext}"
        with file_path.open("w",encoding="utf-8") as fp:
            if args.format == "yaml":
                data = yaml.safe_load(output)
                # enrich with random price/stock if not present
                data.setdefault("price", _random_price())
                data.setdefault("currency", random.choice(CURRENCIES))
                data.setdefault("stock_quantity", _random_stock())
                data.setdefault("rating", _random_rating())
                yaml.safe_dump(data, fp, sort_keys=False)
            elif args.format == "json":
                data = json.loads(output)
                data.setdefault("price", _random_price())
                data.setdefault("currency", random.choice(CURRENCIES))
                data.setdefault("stock_quantity", _random_stock())
                data.setdefault("rating", _random_rating())
                json.dump(data, fp, indent=2)
            else:
                fp.write(output + "\n")
        log.info("%s✔ Generated %s%s", Fore.GREEN, file_path, Style.RESET_ALL)

# -------------------------------------------------------------------------
if __name__ == "__main__":
    generate_products(args.count, args.output, args.industry)
