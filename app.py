import streamlit as st
import database as db

# Initialize the database table on startup
db.init_db()

st.set_page_config(page_title="Payroll Management System", layout="wide")
st.title("💼 AI-Ready Payroll Management System")
st.markdown("---")

# Sidebar navigation
menu = ["📊 Dashboard & View", "➕ Add Employee", "❌ Remove Employee"]
choice = st.sidebar.selectbox("Navigation Menu", menu)

# --- TAB 1: DASHBOARD & VIEW ---
if choice == "📊 Dashboard & View":
    st.subheader("Employee Payroll Records")
    df = db.get_all_employees()
    
    if df.empty:
        st.info("No employee records found. Use the sidebar to add a new employee.")
    else:
        # Display Key Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Employees", len(df))
        col2.metric("Total Monthly Payout", f"₹{df['net_salary'].sum():,.2f}")
        col3.metric("Average Net Salary", f"₹{df['net_salary'].mean():,.2f}")
        
        st.markdown("### Detailed Data Table")
        st.dataframe(df, use_container_width=True)

# --- TAB 2: ADD EMPLOYEE ---
elif choice == "➕ Add Employee":
    st.subheader("Register a New Employee")
    
    with st.form("employee_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name")
            role = st.text_input("Job Role/Designation")
            base_salary = st.number_input("Base Salary (₹)", min_value=0.0, step=1000.0)
            
        with col2:
            allowances = st.number_input("Allowances (HRA, TA, etc.) (₹)", min_value=0.0, step=500.0)
            deductions = st.number_input("Deductions (PF, Tax, etc.) (₹)", min_value=0.0, step=500.0)
        
        submit_button = st.form_submit_button("Calculate & Save Record")
        
        if submit_button:
            if name.strip() == "" or role.strip() == "":
                st.error("Please fill out both Name and Role fields.")
            else:
                db.add_employee(name, role, base_salary, allowances, deductions)
                st.success(f"Successfully added {name} to the payroll database!")

# --- TAB 3: REMOVE EMPLOYEE ---
elif choice == "❌ Remove Employee":
    st.subheader("Remove Employee Record")
    df = db.get_all_employees()
    
    if df.empty:
        st.info("No records available to delete.")
    else:
        # Create a dropdown mapping "ID: Name" for easy deletion Selection
        employee_options = {row['id']: f"ID {row['id']} - {row['name']} ({row['role']})" for _, row in df.iterrows()}
        selected_id = st.selectbox("Select Employee to Remove", options=list(employee_options.keys()), format_func=lambda x: employee_options[x])
        
        if st.button("Delete Record", type="primary"):
            db.delete_employee(selected_id)
            st.success("Record deleted successfully!")
            st.rerun()