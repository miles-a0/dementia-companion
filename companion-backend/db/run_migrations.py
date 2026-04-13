import os
import sys
from pathlib import Path

import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")
MIGRATIONS_DIR = Path(__file__).parent / "migrations"

MIGRATION_FILES = [
    "001_messages.sql",
    "002_biometrics.sql",
    "003_medication.sql",
    "004_conversations.sql",
]

def main():
    if not DATABASE_URL:
        print("Error: DATABASE_URL environment variable not set")
        sys.exit(1)
    
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    
    try:
        for filename in MIGRATION_FILES:
            filepath = MIGRATIONS_DIR / filename
            print(f"Running migration: {filename}")
            
            with open(filepath, "r") as f:
                sql_content = f.read()
            
            cursor = conn.cursor()
            cursor.execute(sql_content)
            cursor.close()
            print(f"  Completed: {filename}")
        
        conn.commit()
        print("All migrations completed successfully.")
        
    except Exception as e:
        conn.rollback()
        print(f"Error running migrations: {e}")
        print("Rolled back all changes.")
        sys.exit(1)
    
    finally:
        conn.close()

if __name__ == "__main__":
    main()