import os
from datetime import datetime, date
from functools import wraps
from io import BytesIO

from flask import Flask, render_template, request, jsonify, redirect, send_file, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from supabase import create_client, Client
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Load environment variables
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


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash("Admin access required.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
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
@admin_required
def index():
    return render_template('index.html')


@app.route('/get-members', methods=['GET'])
@admin_required
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
@admin_required
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
@admin_required
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
@admin_required
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
@admin_required
def admin_only():
    if current_user.role != 'admin':
        return "Access Denied: Admins Only", 403
    return render_template('admin.html')


@app.route('/admin')
@admin_required
def admin_dashboard():
    if current_user.role != 'admin':
        return "Unauthorized", 403
    return render_template('admin.html')


@app.route('/admin-stats')
@admin_required
def admin_stats():
    # Only allow admins to see this
    if current_user.role != 'admin':
        return jsonify({"message": "Unauthorized"}), 403

    # Get today's date in GMT/UTC
    today_gmt = datetime.utcnow().date().isoformat()

    # Query 1: Total Attendance Today
    today_res = supabase.table("attendance") \
        .select("id", count="exact") \
        .eq("check_in_date", today_gmt).execute()

    # Query 2: Breakdown by Service Type (All time or Last 30 days)
    # We'll fetch the count grouped by 'type'
    breakdown_res = supabase.rpc("get_attendance_breakdown").execute()

    return jsonify({
        "today_count": today_res.count,
        "breakdown": breakdown_res.data
    })


@app.route('/api/stats-by-date')
@admin_required
def stats_by_date():
    target_date = request.args.get('date')
    if not target_date:
        return jsonify({"count": 0}), 400

    # Query Supabase for the specific GMT date
    res = supabase.table("attendance") \
        .select("id", count="exact") \
        .eq("check_in_date", target_date).execute()

    return jsonify({"count": res.count})


@app.route('/export-attendance')
@admin_required
def export_attendance():
    if current_user.role != 'admin':
        return "Unauthorized", 403

    # Get the date from the query string (e.g., /export-attendance?date=2026-03-28)
    target_date = request.args.get(
        'date', datetime.utcnow().date().isoformat())

    # Fetch data from Supabase with a Join to get Member Names
    # Note: Ensure your 'attendance' table has a foreign key to 'members'
    res = supabase.table("attendance") \
        .select("created_at, type, notes, members(full_name, phone_number, scd_group)") \
        .eq("check_in_date", target_date).execute()

    if not res.data:
        return "No data for this date", 404

    # Flatten the nested Supabase JSON for Excel
    flattened_data = []
    for row in res.data:
        flattened_data.append({
            "Time (GMT)": row['created_at'],
            "Full Name": row['members']['full_name'],
            "Phone": row['members']['phone_number'],
            "Group": row['members']['scd_group'],
            "Service": row['type'],
            "Notes": row['notes']
        })

    # Create Excel in Memory
    df = pd.DataFrame(flattened_data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Attendance')
    output.seek(0)

    return send_file(
        output,
        attachment_filename=f"Attendance_{target_date}.xlsx",
        as_attachment=True
    )


if __name__ == '__main__':
    app.run(debug=True)
