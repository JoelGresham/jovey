#!/usr/bin/env python3
"""
Script to run the events schema in Supabase database.
This creates the event sourcing foundation tables and functions.
"""
import os
import sys
from pathlib import Path
from supabase import create_client

# Add parent directory to path to import from app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings


def run_events_schema():
    """Execute the events_schema.sql file in Supabase."""

    # Read the SQL file
    sql_file = Path(__file__).parent / "events_schema.sql"

    if not sql_file.exists():
        print(f"❌ Error: {sql_file} not found")
        return False

    with open(sql_file, 'r') as f:
        sql_content = f.read()

    print("📋 Read events_schema.sql successfully")
    print(f"📏 SQL file size: {len(sql_content)} characters")

    # Create Supabase client with service role key
    print(f"🔗 Connecting to Supabase: {settings.supabase_url}")

    supabase = create_client(
        settings.supabase_url,
        settings.supabase_service_key
    )

    try:
        # Execute the SQL
        print("⚙️  Executing SQL schema...")

        # Supabase Python client doesn't have direct SQL execution
        # We need to use the REST API
        import requests

        # Use Supabase REST API to execute SQL
        response = requests.post(
            f"{settings.supabase_url}/rest/v1/rpc/exec_sql",
            headers={
                "apikey": settings.supabase_service_key,
                "Authorization": f"Bearer {settings.supabase_service_key}",
                "Content-Type": "application/json"
            },
            json={"sql": sql_content}
        )

        if response.status_code == 200:
            print("✅ Events schema created successfully!")
            return True
        else:
            # If direct SQL execution isn't available, we'll need to use Supabase Dashboard
            print("⚠️  Direct SQL execution not available via REST API")
            print("📝 Please execute the SQL manually:")
            print("   1. Go to Supabase Dashboard")
            print("   2. Navigate to SQL Editor")
            print(f"   3. Copy and paste the contents of: {sql_file}")
            print("   4. Execute the SQL")
            return False

    except Exception as e:
        print(f"⚠️  Note: {e}")
        print("\n📝 Manual execution required:")
        print("   1. Go to Supabase Dashboard: https://supabase.com/dashboard")
        print(f"   2. Select your project (ID: {settings.supabase_url.split('//')[1].split('.')[0]})")
        print("   3. Navigate to: SQL Editor")
        print(f"   4. Open: {sql_file}")
        print("   5. Copy and paste the entire SQL content")
        print("   6. Click 'Run' to execute")
        print("\n✅ The SQL file is ready at: backend/database/events_schema.sql")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Event Sourcing Schema Setup")
    print("=" * 60)
    print()

    success = run_events_schema()

    print()
    print("=" * 60)

    if not success:
        print("⏸️  Waiting for manual SQL execution in Supabase Dashboard")
        print("=" * 60)
        sys.exit(1)
    else:
        print("✅ Setup complete!")
        print("=" * 60)
        sys.exit(0)
