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

# Optional: Add demo users (remove this block if not needed)
demo_users = [
    ("lavraj", "password123", "secret123"),
    ("testuser", "testpass", "folderpass")
]

cursor.executemany("INSERT INTO data VALUES (?, ?, ?)", demo_users)

conn.commit()
conn.close()

print("✅ base.db created and filled with demo users.")
