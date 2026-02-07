import sqlite3

db = sqlite3.connect('database.db')
cursor = db.cursor()

# Check tables
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print("Tables:", [t[0] for t in tables])

# Check users
cursor.execute('SELECT username, role FROM users')
users = cursor.fetchall()
print("Users:", users)

db.close()
print("✅ Database verification complete!")
