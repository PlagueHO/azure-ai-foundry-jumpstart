"""
Generate technical support cases in YAML format with Azure OpenAI via Semantic Kernel.

Example usage:

python generate_tech_support.py -d "ScanlonSoft Retail Solution. A SaaS platform running in Azure that provide point of sale retail software to small business. React frontend, with APIs hosted in Azure App Service on the backend and an Azure SQL Database." -n 50 -o ./sample-data/tech-support/

Prerequisites
-------------
1. pip install -r requirements.txt
2. Create a `.env` file in this folder (or export env vars) containing:
   AZURE_OPENAI_ENDPOINT="https://<your-endpoint>.openai.azure.com/"
   AZURE_OPENAI_DEPLOYMENT="<deployment-name>"
   AZURE_OPENAI_API_KEY="<api-key>" # Omit if using DefaultAzureCredential()
"""

from __future__ import annotations
import argparse
import datetime as _dt
import os
from pathlib import Path
# asyncio is handled by SyntheticDataGenerator's sync wrapper
import random  # random value generation
# logging is handled by SyntheticDataGenerator
from typing import Final, Tuple
import json
import uuid

import yaml
# dotenv, semantic_kernel, AzureChatCompletion, PromptTemplateConfig, KernelFunction are handled by SyntheticDataGenerator
from colorama import Fore, Style # Keep for coloring output messages

from synthetic_data_generator import SyntheticDataGenerator # Import the new helper class

# -------------------------------------------------------------------------
# Security – Handled by SyntheticDataGenerator
# -------------------------------------------------------------------------
# load_dotenv() and AZURE_OPENAI_... variables are removed as SyntheticDataGenerator handles them.

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

# -------------------------------------------------------------------------
# SyntheticDataGenerator setup
# -------------------------------------------------------------------------
# _create_kernel(), kernel, _create_prompt_function() are removed.
# Logging setup is also removed as SyntheticDataGenerator handles it.
generator = SyntheticDataGenerator()
logger = generator.logger # Use the logger from the generator instance


# -------------------------------------------------------------------------
# Prompt templates per format (Remains script-specific)
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

SYSTEM_PROMPT_TEMPLATE = _build_prompt(args.format)
prompt_function = generator.create_prompt_function(
    template=SYSTEM_PROMPT_TEMPLATE,
    function_name="generate_support_case",
    plugin_name="tech_support",
    prompt_description="Create realistic tech-support cases",
    input_variables=[
        { "name": "system_description", "description": "Target system description",  "is_required": True },
        { "name": "status",             "description": "Case status",                "is_required": True },
        { "name": "severity",           "description": "Case severity",              "is_required": True },
        { "name": "priority",           "description": "Case priority",              "is_required": True },
        { "name": "case_id",            "description": "Pre-generated UUID",         "is_required": True },
        { "name": "created_at",         "description": "Pre-generated ISO-timestamp","is_required": True },
    ],
    max_tokens=1000
)

# -------------------------------------------------------------------------
# Logging (Handled by SyntheticDataGenerator, colorama import kept for messages)
# -------------------------------------------------------------------------
# import colorama and colorama.init() are removed as SyntheticDataGenerator handles colorama init.
# logging.basicConfig and logger = logging.getLogger(__name__) are removed.

# -------------------------------------------------------------------------
# Random attribute helpers (Remains script-specific)
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
# Generation loop wrapped in a function for testability (Remains script-specific)
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
            logger.debug(f"Attempt {attempt}/3 for case {idx}/{count}")
            output: str = prompt_function( # Use the function from the generator
                system_description=system_description,
                status=status_choice,
                severity=severity_choice,
                priority=priority_choice,
                case_id=case_id,
                created_at=created_at,
            )

            # ---------- deserialize when needed ----------
            case_data: dict | None = None
            try:
                if args.format == "yaml":
                    case_data = yaml.safe_load(output)
                elif args.format == "json":
                    case_data = json.loads(output)
                else:  # text – no structured validation
                    pass # output is already the text content

                if args.format != "text":
                    if not isinstance(case_data, dict):
                        raise ValueError(f"Output is not a dictionary. Got: {type(case_data)}")
                    if not required.issubset(case_data.keys()):
                        missing = required - set(case_data.keys())
                        raise ValueError(f"Missing fields: {', '.join(missing)}")
                break  # success
            except Exception as ex:
                logger.error(f"Raw output on error:\n---\n{output}\n---")
                if attempt < 3:
                    logger.warning(f"Attempt {attempt}/3 failed for case {idx} – retrying: {ex}")
                else:
                    logger.error(f"All 3 attempts failed for case {idx}. Error: {ex}")
                    # Decide if you want to raise, or skip this item
                    # For now, let's log and skip to the next item if all attempts fail
                    # raise # Or re-raise the last exception
                    continue # Skip to next case

        if args.format != "text" and case_data is None and attempt == 3: # If all attempts failed
            logger.error(f"Skipping case {idx} due to persistent errors.")
            continue


        generated_at = _dt.datetime.now(_dt.timezone.utc).isoformat()
        
        ext = {"yaml": "yaml", "json": "json", "text": "txt"}[args.format]
        out_file = out_dir / f"{case_id}.{ext}"
        with out_file.open("w", encoding="utf-8") as fp:
            if args.format == "yaml":
                if case_data: yaml.safe_dump({**case_data, "generated_at": generated_at}, fp, sort_keys=False)
            elif args.format == "json":
                if case_data: json.dump({**case_data, "generated_at": generated_at}, fp, indent=2)
            else:  # text
                fp.write(f"{output.strip()}\nGenerated At: {generated_at}\n")

        logger.info("%s✔ Generated %s%s", Fore.GREEN, out_file, Style.RESET_ALL)


# -------------------------------------------------------------------------
# Entry point
# -------------------------------------------------------------------------
if __name__ == "__main__":
    logger.info(f"Starting generation of {args.count} tech support case(s)...")
    generate_cases(args.count, args.output, args.system_description)
    logger.info("Generation complete.")
