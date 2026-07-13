import sqlite3
import pandas as pd

DB_NAME = "payroll.db"

def init_db():
    """Initializes the database and creates the payroll table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payroll (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            base_salary REAL NOT NULL,
            allowances REAL DEFAULT 0,
            deductions REAL DEFAULT 0,
            net_salary REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_employee(name, role, base_salary, allowances, deductions):
    """Calculates net salary and inserts a new employee record."""
    net_salary = base_salary + allowances - deductions
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO payroll (name, role, base_salary, allowances, deductions, net_salary)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, role, base_salary, allowances, deductions, net_salary))
    conn.commit()
    conn.close()

def get_all_employees():
    """Fetches all employee data into a Pandas DataFrame for easy display."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM payroll", conn)
    conn.close()
    return df

def delete_employee(emp_id):
    """Deletes an employee record by ID."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM payroll WHERE id = ?", (emp_id,))
    conn.commit()
    conn.close()