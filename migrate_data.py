import csv
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Initialize Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)


def migrate_members(file_path):
    print(f"🚀 Starting migration from {file_path}...")

    count = 0
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for row in reader:
            # Map your CSV column names to the Supabase column names
            # Adjust the keys (e.g., row['Full Name']) to match your CSV headers exactly
            member_data = {
                "full_name": row['Full Name'].strip(),
                "phone_number": row['Phone Number'].strip(),
                "membership_type": row.get('Type', 'Member').strip()
            }

            try:
                response = supabase.table(
                    "members").insert(member_data).execute()
                print(f"✅ Added: {member_data['full_name']}")
                count += 1
            except Exception as e:
                # This will catch duplicates based on the 'unique' phone_number constraint
                print(f"⚠️ Skipped {member_data['full_name']}: {str(e)}")

    print(f"\n✨ Migration complete! Total members added: {count}")


if __name__ == "__main__":
    # Ensure your CSV file is named 'members_export.csv' or change the name below
    csv_file = "data_export_1.csv"

    if os.path.exists(csv_file):
        migrate_members(csv_file)
    else:
        print(
            f"❌ Error: {csv_file} not found. Please export your Google Sheet as a CSV.")
