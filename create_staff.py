import os
from dotenv import load_dotenv
from supabase import create_client, Client
from werkzeug.security import generate_password_hash

# Load environment variables from .env
load_dotenv()

# Initialize Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
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

    new_email1 = "admin.000@gmail.com"
    new_password1 = "chiefSt3w@rd!CCC26"
    new_name1 = "Administrator"
    new_role1 = "admin"

    new_email2 = "usher.001@gmail.com"
    new_password2 = "1St3w@rd!CCC26"
    new_name2 = "Usher One"
    new_role2 = "usher"

    new_email3 = "usher.002@gmail.com"
    new_password3 = "2St3w@rd!CCC26"
    new_name3 = "Usher Two"
    new_role3 = "usher"

    new_email4 = "usher.003@gmail.com"
    new_password4 = "3St3w@rd!CCC26"
    new_name4 = "Usher Three"
    new_role4 = "usher"

    create_staff_member(new_email1, new_password1, new_name1, new_role1)
    create_staff_member(new_email2, new_password2, new_name2, new_role2)
    create_staff_member(new_email3, new_password3, new_name3, new_role3)
    create_staff_member(new_email4, new_password4, new_name4, new_role4)
