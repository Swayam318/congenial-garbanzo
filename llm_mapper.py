import os
import json
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai

# ✅ Load .env and configure Gemini
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-2.0-flash")

# 🔹 Split fields into chunks
def chunk_list(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

# 🔹 Generate prompt for each chunk
def generate_prompt(erp_name, service_name, fields_chunk, raw_data):
    field_lines = ""
    for field in fields_chunk:
        example = raw_data.get(field, "")
        field_lines += f"- **{field}**: Example → `{example}`\n"

    return f"""
You are an expert in ERP systems and data standardization.

Your task is to map raw ERP field names from an API response to clean, standardized field names using semantic meaning and business logic.

ERP: {erp_name}
Service: {service_name}

Field Mapping Objective:
- Convert cryptic ERP-style fields to human-readable, snake_case names.
- Add prefixes like `employee_`, `organization_`, `customer_` where meaningful.
- Be specific, readable, and consistent.

Here are the fields and example values:

{field_lines}

Return only a valid Python dictionary like:
{{
  "field_one": "standard_name_one",
  "field_two": "standard_name_two"
}}

No extra text, markdown, or commentary.
"""

# 🔹 Main mapping function
def generate_mapping_suggestions(unknown_fields, raw_data, erp_name="sap", service_name="business_partner"):
    suggestions = {}
    all_chunks = list(chunk_list(unknown_fields, 30))

    for idx, chunk in enumerate(all_chunks):
        print(f"🔁 Processing chunk {idx + 1}/{len(all_chunks)}...")
        prompt = generate_prompt(erp_name, service_name, chunk, raw_data)
        try:
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            '''print(f"🧾 Raw LLM Response for chunk {idx + 1}:\n{response_text}\n")'''

            # Extract JSON from response
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            json_part = response_text[start:end]
            mapping = json.loads(json_part)

            # Validate and add
            if isinstance(mapping, dict):
                for field, common_name in mapping.items():
                    if common_name:  # Only add valid names
                        suggestions[field] = common_name.strip()
                    else:
                        print(f"⚠️ Skipping blank mapping for: {field}")
            else:
                print(f"⚠️ Invalid format in chunk {idx + 1}")
        except Exception as e:
            print(f"❌ Error in chunk {idx + 1}: {e}")
            for field in chunk:
                suggestions[field] = None

    '''# Optional: Save all suggestions for manual review
    try:
        pd.DataFrame.from_dict(suggestions, orient='index', columns=["common_name"]).to_csv("debug_llm_mappings.csv")
        print("📄 Dumped suggestions to debug_llm_mappings.csv")
    except Exception as e:
        print(f"⚠️ Failed to save debug dump: {e}")'''

    return suggestions
