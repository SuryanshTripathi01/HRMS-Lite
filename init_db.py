import sqlite3
import os

def init_db():
    """Initialize the database with required tables and default users"""
    db_path = "database.db"
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('ADMIN', 'HR'))
        )
    """)
    
    # Create employee table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employee (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            dept TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)
    
    # Create attendance table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('Present', 'Absent', 'Leave')),
            FOREIGN KEY (employee_id) REFERENCES employee(id)
        )
    """)
    
    # Insert default users if they don't exist
    try:
        cursor.execute("""
            INSERT INTO users (username, password, role)
            VALUES (?, ?, ?)
        """, ("Ethara", "Ethara123", "ADMIN"))
        
        cursor.execute("""
            INSERT INTO users (username, password, role)
            VALUES (?, ?, ?)
        """, ("Prince", "Prince123", "HR"))
        
        print("✅ Database initialized successfully!")
        print("Default users created:")
        print("  Admin: Ethara / Ethara123")
        print("  HR: Prince / Prince123")
    except sqlite3.IntegrityError:
        print("✅ Database already initialized (users already exist)")
    
    db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
