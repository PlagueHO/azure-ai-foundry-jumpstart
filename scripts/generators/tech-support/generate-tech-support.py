"""
Generate technical support cases in YAML format with Azure OpenAI via Semantic Kernel.

Example usage:

python scripts/generators/tech-support/generate-tech-support.py -d "ScanlonSoft Retail Solution. A SaaS platform running in Azure that provide point of sale retail software to small business. React frontend, with APIs hosted in Azure App Service on the backend and an Azure SQL Database." -n 50 -o ./sample-data/tech-support/

Prerequisites
-------------
1. pip install semantic-kernel python-dotenv pyyaml
2. Create a `.env` file in this folder (or export env vars) containing:
   AZURE_OPENAI_ENDPOINT="https://<your-endpoint>.openai.azure.com/"
   AZURE_OPENAI_DEPLOYMENT="<deployment-name>"
   AZURE_OPENAI_API_KEY="<api-key>"
"""

from __future__ import annotations
import argparse
import datetime as _dt
import os
from pathlib import Path
import asyncio  # <-- new
import random  # random value generation
import logging
from typing import Final, Tuple

import yaml
from dotenv import load_dotenv
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.prompt_template import PromptTemplateConfig
from semantic_kernel.functions.kernel_function import KernelFunction
from colorama import Fore, Style

# -------------------------------------------------------------------------
# Security – never print secrets
# -------------------------------------------------------------------------
load_dotenv()  # Loads .env if present
# Load user-specific overrides (not committed to the repo)
load_dotenv(".env", override=True)

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")

if not all([AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_API_KEY]):
    raise EnvironmentError(
        "Azure OpenAI environment variables are not fully configured."
    )

# -------------------------------------------------------------------------
# CLI arguments
# -------------------------------------------------------------------------
parser = argparse.ArgumentParser(
    description="Generate technical support case sample data using Azure OpenAI."
)
parser.add_argument(
    "-d",
    "--system-description",
    required=True,
    help="Short description of the system for which cases are generated.",
)
parser.add_argument(
    "-n",
    "--count",
    type=int,
    default=1,
    help="Number of cases to generate.",
)
parser.add_argument(
    "-o",
    "--output",
    type=Path,
    default=Path.cwd() / "output",
    help="Folder where YAML files will be written (defaults to ./output).",
)
args = parser.parse_args()

args.output.mkdir(parents=True, exist_ok=True)

def _create_kernel() -> sk.Kernel:
    """
    Build a Semantic Kernel instance.
    """
    kernel = sk.Kernel()
    service = AzureChatCompletion(
        deployment_name=AZURE_OPENAI_DEPLOYMENT,
        endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        service_id="azure_open_ai",
    )

    kernel.add_service(service)

    return kernel


# -------------------------------------------------------------------------
# Semantic Kernel setup (Operational Excellence, Reliability)
# -------------------------------------------------------------------------
kernel = _create_kernel()


# -------------------------------------------------------------------------
# Prompt helpers – follows SK sample 03-prompt-function-inline
# -------------------------------------------------------------------------
def _create_prompt_function(kernel: sk.Kernel, template: str, *, max_tokens: int = 800):
    """
    Build an inline prompt-function.
    Returns a sync wrapper that can be called like a normal function.
    """

    # 1. Prompt-template configuration
    prompt_cfg = PromptTemplateConfig(
        name="generate_support_case",
        description="Create realistic tech-support cases in YAML",
        template=template,
        # Single required input variable
        input_variables=[
            { "name": "system_description", "description": "Target system description", "is_required": True },
            { "name": "status",              "description": "Case status",                "is_required": True },
            { "name": "severity",            "description": "Case severity",              "is_required": True },
            { "name": "priority",            "description": "Case priority",              "is_required": True },
        ],
        execution_settings={
            "azure_open_ai": {
                "max_tokens": max_tokens,
                "temperature": 0.7,
                "top_p": 0.95,
            }
        },
    )

    # 2. Register with the kernel
    kernel_func = kernel.add_function(
        name="generate_support_case",
        plugin_name="tech_support",
        function_name="generate_support_case",
        prompt_template_config=prompt_cfg,
    )

    # 3. Helper to invoke the function synchronously
    async def _async_runner(**kwargs):
        result = await kernel.invoke(kernel_func, **kwargs)
        return str(result)

    return lambda **kwargs: asyncio.run(_async_runner(**kwargs))


# -------------------------------------------------------------------------
# Prompt template
# -------------------------------------------------------------------------
SYSTEM_PROMPT = """
You are a helpful support agent generating realistic technical support cases.
The status of this case is :{{$status}}
The severity of this case is :{{$severity}}
The priority of this case is :{{$priority}}
Output MUST be valid YAML. Do not wrap in markdown.

Create a support case for the following system:
- {{$system_description}}

Each YAML file must contain:
id: UUID v4
created_at: ISO 8601 timestamp
system_description: echo back the description
issue_summary: single sentence summary
severity: one of [critical, high, medium, low]
priority: P1..P4
status: one of [open, investigating, resolved, closed]
customer_name: realistic name
contact_email: realistic but fake email
conversation_history:
  - role: customer|agent
    message: text
    timestamp: ISO 8601
resolved_at: ISO 8601 timestamp (optional, only if status is closed)
resolution: text (optional, only if status is resolved or closed)
area: one of [frontend, backend, database, network, other] (optional, only if status is resolved or closed)
is_bug: true|false (optional, only if status is resolved or closed)
root_cause: text (optional, only if status is resolved or closed)

The conversation_history should contain at least 3 but no more than 10 messages, alternating between customer and agent.

Return ONLY the YAML. DO NOT INCLUDE ANY OTHER TEXT. DO NOT INCLUDE ```yaml OR ANY OTHER MARKUP.
"""

prompt = _create_prompt_function(kernel, SYSTEM_PROMPT, max_tokens=1000)

# -------------------------------------------------------------------------
# Logging (replace noisy prints) – adjustable via LOG_LEVEL env-var
# -------------------------------------------------------------------------
import colorama
colorama.init(autoreset=True)
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------------
# Random attribute helpers
# -------------------------------------------------------------------------
STATUS_OPTIONS:   Final[list[str]] = ["open", "investigating", "resolved", "closed"]
SEVERITY_OPTIONS: Final[list[str]] = ["critical", "high", "medium", "low"]
PRIORITY_OPTIONS: Final[list[str]] = ["P1", "P2", "P3", "P4"]


def _random_attributes() -> Tuple[str, str, str]:
    """Return a random (status, severity, priority) tuple."""
    return (
        random.choice(STATUS_OPTIONS),
        random.choice(SEVERITY_OPTIONS),
        random.choice(PRIORITY_OPTIONS),
    )


# -------------------------------------------------------------------------
# Generation loop wrapped in a function for testability
# -------------------------------------------------------------------------
def generate_cases(count: int, out_dir: Path, system_description: str) -> None:
    required = {
        "id", "created_at", "system_description", "issue_summary",
        "severity", "priority", "status", "customer_name",
        "contact_email", "conversation_history",
    }

    for idx in range(1, count + 1):
        status_choice, severity_choice, priority_choice = _random_attributes()

        for attempt in range(1, 4):  # up to 3 retries
            yaml_raw: str = prompt(
                system_description=system_description,
                status=status_choice,
                severity=severity_choice,
                priority=priority_choice,
            )
            try:
                case_data = yaml.safe_load(yaml_raw)

                if not required.issubset(case_data):
                    missing = required - set(case_data)
                    raise ValueError(f"missing fields: {', '.join(missing)}")

                break  # success
            except Exception as ex:
                if attempt < 3:
                    logger.warning(f"Attempt {attempt}/3 failed – retrying: {ex}")
                else:
                    raise

        case_data["generated_at"] = _dt.datetime.now(_dt.timezone.utc).isoformat()

        out_file = out_dir / f"support_case_{idx}.yaml"
        with out_file.open("w", encoding="utf-8") as fp:
            yaml.safe_dump(case_data, fp, sort_keys=False)

        logger.info("%s✔ Generated %s%s", Fore.GREEN, out_file, Style.RESET_ALL)


# -------------------------------------------------------------------------
# Entry point
# -------------------------------------------------------------------------
if __name__ == "__main__":
    generate_cases(args.count, args.output, args.system_description)
