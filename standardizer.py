import os
import pandas as pd

MAPPINGS_DIR = "mappings"

def standardize_response(service_name, erp_name, raw_data):
    file_path = os.path.join(MAPPINGS_DIR, f"{service_name}.csv")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Mapping file for service '{service_name}' not found.")

    df = pd.read_csv(file_path)
    if erp_name not in df.columns:
        raise ValueError(f"ERP '{erp_name}' not found in mapping file.")

    erp_to_common = {
        row[erp_name]: row["common_name"]
        for _, row in df.iterrows()
        if pd.notna(row[erp_name]) and pd.notna(row["common_name"])
    }

    standardized = {}
    for k, v in raw_data.items():
        common = erp_to_common.get(k)
        if common:
            standardized[common] = v
    return standardized
