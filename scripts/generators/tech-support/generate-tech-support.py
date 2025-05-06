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
import json
import uuid

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
parser.add_argument(
    "-f",
    "--format",
    choices=["yaml", "json", "text"],
    default="yaml",
    help="Output file format (yaml|json|text). Defaults to yaml.",
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
            { "name": "system_description", "description": "Target system description",  "is_required": True },
            { "name": "status",             "description": "Case status",                "is_required": True },
            { "name": "severity",           "description": "Case severity",              "is_required": True },
            { "name": "priority",           "description": "Case priority",              "is_required": True },
            { "name": "case_id",            "description": "Pre-generated UUID",         "is_required": True },
            { "name": "created_at",         "description": "Pre-generated ISO-timestamp","is_required": True },
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
# Prompt templates per format
# -------------------------------------------------------------------------
def _build_prompt(output_format: str) -> str:
    base = """
You are a helpful support agent generating realistic technical support cases.
The status of this case is :{{$status}}
The severity of this case is :{{$severity}}
The priority of this case is :{{$priority}}
"""
    if output_format == "yaml":
        return base + """
Output MUST be valid YAML. Do not wrap in markdown.

Create a support case for the following system:
- {{$system_description}}

case_id: {{$case_id}}
created_at: {{$created_at}}
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
resolved_at: ISO 8601 timestamp (optional, only if status is closed, must be after created_at)
resolution: text (optional, only if status is resolved or closed)
area: one of [frontend, backend, database, network, other] (optional, only if status is resolved or closed)
is_bug: true|false (optional, only if status is resolved or closed)
root_cause: text (optional, only if status is resolved or closed)

The conversation_history should contain at least 3 but no more than 10 messages, alternating between customer and agent.

Return ONLY the YAML. DO NOT INCLUDE ANY OTHER TEXT. DO NOT INCLUDE ```yaml OR ANY OTHER MARKUP.
"""
    if output_format == "json":
        return base + """
Output MUST be valid JSON. Do not wrap in markdown.

{
  "case_id": "{{$case_id}}",
  "created_at": "{{$created_at}}",
  "system_description": "{{$system_description}}",
  "issue_summary": "single sentence summary",
  "severity": "one of [critical, high, medium, low]",
  "priority": "P1..P4",
  "status": "one of [open, investigating, resolved, closed]",
  "customer_name": "realistic name",
  "contact_email": "realistic but fake email",
  "conversation_history": [
    {
      "role": "customer|agent",
      "message": "text",
      "timestamp": "ISO 8601"
    }
  ],
  "resolved_at": "ISO 8601 timestamp (optional, only if status is closed, must be after created_at))",
  "resolution": "text (optional, only if status is resolved or closed)",
  "area": "one of [frontend, backend, database, network, other] (optional, only if status is resolved or closed)",
  "is_bug": "true|false (optional, only if status is resolved or closed)",
  "root_cause": "text (optional, only if status is resolved or closed)"
}

The conversation_history should contain at least 3 but no more than 10 messages, alternating between customer and agent.

Return ONLY the JSON. DO NOT INCLUDE ANY OTHER TEXT. DO NOT INCLUDE ```json OR ANY OTHER MARKUP.
"""
    # TEXT (free-form)
    return base + """
Case ID: {{$case_id}}
Created At: {{$created_at}}
System Description: {{$system_description}}
Issue Summary: single sentence summary
Severity: {{$severity}}
Priority: {{$priority}}
Status: {{$status}}
Customer Name: realistic name
Contact Email: realistic but fake email
Conversation History:
  - (ISO 8601) [customer] message text
  - (ISO 8601) [agent]    message text
  - repeat 3-10 lines alternating roles
Resolved At: ISO 8601 (omit if not resolved/closed, must be after created_at))
Resolution: text (omit if not resolved/closed)
Area: frontend|backend|database|network|other (omit if not resolved/closed)
Is Bug: true|false (omit if not resolved/closed)
Root Cause: text (omit if not resolved/closed)
"""

SYSTEM_PROMPT = _build_prompt(args.format)
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
        "case_id", "created_at", "system_description", "issue_summary",
        "severity", "priority", "status", "customer_name",
        "contact_email", "conversation_history",
    }
    for idx in range(1, count + 1):
        status_choice, severity_choice, priority_choice = _random_attributes()
        case_id: str = str(uuid.uuid4())
        created_at: str = _dt.datetime.now(_dt.timezone.utc).isoformat()

        for attempt in range(1, 4):
            # ---------- invoke LLM ----------
            output: str = prompt(
                system_description=system_description,
                status=status_choice,
                severity=severity_choice,
                priority=priority_choice,
                case_id=case_id,
                created_at=created_at,
            )

            # ---------- deserialize when needed ----------
            if args.format == "yaml":
                case_data = yaml.safe_load(output)
            elif args.format == "json":
                case_data = json.loads(output)
            else:  # text – no structured validation
                case_data = None

            try:
                if args.format != "text":
                    if not required.issubset(case_data):
                        missing = required - set(case_data)
                        raise ValueError(f"missing fields: {', '.join(missing)}")
                break  # success
            except Exception as ex:
                if attempt < 3:
                    logger.warning(f"Attempt {attempt}/3 failed – retrying: {ex}")
                else:
                    raise

        generated_at = _dt.datetime.now(_dt.timezone.utc).isoformat()
        if case_data is not None:
            case_data["generated_at"] = generated_at

        ext = {"yaml": "yaml", "json": "json", "text": "txt"}[args.format]
        out_file = out_dir / f"{case_id}.{ext}"
        with out_file.open("w", encoding="utf-8") as fp:
            if args.format == "yaml":
                yaml.safe_dump(case_data, fp, sort_keys=False)
            elif args.format == "json":
                json.dump(case_data, fp, indent=2)
            else:  # text
                fp.write(f"{output.strip()}\nGenerated At: {generated_at}\n")

        logger.info("%s✔ Generated %s%s", Fore.GREEN, out_file, Style.RESET_ALL)


# -------------------------------------------------------------------------
# Entry point
# -------------------------------------------------------------------------
if __name__ == "__main__":
    generate_cases(args.count, args.output, args.system_description)
