import os
import pandas as pd
from llm_mapper import generate_mapping_suggestions

MAPPINGS_DIR = "mappings"

def update_mapping_file(service_name, erp_name, raw_data):
    file_path = os.path.join(MAPPINGS_DIR, f"{service_name}.csv")

    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
    else:
        df = pd.DataFrame(columns=["common_name", erp_name])

    # Make sure the ERP column exists
    if erp_name not in df.columns:
        df[erp_name] = ""

    all_fields = list(raw_data.keys())
    existing_fields = df[erp_name].dropna().tolist()
    new_fields = [f for f in all_fields if f not in existing_fields]

    if new_fields:
        print(f"🧠 Detected {len(new_fields)} new fields: {new_fields}")
        suggestions = generate_mapping_suggestions(new_fields, raw_data, erp_name, service_name)

        for field in new_fields:
            # ✅ Reuse existing common_name if field is already mapped in another ERP column
            matched_common_name = None
            for _, row in df.iterrows():
                if field in row.values:
                    matched_common_name = row["common_name"]
                    df.at[row.name, erp_name] = field
                    break

            # ✅ If not found, insert new row
            if not matched_common_name:
                common_name = suggestions.get(field)
                if common_name:
                    new_row = {col: "" for col in df.columns}
                    new_row["common_name"] = common_name
                    new_row[erp_name] = field
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                else:
                    print(f"⚠️ Skipping unmapped field: {field}")

        # Save updated mapping
        df.to_csv(file_path, index=False)
        print(f"✅ Mapping file updated: {file_path}")
    else:
        print("✅ No new fields to map.")

    return df
