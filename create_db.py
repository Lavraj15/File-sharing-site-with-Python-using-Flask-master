import sqlite3

# Create a new SQLite database
conn = sqlite3.connect("base.db")
cursor = conn.cursor()

# Create the required table
cursor.execute("""
CREATE TABLE IF NOT EXISTS data (
    username TEXT,
    password TEXT,
    folder_password TEXT
)
""")

conn.commit()
conn.close()

print("✅ base.db created (empty, no demo users).")
