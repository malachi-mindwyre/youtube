import sqlite3

db_path = r"C:\Users\Tannest\Desktop\workie\youtube\results\affiliate_program.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create the table if not exists
cursor.execute('''
CREATE TABLE IF NOT EXISTS affiliates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    referral_id TEXT UNIQUE NOT NULL
)
''')

# Query all records
cursor.execute('SELECT * FROM affiliates')
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
