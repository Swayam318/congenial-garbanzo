def extract_first_record(json_data, erp_name=None):
    def is_valid_field(k, v):
        # Skip internal/meta fields
        if k.startswith("__"):
            return False
        if isinstance(v, dict) and ("__deferred" in v or "uri" in v):
            return False
        # Skip noisy/media/Odoo-specific fields
        noisy_prefixes = ("avatar_", "image_", "message_", "website_message_", "activity_", "rating_ids", "badge_ids")
        if any(k.startswith(prefix) for prefix in noisy_prefixes):
            return False
        # Skip large binary data
        if isinstance(v, str) and len(v) > 500:
            return False
        return True

    # 🟣 Odoo response is already a clean dict
    if erp_name == "odoo" and isinstance(json_data, dict):
        return {k: v for k, v in json_data.items() if is_valid_field(k, v)}

    # 🔵 SAP-style or nested responses
    if isinstance(json_data, dict):
        for key, value in json_data.items():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                return {k: v for k, v in value[0].items() if is_valid_field(k, v)}
            elif isinstance(value, dict):
                nested = extract_first_record(value, erp_name)
                if nested:
                    return nested
        if all(isinstance(v, (str, int, float, bool, type(None))) for v in json_data.values()):
            return {k: v for k, v in json_data.items() if is_valid_field(k, v)}

    elif isinstance(json_data, list) and json_data and isinstance(json_data[0], dict):
        return {k: v for k, v in json_data[0].items() if is_valid_field(k, v)}

    return None
