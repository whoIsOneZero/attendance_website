import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from supabase import create_client, Client
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

# --- Supabase Setup ---
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

# --- Flask-Login Setup ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, id, email, role):
        self.id = id
        self.email = email
        self.role = role


@login_manager.user_loader
def load_user(user_id):
    res = supabase.table("staff").select("*").eq("id", user_id).execute()
    if res.data:
        u = res.data[0]
        return User(u['id'], u['email'], u['role'])
    return None

# --- ROUTES ---


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').lower().strip()
        password = request.form.get('password')

        res = supabase.table("staff").select("*").eq("email", email).execute()

        if res.data and check_password_hash(res.data[0]['password_hash'], password):
            user_data = res.data[0]
            user = User(user_data['id'], user_data['email'], user_data['role'])
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password')

    return render_template('login.html')


@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/get-members', methods=['GET'])
@login_required
def get_members():
    try:
        # Added scd_group and membership_type so the frontend has them for editing
        response = supabase.table("members").select(
            "id, full_name, phone_number, scd_group, membership_type"
        ).execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/create-member', methods=['POST'])
@login_required
def create_member():
    data = request.json
    try:
        # Dynamic insertion from the modal fields
        response = supabase.table("members").insert({
            "full_name": data.get("full_name"),
            "phone_number": data.get("phone_number"),
            "scd_group": data.get("scd_group"),
            "membership_type": data.get("membership_type")
        }).execute()

        if not response.data:
            return jsonify({"status": "error", "message": "No data returned from database."}), 500

        return jsonify({"status": "success", "member": response.data[0]}), 201
    except Exception as e:
        print(f"CREATE ERROR: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/update-member', methods=['POST'])
@login_required
def update_member():
    data = request.json
    member_id = data.get("id")

    try:
        # Full update to allow fixing names or changing membership types
        response = supabase.table("members").update({
            "full_name": data.get("full_name"),
            "phone_number": data.get("phone_number"),
            "scd_group": data.get("scd_group"),
            "membership_type": data.get("membership_type")
        }).eq("id", member_id).execute()

        return jsonify({"status": "success", "message": "Member updated!"}), 200
    except Exception as e:
        print(f"UPDATE ERROR: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/submit', methods=['POST'])
@login_required
def submit_attendance():
    data = request.json
    try:
        response = supabase.table("attendance").insert({
            "member_id": data.get("member_id"),
            "attendance_type": data.get("type"),
            "notes": data.get("notes")
        }).execute()

        return jsonify({"status": "success", "message": "Marked present!"}), 200
    except Exception as e:
        if "duplicate key value" in str(e):
            return jsonify({"status": "error", "message": "Already marked present today."}), 400
        return jsonify({"status": "error", "message": "Submission failed."}), 500


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/admin-dashboard')
@login_required
def admin_only():
    if current_user.role != 'admin':
        return "Access Denied: Admins Only", 403
    return render_template('admin.html')


if __name__ == '__main__':
    app.run(debug=True)
