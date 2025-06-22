import sqlite3

# Connect to the database (creates it if it doesn't exist)
conn = sqlite3.connect('expense_tracker.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    date TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS income (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    amount REAL NOT NULL,
    date TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS goals (
    username TEXT PRIMARY KEY,
    goal REAL NOT NULL
)
''')

conn.commit()
conn.close()

print("✅ All tables created successfully.")
