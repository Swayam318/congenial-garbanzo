from datetime import datetime

def normalize_input_fields(user_input: dict, common_to_erp: dict) -> dict:
    """
    Normalize and map user input using standardized field names to ERP-specific fields.

    Args:
        user_input: Dict from user (with common_name keys)
        common_to_erp: Dict mapping from common_name → erp_field

    Returns:
        Normalized and ERP-mapped dictionary.
    """
    normalized = {}

    for common_key, value in user_input.items():
        erp_key = common_to_erp.get(common_key)
        if not erp_key:
            print(f"⚠️ Unknown field: '{common_key}'. Skipping.")
            continue

        # Normalize value types
        normalized_value = value

        # Convert boolean
        if value.lower() in ("true", "false"):
            normalized_value = value.lower() == "true"

        # Convert numbers
        elif value.isdigit():
            normalized_value = int(value)
        else:
            try:
                normalized_value = float(value)
            except ValueError:
                pass  # keep as string if not number

        # Convert dates
        for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"):
            try:
                normalized_value = datetime.strptime(value, fmt).strftime("%Y-%m-%d")
                break
            except ValueError:
                continue

        normalized[erp_key] = normalized_value

    return normalized
