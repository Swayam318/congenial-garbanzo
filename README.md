**ERP Integration and Standardization Framework:**

A powerful and secure framework to integrate, standardize, and interact with multiple ERP systems like Odoo and SAP 
using APIs, LLM-powered field mapping, and a Flask-based web UI.
 
**Features:**
- Dynamic standardization of ERP data across multiple services (HR, Finance, SCM, etc.)
- LLM-powered field mapping via Gemini API
- Secure credential management with Fernet encryption
- Support for GET, POST, PUT, DELETE operations via CLI and Flask Web UI
- Mapping visualization and editable forms per service
- Ready-to-deploy on Render.com
  
 **Setup Instructions (Local)**
 
 1. **Clone the repo**
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
 
 2. **Create a virtual environment**
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
 
 3. **Install dependencies**
   pip install -r requirements.txt
 
 4. **Create a .env file with:**
   ODOO_URL=...
   ODOO_DB=...
   ODOO_USERNAME=...
   ODOO_PASSWORD=...
   ENCRYPTION_KEY=...
   GEMINI_API_KEY=...
 
 **Run Locally**
 CLI Mode: python main.py
 Web UI Mode (if app.py is present): python app.py
 
**Deploy on Render.com**
- Create new Web Service
- Build Command: pip install -r requirements.txt
- Start Command: gunicorn app:app
- Add Environment Variables from .env
  
 **Encrypting Credentials:**
 Use encrypter.py to generate a Fernet key and encrypt your Odoo password.
 
 **Gemini LLM Setup**
 Add your API key to .env as GEMINI_API_KEY
