# Synthetic Data Generators

This folder contains self-contained scripts that create **fictional** data sets with help from Azure OpenAI via the [Microsoft Semantic Kernel](https://aka.ms/semantic-kernel).  
Every script relies on the reusable helper `synthetic_data_generator.py` to remove boiler-plate and enforce consistent security / logging standards.

---

## 1. Common Helper – `synthetic_data_generator.py`

| Responsibility | Details |
| -------------- | ------- |
| Environment loading | Merges a root `.env` plus an optional script-local override to obtain:<br/>`AZURE_OPENAI_ENDPOINT` • `AZURE_OPENAI_DEPLOYMENT` • `AZURE_OPENAI_API_KEY` (optional – falls back to `DefaultAzureCredential`). |
| Kernel wiring | Registers an `AzureChatCompletion` service and exposes `create_prompt_function(…)` that returns a **synchronous** wrapper around a Semantic Kernel function. |
| Logging | Colourised console output with the level controlled by `LOG_LEVEL` (`INFO` default). |
| Security | Uses API key *or* Managed Identity (no secrets hard-coded in source). |

Minimal `.env` example:

```env
AZURE_OPENAI_ENDPOINT="https://<your-endpoint>.openai.azure.com/"
AZURE_OPENAI_DEPLOYMENT="gpt-4o"
# AZURE_OPENAI_API_KEY="<api-key>"  # Only use when using Entra ID identity
LOG_LEVEL="INFO"
```

Install runtime dependencies once:

```bash
pip install -r requirements.txt
```

---

## 2. Generator Scripts

### 2.1  `generate_tech_support.py`

Creates realistic technical-support cases (YAML / JSON / text).

| Flag | Required | Description | Default |
| ---- | -------- | ----------- | ------- |
| `-d, --system-description` | ✅ | Short description of the system under support | — |
| `-n, --count`              | ❌ | How many cases to create | `1` |
| `-o, --output`             | ❌ | Output folder | `./output` |
| `-f, --format`             | ❌ | `yaml` \| `json` \| `text` | `yaml` |

Example:

```bash
python generate_tech_support.py \
  -d "ScanlonSoft Retail Solution – React SPA + Azure SQL backend" \
  -n 50 -o ./sample/tech-support -f yaml
```

---

### 2.2  `generate_healthcare_records.py`

Produces anonymised medical documents in several formats.

| Flag | Required | Description | Default |
| ---- | -------- | ----------- | ------- |
| `-n, --count`          | ❌ | Number of records | `1` |
| `-o, --output`         | ❌ | Output folder | `./output_healthcare` |
| `-f, --format`         | ❌ | `yaml` \| `json` \| `text` | `yaml` |
| `--document-type`      | ❌ | e.g. *Clinic Note*, *Discharge Summary* | `Clinic Note` |
| `--specialty`          | ❌ | Medical specialty | `General Medicine` |

Example:

```bash
python generate_healthcare_records.py \
  -n 10 --format json \
  --document-type "Discharge Summary" --specialty Cardiology \
  -o ./sample/healthcare
```

---

### 2.3  `generate_retail_product.py`

Generates catalogue items for e-commerce scenarios.

| Flag | Required | Description | Default |
| ---- | -------- | ----------- | ------- |
| `-i, --industry` | ❌ | Theme / vertical (electronics, fashion…) | `general` |
| `-n, --count`    | ❌ | Number of products | `1` |
| `-o, --output`   | ❌ | Output folder | `./output` |
| `-f, --format`   | ❌ | `yaml` \| `json` \| `text` | `yaml` |

Example:

```bash
python generate_retail_product.py \
  -i electronics -n 100 -f yaml -o ./sample/retail-products
```

---

## 3. Quick-start

```bash
# 1. Clone repo & enter folder
# 2. Create .env (see above)
# 3. Install deps
pip install -r scripts/data-generators/requirements.txt

# 4. Generate sample data
cd scripts/data-generators
python generate_tech_support.py -d "Contoso Banking App" -n 5
```

All output files are written individually with a UUID-based filename and enriched with generation metadata where applicable.
