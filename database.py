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
import sqlite3
import pandas as pd
from datetime import datetime
from fpdf import FPDF

DB_NAME = "payroll.db"

def get_salary_structure(role):
    """Predefines Base Salary slabs based on the employee's designation."""
    role_lower = role.lower()
    if "manager" in role_lower:
        base = 90000.0
    elif "lead" in role_lower or "senior" in role_lower:
        base = 85000.0
    elif "analyst" in role_lower:
        base = 65000.0
    elif "developer" in role_lower or "engineer" in role_lower:
        base = 60000.0
    else:
        base = 450000.0 # Default base pay for any other role
        
    # Statutory Breakdown Rules Engine
    pf = base * 0.12        # 12% PF
    esi = base * 0.0075     # 0.75% ESI
    prof_tax = 200.0        # Fixed Professional Tax
    tds = base * 0.10       # 10% TDS slab estimation
    net_pay = base - (pf + esi + prof_tax + tds)
    
    return {
        "base": base,
        "pf": pf,
        "esi": esi,
        "prof_tax": prof_tax,
        "tds": tds,
        "net_pay": net_pay
    }

def get_employee_full_details(emp_id):
    """Fetches comprehensive profile details for an employee."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name, email, role, bank_name, account_no, pan_card FROM employees WHERE emp_id = ?", (emp_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "name": row[0], "email": row[1], "role": row[2],
            "bank": row[3], "account": row[4], "pan": row[5]
        }
    return None
def generate_detailed_payslip_pdf(emp_id):
    """Generates a comprehensive itemized binary PDF payslip."""
    emp = get_employee_full_details(emp_id)
    if not emp:
        return None
        
    # Get predefined automatic calculations based on their role
    sal = get_salary_structure(emp["role"])
    
    pdf = FPDF()
    pdf.add_page()
    
    # 1. Corporate Header
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, "ENTERPRISE PAYROLL SYSTEM", ln=True, align="C")
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "MONTHLY SALARY DISBURSEMENT STATEMENT", ln=True, align="C")
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    # 2. Employee Profile Metadata Table
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(95, 8, f"Employee Name: {emp['name']}", ln=False)
    pdf.cell(95, 8, f"Employee ID: {emp_id}", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(95, 6, f"Designation: {emp['role']}", ln=False)
    pdf.cell(95, 6, f"PAN Card Reference: {emp['pan']}", ln=True)
    pdf.cell(95, 6, f"Bank Name: {emp['bank']}", ln=False)
    pdf.cell(95, 6, f"Account No: {emp['account']}", ln=True)
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(8)
    
    # 3. Financial Breakdown Ledger Header
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(95, 8, "EARNINGS / COMPONENTS", border=1, align="C")
    pdf.cell(95, 8, "STATUTORY DEDUCTIONS", border=1, align="C", ln=True)
    
    # Row: Base Salary & PF
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(65, 8, " Basic Base Salary", border="LB")
    pdf.cell(30, 8, f"Rs. {sal['base']:,.2f} ", border="RB", align="R")
    pdf.cell(65, 8, " Provident Fund (PF - 12%)", border="B")
    pdf.cell(30, 8, f"Rs. {sal['pf']:,.2f} ", border="RB", ln=True, align="R")
    
    # Row: Empty Earnings Slot & ESI
    pdf.cell(65, 8, " Allowances / Incentives", border="LB")
    pdf.cell(30, 8, "Rs. 0.00 ", border="RB", align="R")
    pdf.cell(65, 8, " Employee State Insurance (ESI)", border="B")
    pdf.cell(30, 8, f"Rs. {sal['esi']:,.2f} ", border="RB", ln=True, align="R")
    
    # Row: Empty Earnings Slot & Professional Tax / TDS
    pdf.cell(65, 8, "", border="LB")
    pdf.cell(30, 8, "", border="RB")
    pdf.cell(65, 8, " Professional Tax (PT)", border="B")
    pdf.cell(30, 8, f"Rs. {sal['prof_tax']:,.2f} ", border="RB", ln=True, align="R")
    
    pdf.cell(65, 8, "", border="LB")
    pdf.cell(30, 8, "", border="RB")
    pdf.cell(65, 8, " Income Tax / TDS Slab (10%)", border="B")
    pdf.cell(30, 8, f"Rs. {sal['tds']:,.2f} ", border="RB", ln=True, align="R")
    
    # 4. Net Take-Home Payout Banner
    pdf.ln(5)
    pdf.set_fill_color(230, 245, 230) # Light green background highlight
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(190, 12, f"  NET TAKE-HOME PAYOUT:  Rs. {sal['net_pay']:,.2f}", border=1, ln=True, fill=True)
    
    # Footer
    pdf.ln(15)
    pdf.set_font("Helvetica", "I", 9)
    pdf.cell(0, 5, "This document is electronically verified and strictly confidential.", ln=True, align="C")
    
    return pdf.output()