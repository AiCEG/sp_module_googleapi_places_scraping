import sqlite3
import csv

# Connect to the SQLite database
conn = sqlite3.connect('googleplacesdb.db')
cur = conn.cursor()

# Create table
cur.execute('''
    CREATE TABLE IF NOT EXISTS places (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        api_keyword TEXT,
        business_status TEXT,
        place_id TEXT,
        lat REAL,
        lng REAL,
        rating REAL,
        user_ratings_total INTEGER,
        types TEXT,
        vicinity TEXT,
        price_level INTEGER
    )
''')

# Open the CSV file
f = open('export_places.csv', 'r', encoding='utf-8')
reader = csv.reader(f)

# Skip the header row
next(reader)

# For each row in the CSV file...
for row in reader:
    # Insert the row into the SQLite table
    cur.execute('''
        INSERT INTO places (name, api_keyword, business_status, place_id, lat, lng, rating, user_ratings_total, types, vicinity, price_level)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    ''', row[1:])  # Leave out the first element of the row, which is the id

# Commit the changes
conn.commit()

# Close the file and the connection
f.close()
conn.close()
