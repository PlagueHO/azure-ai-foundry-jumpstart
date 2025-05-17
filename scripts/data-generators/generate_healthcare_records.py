"""
Generate synthetic healthcare records using Azure OpenAI via Semantic Kernel.
This script creates anonymized and entirely fictional medical documents.

Example usage:
python scripts/data-generators/generate_healthcare_records.py -n 10 -o ./sample-data/healthcare/ --format yaml --document-type "Clinic Note" --specialty "Cardiology"
python scripts/data-generators/generate_healthcare_records.py -n 5 -o ./sample-data/healthcare/ --format json --document-type "Discharge Summary"
python scripts/data-generators/generate_healthcare_records.py -n 3 -o ./sample-data/healthcare/ --format text --document-type "Referral Letter" --specialty "Oncology"

Prerequisites
-------------
1. pip install semantic-kernel python-dotenv pyyaml colorama
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
import random
import json
import uuid

import yaml
from colorama import Fore, Style

from synthetic_data_generator import SyntheticDataGenerator

# -------------------------------------------------------------------------
# CLI arguments
# -------------------------------------------------------------------------
parser = argparse.ArgumentParser(
    description="Generate synthetic healthcare records using Azure OpenAI."
)
parser.add_argument(
    "-n",
    "--count",
    type=int,
    default=1,
    help="Number of healthcare records to generate.",
)
parser.add_argument(
    "-o",
    "--output",
    type=Path,
    default=Path.cwd() / "output_healthcare",
    help="Folder where output files will be written.",
)
parser.add_argument(
    "-f",
    "--format",
    choices=["yaml", "json", "text"],
    default="yaml",
    help="Output file format (yaml|json|text). Defaults to yaml.",
)
parser.add_argument(
    "--document-type",
    type=str,
    default="Clinic Note",
    help="Type of medical document to generate (e.g., 'Clinic Note', 'Discharge Summary', 'Referral Letter', 'Operative Note', 'Pathology Report').",
)
parser.add_argument(
    "--specialty",
    type=str,
    default="General Medicine",
    help="Optional medical specialty for the record (e.g., 'Cardiology', 'Pediatrics', 'Oncology').",
)
args = parser.parse_args()

args.output.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------------------
# SyntheticDataGenerator setup
# -------------------------------------------------------------------------
generator = SyntheticDataGenerator()
logger = generator.logger

# -------------------------------------------------------------------------
# Prompt templates per format
# -------------------------------------------------------------------------
def _build_prompt(output_format: str) -> str:
    base = """
You are an AI assistant tasked with generating realistic but entirely FAKE and ANONYMIZED healthcare documents.
DO NOT include any real patient names, addresses, phone numbers, or any other personally identifiable information (PII). Use placeholder names like "Jane Doe", "John Smith" or fictional names.
Ensure all medical details, conditions, and treatments are plausible for the specified document type and specialty, but are entirely fictional.
The generated content should be suitable for testing data processing pipelines and AI models without raising privacy concerns or violating content safety policies.

Document Type: {{$document_type}}
Specialty: {{$specialty}}
Record ID: {{$record_id}}
Creation Date: {{$created_at}}
"""
    if output_format == "yaml":
        return base + """
Output MUST be valid YAML. Do not wrap in markdown.

Generate a FAKE and ANONYMIZED '{{$document_type}}' for the '{{$specialty}}' specialty.

record_id: {{$record_id}}
document_type: '{{$document_type}}'
specialty: '{{$specialty}}'
created_at: {{$created_at}} # ISO 8601 timestamp for document creation
patient_details:
  fictional_name: "Fictional Patient Name (e.g., Jane Doe, Robert Smith)"
  age: integer (e.g., 35)
  gender: "Male | Female | Other | Prefer not to say"
  fictional_patient_id: "Fake ID (e.g., MRN-FAKE-12345)"
document_content:
  title: "Clear title for the document (e.g., Cardiology Clinic Follow-up Note)"
  sections: # Array of sections, each with a heading and paragraph(s) of text.
    - heading: "Reason for Visit/Consultation" # or "Indication for Procedure" for operative notes, "Clinical History" for pathology etc.
      content: "Detailed fictional paragraph."
    - heading: "History of Present Illness" # or "Procedure Details", "Gross Description"
      content: "Detailed fictional paragraph."
    - heading: "Past Medical History" # (optional, can be brief)
      content: "Fictional relevant past conditions."
    - heading: "Assessment" # or "Findings", "Microscopic Description"
      content: "Fictional assessment or findings."
    - heading: "Plan" # or "Recommendations", "Impression/Diagnosis", "Post-operative Care"
      content: "Fictional treatment plan or recommendations."
  # Add other relevant sections based on document_type. For example:
  # For Discharge Summary: "Hospital Course", "Discharge Medications", "Follow-up Instructions"
  # For Operative Note: "Preoperative Diagnosis", "Postoperative Diagnosis", "Anesthesia", "Complications"
  # For Referral Letter: "Referring Physician", "Receiving Physician", "Reason for Referral"
author_details:
  fictional_doctor_name: "Dr. Fictional Name"
  fictional_clinic_name: "Fictional Clinic/Hospital Name"
  fictional_contact_info: "fake-email@example.com / 555-0100-FAKE"

Return ONLY the YAML. DO NOT INCLUDE ANY OTHER TEXT. DO NOT INCLUDE ```yaml OR ANY OTHER MARKUP.
"""
    if output_format == "json":
        return base + """
Output MUST be valid JSON. Do not wrap in markdown.

{
  "record_id": "{{$record_id}}",
  "document_type": "{{$document_type}}",
  "specialty": "{{$specialty}}",
  "created_at": "{{$created_at}}",
  "patient_details": {
    "fictional_name": "Fictional Patient Name (e.g., Jane Doe, Robert Smith)",
    "age": 35,
    "gender": "Female",
    "fictional_patient_id": "MRN-FAKE-12345"
  },
  "document_content": {
    "title": "Cardiology Clinic Follow-up Note",
    "sections": [
      {
        "heading": "Reason for Visit/Consultation",
        "content": "Detailed fictional paragraph."
      },
      {
        "heading": "History of Present Illness",
        "content": "Detailed fictional paragraph."
      },
      {
        "heading": "Assessment",
        "content": "Fictional assessment or findings."
      },
      {
        "heading": "Plan",
        "content": "Fictional treatment plan or recommendations."
      }
    ]
  },
  "author_details": {
    "fictional_doctor_name": "Dr. Fictional Name",
    "fictional_clinic_name": "Fictional Clinic/Hospital Name",
    "fictional_contact_info": "fake-email@example.com / 555-0100-FAKE"
  }
}

Ensure the 'sections' array contains appropriate headings and content for a '{{$document_type}}' in '{{$specialty}}'.
The content must be entirely fictional and anonymized.
Return ONLY the JSON. DO NOT INCLUDE ANY OTHER TEXT. DO NOT INCLUDE ```json OR ANY OTHER MARKUP.
"""
    # TEXT (free-form)
    return base + """
Generate a FAKE and ANONYMIZED '{{$document_type}}' for the '{{$specialty}}' specialty.
The output should be plain text, well-formatted, and easy to read.
Include sections like:
- Patient Information (Fictional Name, Age, Gender, Fictional ID)
- Document Title
- Date of Service/Creation: {{$created_at}}
- Key Sections relevant to a '{{$document_type}}' (e.g., Reason for Visit, History, Assessment, Plan, Findings, Recommendations).
- Authored by (Fictional Doctor, Fictional Clinic).

Example Structure:

Record ID: {{$record_id}}
Document Type: {{$document_type}}
Specialty: {{$specialty}}
Created At: {{$created_at}}

Patient: Jane Doe (Fictional)
Age: 45
Gender: Female
Patient ID: FAKE-PT-001

--- Document: {{$document_type}} ---
Title: Example {{$document_type}} for {{$specialty}}

[Section Heading 1]
[Fictional content for section 1...]

[Section Heading 2]
[Fictional content for section 2...]

[And so on, with relevant sections for the document type...]

---
Authored by:
Dr. Fictional Name
Fictional Clinic for {{$specialty}}
Contact: fake-doctor@example.com / 555-0101-FAKE

Ensure all information is plausible but entirely fictional and anonymized.
"""

PROMPT_TEMPLATE_STRING = _build_prompt(args.format)
prompt_function = generator.create_prompt_function(
    template=PROMPT_TEMPLATE_STRING,
    function_name="generate_healthcare_record",
    plugin_name="healthcare",
    prompt_description="Create realistic but fake and anonymized healthcare records.",
    input_variables=[
        {"name": "document_type", "description": "Type of medical document", "is_required": True},
        {"name": "specialty", "description": "Medical specialty", "is_required": True},
        {"name": "record_id", "description": "Pre-generated UUID for the record", "is_required": True},
        {"name": "created_at", "description": "Pre-generated ISO-timestamp for record creation", "is_required": True},
    ],
    max_tokens=1500, # Increased token limit for potentially longer medical notes
    temperature=0.6 # Slightly lower temperature for more factual-sounding (but still fake) text
)

# -------------------------------------------------------------------------
# Generation loop
# -------------------------------------------------------------------------
def generate_records(count: int, out_dir: Path, doc_type: str, specialty: str, output_format: str) -> None:
    required_fields_yaml_json = {
        "record_id", "document_type", "specialty", "created_at",
        "patient_details", "document_content", "author_details"
    }
    # Document types can be expanded or randomized if needed
    document_types_available = [
        "Clinic Note", "Discharge Summary", "Referral Letter",
        "Operative Note", "Pathology Report", "Consultation Note",
        "Progress Note", "Radiology Report"
    ]

    for idx in range(1, count + 1):
        current_doc_type = doc_type if doc_type else random.choice(document_types_available)
        record_id: str = str(uuid.uuid4())
        created_at: str = _dt.datetime.now(_dt.timezone.utc).isoformat()

        output_content: str = ""
        record_data: dict | None = None

        for attempt in range(1, 4):
            logger.debug(f"Attempt {attempt}/3 for record {idx}/{count} (Type: {current_doc_type}, Specialty: {specialty})")
            try:
                output_content = prompt_function(
                    document_type=current_doc_type,
                    specialty=specialty,
                    record_id=record_id,
                    created_at=created_at
                ).strip()

                if not output_content:
                    raise ValueError("LLM returned empty content.")

                if output_format == "yaml":
                    record_data = yaml.safe_load(output_content)
                elif output_format == "json":
                    # Attempt to strip markdown fences if present, as LLMs sometimes add them
                    if output_content.startswith("```json"):
                        output_content = output_content.removeprefix("```json").removesuffix("```").strip()
                    elif output_content.startswith("```"): # Generic markdown fence
                         output_content = output_content.removeprefix("```").removesuffix("```").strip()
                    record_data = json.loads(output_content)
                else:  # text format
                    break  # No further validation needed for text

                if not isinstance(record_data, dict):
                    raise ValueError(f"Output is not a dictionary. Got: {type(record_data)}")
                if not required_fields_yaml_json.issubset(record_data.keys()):
                    missing = required_fields_yaml_json - set(record_data.keys())
                    raise ValueError(f"Missing core fields from LLM: {', '.join(missing)}")
                
                # Basic check for PII-like content (simple check, not foolproof)
                if output_format != "text" and record_data:
                    patient_name = record_data.get("patient_details", {}).get("fictional_name", "")
                    if "real name" in patient_name.lower() or "@" in patient_name : # very basic check
                         logger.warning(f"Potential PII-like name detected: '{patient_name}'. Please review output.")

                break  # Success
            except Exception as e:
                logger.error(f"Raw output on error (attempt {attempt}):\n---\n{output_content}\n---")
                if attempt < 3:
                    logger.warning(f"Attempt {attempt}/3 failed for record {idx} - retrying: {e}")
                else:
                    logger.error(f"All 3 attempts failed for record {idx}. Error: {e}")
                    output_content = "" # Ensure output is empty if all attempts failed
                    record_data = None
                    break # Break from retry loop

        if not output_content and output_format != "text":
            logger.error(f"Skipping record {idx} (Type: {current_doc_type}) due to persistent errors.")
            continue
        
        if not output_content and output_format == "text":
             logger.error(f"Skipping record {idx} (Type: {current_doc_type}) as no text content was generated after retries.")
             continue


        generated_at_ts = _dt.datetime.now(_dt.timezone.utc).isoformat()
        ext = {"yaml": "yaml", "json": "json", "text": "txt"}[output_format]
        # Sanitize document type and specialty for filename
        safe_doc_type = "".join(c if c.isalnum() else "_" for c in current_doc_type)
        safe_specialty = "".join(c if c.isalnum() else "_" for c in specialty)
        file_path = out_dir / f"record_{safe_doc_type}_{safe_specialty}_{record_id}.{ext}"

        with file_path.open("w", encoding="utf-8") as fp:
            if output_format == "yaml":
                if record_data:
                    record_data["generation_metadata"] = {"generated_at_script": generated_at_ts, "script_version": "1.0"}
                    yaml.safe_dump(record_data, fp, sort_keys=False, allow_unicode=True)
            elif output_format == "json":
                if record_data:
                    record_data["generation_metadata"] = {"generated_at_script": generated_at_ts, "script_version": "1.0"}
                    json.dump(record_data, fp, indent=2, ensure_ascii=False)
            else:  # text
                fp.write(f"{output_content}\n\n---Generation Metadata---\nGenerated At (Script): {generated_at_ts}\nScript Version: 1.0\n")
        
        logger.info("%s✔ Generated %s%s (Type: %s, Specialty: %s)", Fore.GREEN, file_path, Style.RESET_ALL, current_doc_type, specialty)

# -------------------------------------------------------------------------
# Entry point
# -------------------------------------------------------------------------
if __name__ == "__main__":
    logger.info(
        f"Starting generation of {args.count} healthcare record(s) "
        f"(Document Type: {args.document_type or 'Any'}, Specialty: {args.specialty}, Format: {args.format})..."
    )
    generate_records(args.count, args.output, args.document_type, args.specialty, args.format)
    logger.info("Generation complete.")

