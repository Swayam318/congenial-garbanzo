import requests
import json
import xmlrpc.client
from dotenv import load_dotenv
load_dotenv()


def parse_access_key(access_key):
    parts = access_key.split("|")
    if len(parts) != 3:
        raise ValueError("Access key format must be 'db|username|password'")
    return parts

def fetch_erp_data(api_url, access_key, erp_name,service_name=None):
    try:
        if erp_name == "sap":
            headers = {"apikey": access_key}
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            return response.json()
        elif erp_name == "odoo":
            if not service_name:
                raise ValueError("Service name is required for Odoo.")
            db, username, password = parse_access_key(access_key)
            common = xmlrpc.client.ServerProxy(f"{api_url}/xmlrpc/2/common")
            uid = common.authenticate(db, username, password, {})
            if not uid:
                print("❌ Authentication failed.")
                return None
            print(f"✅ Odoo Authenticated. UID: {uid}")

            # Map service names to Odoo model names
            odoo_model_map = {
                "employees": "hr.employee",
                "contacts": "res.partner",
                "rateplan": "res.partner",  # change as needed
                # Add more as needed
            }
            
            model_name = odoo_model_map.get(service_name, "res.partner")  # fallback model
            print(f"🔍 Using Odoo model: {model_name}")
            
            models = xmlrpc.client.ServerProxy(f"{api_url}/xmlrpc/2/object")
            
            # Fetch data
            records = models.execute_kw(
                db, uid, password,
                model_name, 'search_read',
                [[]], {'limit': 5}
            )
            
            return records[0] if records else {}

    except Exception as e:
        print("❌ Error fetching ERP data:", e)
        return None

def post_erp_data(api_url, access_key, erp_name, model_name, data):
    try:
        if erp_name == "odoo":
            db, username, password = parse_access_key(access_key)
            common = xmlrpc.client.ServerProxy(f"{api_url}/xmlrpc/2/common")
            uid = common.authenticate(db, username, password, {})
            if not uid:
                print("❌ Authentication failed.")
                return

            models = xmlrpc.client.ServerProxy(f"{api_url}/xmlrpc/2/object")
           
            # ✅ Validate using fields_get
            valid_fields = models.execute_kw(db, uid, password, model_name, 'fields_get', [], {'attributes': ['string']})
            cleaned_data = {k: v for k, v in data.items() if k in valid_fields}

            record_id = models.execute_kw(db, uid, password, model_name, 'create', [cleaned_data])
            print(f"🎉 New record created in Odoo model `{model_name}`: ID {record_id}")
        else:
            print("⚠️ POST not implemented for ERP:", erp_name)
    except Exception as e:
        print("❌ Error posting to ERP:", e)

def delete_erp_data(api_url, access_key, erp_name, model_name, record_id):
    try:
        if erp_name == "odoo":
            db, username, password = parse_access_key(access_key)
            common = xmlrpc.client.ServerProxy(f"{api_url}/xmlrpc/2/common")
            uid = common.authenticate(db, username, password, {})
            models = xmlrpc.client.ServerProxy(f"{api_url}/xmlrpc/2/object")
           

            success = models.execute_kw(db, uid, password, model_name, 'unlink', [[record_id]])
            if success:
                print(f"🗑️ Successfully deleted record ID {record_id} from `{model_name}`.")
            else:
                print(f"⚠️ Failed to delete record ID {record_id}.")
        else:
            print("⚠️ DELETE not implemented for ERP:", erp_name)
    except Exception as e:
        print("❌ Error deleting from ERP:", e)

def update_erp_data(api_url, access_key, erp_name, model_name, record_id, data):
    try:
        if erp_name == "odoo":
            db, username, password = parse_access_key(access_key)
            common = xmlrpc.client.ServerProxy(f"{api_url}/xmlrpc/2/common")
            uid = common.authenticate(db, username, password, {})
            models = xmlrpc.client.ServerProxy(f"{api_url}/xmlrpc/2/object")
           
            # ✅ Validate with fields_get
            valid_fields = models.execute_kw(db, uid, password, model_name, 'fields_get', [], {'attributes': ['string']})
            cleaned_data = {k: v for k, v in data.items() if k in valid_fields}

            success = models.execute_kw(db, uid, password, model_name, 'write', [[record_id], cleaned_data])
            if success:
                print(f"🔄 Successfully updated record ID {record_id} in `{model_name}`.")
            else:
                print(f"⚠️ Failed to update record ID {record_id}.")
        else:
            print("⚠️ UPDATE not implemented for ERP:", erp_name)
    except Exception as e:
        print("❌ Error updating ERP:", e)
