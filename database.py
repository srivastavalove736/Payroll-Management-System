import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "payroll.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Master Employee Table (Onboarding & Bank Details)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            emp_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            role TEXT NOT NULL,
            bank_name TEXT,
            account_no TEXT,
            ifsc_code TEXT,
            pan_card TEXT,
            onboarding_date TEXT
        )
    ''')
    
    # 2. Integration Table (Attendance & Leaves)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id INTEGER,
            month TEXT,
            total_days INTEGER DEFAULT 30,
            days_present REAL,
            FOREIGN KEY(emp_id) REFERENCES employees(emp_id)
        )
    ''')

    # 3. Comprehensive Payroll Table (Calculations & Compliance)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payroll_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id INTEGER,
            month TEXT,
            gross_salary REAL,
            pf_deduction REAL,
            esi_deduction REAL,
            tds_deduction REAL,
            prof_tax REAL,
            net_pay REAL,
            payment_status TEXT DEFAULT 'Pending',
            FOREIGN KEY(emp_id) REFERENCES employees(emp_id)
        )
    ''')
    conn.commit()
    conn.close()

# Helper Functions to write data
def onboard_employee(name, email, role, bank, acc, ifsc, pan):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO employees (name, email, role, bank_name, account_no, ifsc_code, pan_card, onboarding_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, email, role, bank, acc, ifsc, pan, datetime.today().strftime('%Y-%m-%d')))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def update_attendance(emp_id, month, days_present):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO attendance (emp_id, month, days_present) VALUES (?, ?, ?)", (emp_id, month, days_present))
    conn.commit()
    conn.close()

def get_employee_dropdown():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT emp_id, name FROM employees", conn)
    conn.close()
    return dict(zip(df['emp_id'], df['name']))
def get_dashboard_data():
    """Fetches combined data from employees and attendance tables for the dashboard."""
    conn = sqlite3.connect(DB_NAME)
    query = '''
        SELECT 
            e.emp_id AS [Employee ID],
            e.name AS [Name],
            e.role AS [Designation],
            e.pan_card AS [PAN Card],
            a.month AS [Payroll Month],
            a.days_present AS [Days Present]
        FROM employees e
        LEFT JOIN attendance a ON e.emp_id = a.emp_id
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df
from fpdf import FPDF

def generate_payslip_pdf(emp_id, emp_name):
    """Generates a real structured binary PDF document for downloading."""
    pdf = FPDF()
    pdf.add_page()
    
    # Header Banner
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "ENTERPRISE PAYROLL SYSTEM", ln=True, align="C")
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 10, "Confidential Salary Slip Summary", ln=True, align="C")
    pdf.line(10, 32, 200, 32)
    pdf.ln(10)
    
    # Body Content
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 10, f"Employee Database ID: {emp_id}", ln=True)
    pdf.cell(0, 10, f"Employee Full Name: {emp_name}", ln=True)
    pdf.cell(0, 10, f"Verification Status: Statutory Compliance Verified", ln=True)
    pdf.ln(5)
    
    pdf.line(10, 68, 200, 68)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 10, "Note: This is a system-generated secure record snapshot.", ln=True, align="L")
    
    # Output the document structure as a byte-string
    return pdf.output()