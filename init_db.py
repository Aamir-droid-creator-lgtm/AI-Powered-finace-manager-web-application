import sqlite3

conn = sqlite3.connect('expense_tracker.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS recurring_expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    amount REAL NOT NULL,
    description TEXT,
    frequency TEXT NOT NULL
)
''')

conn.commit()
conn.close()

print("Table 'recurring_expenses' created.")
