import os
from dotenv import load_dotenv
from supabase import create_client, Client
from werkzeug.security import generate_password_hash

# Load environment variables from .env
load_dotenv()

# Initialize Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)


def create_staff_member(email, password, full_name, role='usher'):
    """
    Hashes the password and inserts a new staff member into the 'staff' table.
    """
    # 1. Hash the password safely
    hashed_password = generate_password_hash(password)

    # 2. Prepare the data
    staff_data = {
        "email": email.lower().strip(),
        "password_hash": hashed_password,
        "full_name": full_name,
        "role": role  # Must be 'admin' or 'usher'
    }

    try:
        # 3. Insert into Supabase
        response = supabase.table("staff").insert(staff_data).execute()

        if response.data:
            print(f"✅ Success! {full_name} ({role}) created.")
        else:
            print("❌ Failed to create user. Check if the email already exists.")

    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    print("--- Church Attendance Staff Creator ---")

    """ new_email = "admin.000@gmail.com"
    new_password = "Temp@1234"
    new_name = "Shalom"
    new_role = "admin"  # Options: 'admin' or 'usher' """

    new_email = "usher.001@gmail.com"
    new_password = "Temp@1234"
    new_name = "Mr. Akwasi"
    new_role = "usher"  # Options: 'admin' or 'usher'

    create_staff_member(new_email, new_password, new_name, new_role)
