import sqlite3

db_path = "./results/affiliate_program.db"

with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM affiliates;")
    rows = cursor.fetchall()
    
    # Print column headers
    col_names = [description[0] for description in cursor.description]
    print("\t".join(col_names))
    
    # Print all rows
    for row in rows:
        print("\t".join(str(item) for item in row))
