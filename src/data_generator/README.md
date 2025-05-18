# Synthetic Data Generator (Package-level Guide)

This package provides the **engine, interfaces and scenario plug-ins** used by
the Azure AI Foundry Jumpstart Solution Accelerator to create realistic yet
*entirely fictional* datasets with Azure OpenAI + Semantic Kernel.

## 1. Quick Start (One-liner)

```bash
python -m data_generator --scenario tech-support --count 10 --out-dir ./data
```

The command above:

1. Loads environment variables / `.env` for Azure OpenAI connectivity.  
2. Instantiates the requested `DataGeneratorTool` (`tech-support`).  
3. Generates `10` records in parallel and writes them to `./data`  
   (`0001.json`, `0002.json`, …).

---

## 2. Prerequisites

- Python ≥ 3.10
- An Azure OpenAI resource (endpoint + deployment)  
- Either an API key **or** Managed Identity permission

```dotenv
# .env (example)
AZURE_OPENAI_ENDPOINT   = "https://<your>.openai.azure.com"
AZURE_OPENAI_DEPLOYMENT = "gpt-4-1"
# Optional; omit to use Managed Identity
# AZURE_OPENAI_API_KEY  = "<key>"
```

Install dependencies from the repo root:

```bash
pip install -e ".[dev]"
```

---

## 3. Global CLI Flags

| Flag                         | Required | Description                                               | Default  |
|------------------------------|----------|-----------------------------------------------------------|----------|
| `--scenario`                 | Y        | Which tool to run (`tech-support`, `retail-product`, ...) |          |
| `--count`                    |          | Number of records to create                               | `1`      |
| `--out-dir`                  |          | Output folder (auto-created)                              | `./data` |
| `--output-format`            |          | `json`, `yaml`, `text`                                    | `json`   |
| `--azure-openai-endpoint`    |          | Override env var                                          |          |
| `--azure-openai-deployment`  |          | Override env var                                          |          |
| `--azure-openai-api-key`     |          | Bypass Managed Identity                                   |          |

---

## 4. Tool Reference

### 4.1 Tech-Support (`tech-support`)

Produces synthetic help-desk cases.

| Flag                         | Required | Description                        | Default  |
|------------------------------|----------|------------------------------------|----------|
| `-d`, `--system-description` | Y        | Short blurb of the affected system |          |

Example:

```bash
python -m data_generator \
  --scenario tech-support \
  --count 50 \
  --system-description "ContosoShop – React SPA + Azure SQL back-end" \
  --output-format yaml \
  --out-dir ./sample-data/tech-support
```

### 4.2 Retail-Product (`retail-product`)

Creates e-commerce catalogue entries.

| Flag               | Required | Description                                  | Default   |
|--------------------|----------|----------------------------------------------|-----------|
| `-i`, `--industry` | N        | Industry / theme (electronics, fashion, ...) | `general` |

Example:

```bash
python -m data_generator \
  --scenario retail-product \
  --count 100 \
  --industry electronics \
  --output-format json \
  --out-dir ./sample-data/retail-products
```

### 4.3 Healthcare-Record (`healthcare-record`)

Generate anonymized healthcare documents.

| Flag               | Required | Description                                                      | Default            |
|--------------------|----------|------------------------------------------------------------------|--------------------|
| `--document-type`  | N        | Type of medical document (e.g. Clinic Note, Discharge Summary)   | `Clinic Note`      |
| `--specialty`      | N        | Medical specialty (e.g. Cardiology, Oncology)                    | `General Medicine` |

Example:

```bash
python -m data_generator \
  --scenario healthcare-record \
  --count 10 \
  --document-type "Discharge Summary" \
  --specialty Cardiology \
  --output-format yaml \
  --out-dir ./sample-data/healthcare-records
```

### 4.4 Financial-Transaction (`financial-transaction`)

Generate synthetic bank-account statements with ≥50 transactions.

| Flag                  | Required | Description                                        | Default    |
|-----------------------|----------|----------------------------------------------------|------------|
| `-a, --account-type`  | N        | Account kind (checking, savings, credit)           | `checking` |
| `--transactions-max`  | N        | Max transactions per statement                     | `50`       |
| `--fraud-percent`     | N        | % chance to include a subtle fraudulent transaction| `0`        |

Example:

```bash
python -m data_generator \
  --scenario financial-transaction \
  --count 20 \
  --account-type savings \
  --transactions-max 100 \
  --fraud-percent 5 \
  --output-format yaml \
  --out-dir ./data/financial
```

---

## 5.  Extending with New Scenarios

1. Add `<new>.py` under `src/data_generator/tools/`.
2. Subclass `DataGeneratorTool`, set unique `name` + `toolName`.
3. Implement `build_prompt`, `cli_arguments`, `validate_args`, etc.
4. No core changes required – the registry auto-discovers the new tool.

For full architectural details refer to
[`docs/DESIGN.md`](../docs/DESIGN.md).
