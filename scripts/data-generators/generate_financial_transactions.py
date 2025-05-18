"""
Generate synthetic bank-account statements with ≥50 transactions each, using Azure
OpenAI via Semantic Kernel.

Example:
python generate_financial_transactions.py -n 20 -a checking -f json -o ./sample-data/financial-transactions/

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
import uuid
import datetime as _dt
import random
import json
from pathlib import Path
from typing import Final

import yaml
from colorama import Fore, Style
from synthetic_data_generator import SyntheticDataGenerator

# ---------- CLI ----------
parser = argparse.ArgumentParser(
    description="Generate synthetic bank statements with realistic transactions."
)
parser.add_argument("-a", "--account-type", default="checking",
                    help="Account type (e.g., checking, savings, credit).")
parser.add_argument("-n", "--count", type=int, default=1,
                    help="Number of statements to generate.")
parser.add_argument("-o", "--output", type=Path,
                    default=Path.cwd() / "output_financial", # Consistent with healthcare
                    help="Output folder.")
parser.add_argument("-f", "--format", choices=["yaml", "json", "text"],
                    default="yaml", help="Output format.")
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)

# ---------- Common helper ----------
generator = SyntheticDataGenerator() # Renamed for consistency
logger = generator.logger # Renamed for consistency

# ---------- Prompt ----------
def _build_prompt(output_format: str) -> str: # Renamed arg for consistency
    base = """
You are a banking data specialist creating realistic but entirely fictional
ACCOUNT STATEMENTS for demonstrations such as fraud-detection analytics.
Never reveal any real PII. Use plausible but fake names & IDs.

Account Type: {{$account_type}}
Account ID:   {{$account_id}}
Statement ID: {{$statement_id}}
Period:       {{$start_date}} - {{$end_date}}

Generate AT LEAST 50 transactions within the period. Distribute dates,
amounts and balances realistically. Use ISO-8601 dates and two-decimal
currency amounts (USD). Opening balance + sum(transactions) →
closing balance (allow for rounding cents).
"""
    if output_format == "yaml":
        return base + """
Return valid YAML ONLY (no fences).

statement_id: {{$statement_id}}
account_id: {{$account_id}}
account_type: {{$account_type}}
start_date: {{$start_date}}   # ISO 8601
end_date: {{$end_date}}       # ISO 8601
opening_balance: 1234.56
closing_balance: 2345.67
currency: USD
transactions:
  - tx_id: uuid
    date: ISO 8601
    description: text
    amount: 12.34               # negative = debit, positive = credit
    balance_after: 1246.90      # running ledger balance
    category: groceries|salary|transfer|utilities|other
"""
    if output_format == "json":
        return base + """
{
  "statement_id":"{{$statement_id}}",
  "account_id":"{{$account_id}}",
  "account_type":"{{$account_type}}",
  "start_date":"{{$start_date}}",
  "end_date":"{{$end_date}}",
  "opening_balance":1234.56,
  "closing_balance":2345.67,
  "currency":"USD",
  "transactions":[
    {
      "tx_id":"uuid",
      "date":"ISO 8601",
      "description":"text",
      "amount":-25.30,
      "balance_after":1209.26,
      "category":"groceries"
    }
  ]
}
Return JSON ONLY (no markdown fences).
"""
    # TEXT
    return base + """
Statement ID: {{$statement_id}}
Account ID: {{$account_id}} ({{$account_type}})
Period: {{$start_date}} – {{$end_date}}
Opening Balance: 1234.56 USD
Closing Balance: 2345.67 USD

Transactions:
date | description | amount | balance_after | category
----------------------------------------------------------------
2024-01-02 | Grocery Store | -45.67 | 1188.89 | groceries
... ≥50 rows ...
"""

PROMPT_TEMPLATE_STRING = _build_prompt(args.format) # Renamed PROMPT to PROMPT_TEMPLATE_STRING
prompt_function = generator.create_prompt_function( # Renamed prompt_fn to prompt_function
    template=PROMPT_TEMPLATE_STRING,
    function_name="generate_statement",
    plugin_name="financial_tx",
    prompt_description="Create synthetic bank statements (≥50 transactions).",
    input_variables=[
        {"name":"account_type","description":"Type of account","is_required":True},
        {"name":"account_id","description":"Random account number","is_required":True},
        {"name":"statement_id","description":"UUID of statement","is_required":True},
        {"name":"start_date","description":"Period start","is_required":True},
        {"name":"end_date","description":"Period end","is_required":True},
    ],
    max_tokens=2000, # Adjusted max_tokens
    temperature=0.55
)

# ---------- Generation ----------
required_fields_yaml_json: Final = { # Renamed REQ_FIELDS for consistency
    "statement_id","account_id","account_type",
    "start_date","end_date","opening_balance",
    "closing_balance","currency","transactions"
}

def _period_dates(months_back:int=1):
    today=_dt.date.today()
    first=(today.replace(day=1)-_dt.timedelta(days=1)).replace(day=1)
    last=(first.replace(day=28)+_dt.timedelta(days=4)).replace(day=1)-_dt.timedelta(days=1)
    return first.isoformat(), last.isoformat()

def generate_statements(count:int, out_dir:Path, acct_type:str, output_format:str) -> None: # Renamed and updated signature
    for idx in range(1, count+1):
        start_date,end_date=_period_dates()
        statement_id=str(uuid.uuid4())
        account_id=str(random.randint(1000000000,9999999999)) # Fictional account ID

        output_content: str = "" # Renamed for consistency
        statement_data: dict | None = None # Renamed for consistency

        for attempt in range(1,4):
            logger.debug(f"Attempt {attempt}/3 for statement {idx}/{count}")
            output_content=prompt_function( # Use renamed variable
                account_type=acct_type,
                account_id=account_id,
                statement_id=statement_id,
                start_date=start_date,
                end_date=end_date
            ).strip()

            if not output_content:
                logger.warning(f"LLM returned empty content on attempt {attempt} for statement {idx}.")
                if attempt == 3:
                    logger.error(f"Skipping statement {idx} after 3 attempts due to empty content.")
                continue # Try again or fail

            try:
                if output_format=="yaml":
                    statement_data=yaml.safe_load(output_content)
                elif output_format=="json":
                    # Handle potential markdown fences
                    if output_content.startswith("```json"):
                        output_content = output_content.removeprefix("```json").removesuffix("```").strip()
                    elif output_content.startswith("```"):
                         output_content = output_content.removeprefix("```").removesuffix("```").strip()
                    statement_data=json.loads(output_content)
                else: # text format
                    break # No further validation for text

                if not isinstance(statement_data, dict):
                    raise ValueError(f"Output is not a dictionary. Got: {type(statement_data)}")
                if not required_fields_yaml_json.issubset(statement_data.keys()):
                    missing = required_fields_yaml_json - set(statement_data.keys())
                    raise ValueError(f"Missing required fields: {', '.join(missing)}")
                if len(statement_data.get("transactions",[]))<50: # Check for minimum transactions
                    raise ValueError(f"Fewer than 50 transactions returned. Got: {len(statement_data.get('transactions',[]))}")
                break # Success
            except Exception as e:
                logger.error(f"Raw output on error (attempt {attempt}):\n---\n{output_content}\n---")
                if attempt==3:
                    logger.error(f"Skipping statement {idx} due to repeated errors: {e}")
                    output_content="" # Ensure output_content is empty if all attempts failed
                    statement_data=None
                else:
                    logger.warning(f"Retry ({attempt}/3) for statement {idx}: {e}")

        if not output_content and output_format != "text":
            logger.error(f"Skipping statement {idx} (Account Type: {acct_type}) due to persistent errors.")
            continue
        if not output_content and output_format == "text":
            logger.error(f"Skipping statement {idx} (Account Type: {acct_type}) as no text content was generated.")
            continue


        generated_at_ts=_dt.datetime.now(_dt.timezone.utc).isoformat()
        ext={"yaml":"yaml","json":"json","text":"txt"}[output_format]
        
        # Sanitize account type for filename (though less critical for predefined types)
        safe_acct_type = "".join(c if c.isalnum() else "_" for c in acct_type)
        file_path=out_dir/f"statement_{safe_acct_type}_{statement_id}.{ext}" # Consistent filename pattern

        with file_path.open("w",encoding="utf-8") as fp:
            if output_format=="yaml":
                if statement_data: # Check if data exists
                    statement_data["generation_metadata"]={"generated_at_script":generated_at_ts, "script_version": "1.0"}
                    yaml.safe_dump(statement_data,fp,sort_keys=False, allow_unicode=True)
            elif output_format=="json":
                if statement_data: # Check if data exists
                    statement_data["generation_metadata"]={"generated_at_script":generated_at_ts, "script_version": "1.0"}
                    json.dump(statement_data,fp,indent=2, ensure_ascii=False)
            else: # text
                fp.write(f"{output_content}\n\n---Generation Metadata---\nGenerated At (Script): {generated_at_ts}\nScript Version: 1.0\n")

        logger.info("%s✔ Generated %s%s (Account Type: %s)",Fore.GREEN,file_path,Style.RESET_ALL, acct_type)

if __name__=="__main__":
    logger.info(
        f"Starting generation of {args.count} financial statement(s) "
        f"(Account Type: {args.account_type}, Format: {args.format})..."
    )
    generate_statements(args.count,args.output,args.account_type, args.format) # Updated call
    logger.info("Generation complete.")
