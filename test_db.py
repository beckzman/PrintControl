import sqlite3
conn = sqlite3.connect('backend/data/printers.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(printers)")
columns = cursor.fetchall()
for col in columns:
    print(col)
