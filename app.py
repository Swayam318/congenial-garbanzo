from flask import Flask, render_template, request, jsonify
from fetch_data import (fetch_erp_data, post_erp_data, update_erp_data, delete_erp_data)
from smart_extractor import extract_first_record
from auto_mapper import update_mapping_file
from standardizer import standardize_response
from normalize import normalize_input_fields
import pandas as pd
import os
import xmlrpc.client
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Ensure mappings directory exists
MAPPINGS_DIR = "mappings"
os.makedirs(MAPPINGS_DIR, exist_ok=True)

# Service to model mapping (only the 5 services you specified)
SERVICE_TO_MODEL = {
    "business": "business.module",  # Update with actual Odoo model
    "contacts": "res.partner",
    "customer": "res.partner", 
    "employee": "hr.employee",
    "rateplan": "product.pricelist"  # Update with actual Odoo model
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/execute', methods=['POST'])
def execute():
    data = request.json
    try:
        choice = data.get('choice')
        erp_name = data.get('erp_name', '').lower().strip()
        api_url = data.get('api_url', '').strip()
        service_name = data.get('service_name', '').lower().strip()

        # Validate service
        if service_name not in SERVICE_TO_MODEL:
            return jsonify({"error": f"Invalid service: {service_name}"}), 400

        # Load access key
        if erp_name == "odoo":
            ODOO_DB = os.getenv("ODOO_DB")
            ODOO_USERNAME = os.getenv("ODOO_USERNAME")
            fernet = Fernet(os.getenv("FERNET_KEY"))
            ODOO_PASSWORD = fernet.decrypt(os.getenv("ODOO_PASSWORD_ENC").encode()).decode()
            access_key = f"{ODOO_DB}|{ODOO_USERNAME}|{ODOO_PASSWORD}"
        elif erp_name == "sap":
            access_key = os.getenv("SAP_ACCESS_KEY")
        else:
            return jsonify({"error": f"Unsupported ERP: {erp_name}"}), 400

        if choice == "1":  # Fetch operation
            data = fetch_erp_data(api_url, access_key, erp_name, service_name)
            if not data:
                return jsonify({"error": "No data returned from ERP"}), 400

            record = extract_first_record(data, erp_name)
            if not record:
                return jsonify({"error": "No valid record found"}), 400

            update_mapping_file(service_name, erp_name, record)
            standardized = standardize_response(service_name, erp_name, record)
            
            return jsonify({
                "status": "success",
                "erp_fields": list(record.keys()),
                "standardized_data": standardized
            })

        elif choice == "2":  # CRUD operation
            action = data.get('action', '').lower().strip()
            record_id = data.get('record_id')
            fields = data.get('fields', {})

            model_name = SERVICE_TO_MODEL[service_name]

            # Field mapping
            mapping_path = os.path.join(MAPPINGS_DIR, f"{service_name}.csv")
            if not os.path.exists(mapping_path):
                return jsonify({"error": f"No mapping for {service_name}"}), 400

            df = pd.read_csv(mapping_path)
            if erp_name not in df.columns:
                return jsonify({"error": f"No {erp_name} mapping for {service_name}"}), 400

            common_to_erp = {
                row["common_name"]: row[erp_name]
                for _, row in df.iterrows()
                if pd.notna(row["common_name"]) and pd.notna(row[erp_name])
            }

            # Execute operation
            erp_data = normalize_input_fields(fields, common_to_erp)
            if action == "post":
                result = post_erp_data(api_url, access_key, erp_name, model_name, erp_data)
            elif action == "update":
                result = update_erp_data(api_url, access_key, erp_name, model_name, record_id, erp_data)
            elif action == "delete":
                result = delete_erp_data(api_url, access_key, erp_name, model_name, record_id)
            else:
                return jsonify({"error": "Invalid action"}), 400

            return jsonify({
                "status": "success",
                "result": result
            })

        else:
            return jsonify({"error": "Invalid mode selected"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)