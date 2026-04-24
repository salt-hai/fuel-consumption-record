#!/usr/bin/env python3
"""Add icon column to vehicles table"""

import sqlite3

# Connect to database
db_path = "fuel.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if column exists
    cursor.execute("PRAGMA table_info(vehicles)")
    columns = [col[1] for col in cursor.fetchall()]

    if 'icon' not in columns:
        # Add icon column
        cursor.execute("ALTER TABLE vehicles ADD COLUMN icon VARCHAR DEFAULT '🚗'")
        print("OK: Added icon column")

        # Set default icon for existing records
        cursor.execute("UPDATE vehicles SET icon = '🚗' WHERE icon IS NULL")
        print("OK: Set default icon for existing records")
    else:
        print("OK: icon column already exists")

    # Verify
    cursor.execute("SELECT id, name, icon FROM vehicles")
    rows = cursor.fetchall()
    print(f"\nCurrent vehicles:")
    for row in rows:
        print(f"  ID: {row[0]}, Name: {row[1]}, Icon: {row[2]}")

    conn.commit()
    print("\nOK: Database updated successfully!")

except Exception as e:
    print(f"ERROR: {e}")
    conn.rollback()
finally:
    conn.close()
