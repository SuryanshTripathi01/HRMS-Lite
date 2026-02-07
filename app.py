from functools import wraps
import email
import os
from flask import Flask, render_template, request, redirect, flash,session
import sqlite3



app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "secret123")   # use env var in production

def init_database():
    """Initialize database with tables and default users"""
    db = sqlite3.connect("database.db")
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
        
        print("✅ Database initialized with default users")
    except sqlite3.IntegrityError:
        print("✅ Database already initialized")
    
    db.commit()
    db.close()

# Initialize database on app startup
with app.app_context():
    init_database()
def get_db():
    return sqlite3.connect("database.db")

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("role") != "ADMIN":
            flash("Admin access required", "error")
            return redirect("/employees")
        return f(*args, **kwargs)
    return decorated

@app.route("/add", methods=["GET", "POST"])
@login_required
def add_employee():
    if request.method == "POST":
        employee_id = request.form["employee_id"]
        name = request.form["name"]
        email = request.form["email"]
        dept = request.form["dept"]
        role = request.form["role"]
        print(employee_id, email)
        try:
            db = get_db()
            db.execute("""
                INSERT INTO employee (employee_id, name, email, dept, role)
                VALUES (?, ?, ?, ?, ?)
            """, (employee_id, name, email, dept, role))
            db.commit()
            db.close()

            flash("Employee added successfully", "success")
            return redirect("/employees")

        except sqlite3.IntegrityError as e:
            flash("Employee ID or Email already exists!", "error")
            return redirect("/add")
        

    return render_template("add_employee.html")


@app.route("/employees")
@login_required
def employees():
    db = get_db()
    data = db.execute("SELECT * FROM employee").fetchall()
    db.close()
    return render_template("employees.html", data=data)

@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_employee(id):
    db = get_db()

    if request.method == "POST":
        name = request.form["name"]
        role = request.form["role"]
        email= request.form["email"]
        dept= request.form["dept"]

        db.execute(
            "UPDATE employee SET name=?, email=?, dept=?, role=? WHERE id=?",
            (name, email, dept, role, id) 
        )
        db.commit()
        db.close()
        return redirect("/employees")

    employee = db.execute(
        "SELECT * FROM employee WHERE id=?",
        (id,)
    ).fetchone()
    db.close()

    return render_template("edit_employee.html", employee=employee)

@app.route("/delete/<int:id>")
@login_required
@admin_required
def delete_employee(id):
    db = get_db()
    db.execute("DELETE FROM employee WHERE id=?", (id,))
    db.commit()
    db.close()
    return redirect("/employees")

@app.route("/attendance/<int:emp_id>", methods=["GET", "POST"])
@login_required
def attendance(emp_id):
    if request.method == "POST":
        date = request.form["date"]
        status = request.form["status"]

        db = get_db()
        db.execute("""
            INSERT INTO attendance (employee_id, date, status)
            VALUES (?, ?, ?)
        """, (emp_id, date, status))
        db.commit()
        db.close()

        return redirect("/employees")

    return render_template("attendance.html")

@app.route("/attendance/view/<int:emp_id>")
def view_attendance(emp_id):
    db = get_db()
    records = db.execute("""
        SELECT date, status
        FROM attendance
        WHERE employee_id=?
        ORDER BY date DESC
    """, (emp_id,)).fetchall()
    db.close()

    return render_template(
        "attendance_view.html",
        attendance=records
    )

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()
        db.close()

        if user:
            session["user_id"] = user[0]
            session["username"] = user[1]
            session["role"] = user[3]
            return redirect("/employees")
        else:
            flash("Invalid credentials", "error")

    return render_template("index.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__=='__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

