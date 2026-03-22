# Attendance System

A modern, role-based attendance tracker for church services.

## **🛠️ Technical Stack**

- **Backend:** Python / Flask
- **Database:** Supabase (PostgreSQL) + Row-Level Security (RLS)
- **Auth:** Flask-Login & Werkzeug (Password Hashing)
- **Frontend:** Vanilla JS, CSS (Glassmorphism), HTML5

### **🚀 Setup**

1. **Venv:** `python -m venv venv` & `pip install -r requirements.txt`
2. **Env:** Create `.env` with:
   - `FLASK_SECRET_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
3. **Database:** Run SQL schema for `staff`, `members`, and `attendance` tables.
4. **Run:** `python app.py`

### **🔐 Security Architecture**

- **Backend:** Flask uses `SERVICE_ROLE_KEY` to bypass RLS and manage data.
- **Frontend:** No direct database keys exposed; all actions proxied through Flask.
- **RBAC:** \* **Admin:** Full CRUD + Dashboard access.
  - **Usher:** Member search and Check-In only.

### **📂 Structure**

- `app.py`: Server logic & Supabase routes.
- `static/`: UI styling & frontend logic (Modals/Spinners).
- `templates/`: Jinja2 templates for Login, Attendance, and Admin views.

**Would you like me to generate the `requirements.txt` file for you now?**
