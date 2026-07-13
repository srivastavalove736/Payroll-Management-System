import sqlite3

def inject_dummy_data():
    conn = sqlite3.connect("payroll.db")
    cursor = conn.cursor()
    
    # 1. Clear existing rows to avoid duplicates
    cursor.execute("DELETE FROM employees")
    cursor.execute("DELETE FROM attendance")
    cursor.execute("DELETE FROM payroll_records")

    # 2. Insert Core Team as Employees (Onboarding Data)
    team_members = [
        ("Utkarsh Srivastava", "utkarsh@company.com", "Project Manager", "HDFC Bank", "10023456789", "HDFC0000123", "ABCDE1234F"),
        ("Love Srivastava", "love@company.com", "Lead AI Engineer", "ICICI Bank", "20098765432", "ICIC0000456", "FGHIJ5678K"),
        ("Mayank Gupta", "mayank@company.com", "Data Analyst", "SBI Bank", "30045612378", "SBIN0000789", "KLMNO9012L"),
        ("Hanee Mishra", "hanee@company.com", "HR Compliance Specialist", "Axis Bank", "40078945612", "UTIB0000321", "PQRST3456M"),
        ("Gyanendra", "gyanendra@company.com", "Full Stack Developer", "PNB Bank", "50032165498", "PUNB0000654", "UVWXY7890N"),
        ("Mohit Gupta", "mohit@company.com", "HR Compliance Specialist", "Axis Bank", "40078945641", "UTIB0000521", "PQRHT3456M"),
        ("Sujal Mishra", "sujal@company.com", "HR Compliance Specialist", "LenaDena Bank", "40568945612", "UTHX0000321", "PQRST3498M")
    ]
    
    cursor.executemany('''
        INSERT INTO employees (name, email, role, bank_name, account_no, ifsc_code, pan_card, onboarding_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, '2026-07-01')
    ''', team_members)
    
    # 3. Insert Sync HR Data (Attendance Integration for July 2026)
    attendance_data = [
        (1, "July 2026", 30.0), # Utkarsh - Full attendance
        (2, "July 2026", 29.5), # Love
        (3, "July 2026", 28.0), # Mayank
        (4, "July 2026", 30.0), # Hanee
        (5, "July 2026", 26.5),  # Gyanendra
        (6, "July 2026", 25.5),  # Mohit
        (7, "July 2026", 24.5)  # Sujal
    ]
    cursor.executemany("INSERT INTO attendance (emp_id, month, days_present) VALUES (?, ?, ?)", attendance_data)

    conn.commit()
    conn.close()
    print("🚀 Project database successfully seeded with custom team data!")

if __name__ == "__main__":
    inject_dummy_data()