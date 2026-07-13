import streamlit as st
import pandas as pd
import database as db

db.init_db()

st.set_page_config(page_title="Advanced HR & Payroll Suite", layout="wide")
st.title("🏛️ Enterprise Payroll & HR Management System")
st.markdown("---")

# Navigation Menu matching your requirements
menu = [
    "👾 0. Dashboard & View",
    "👤 1. Employee Onboarding", 
    "🔌 2. HR & Attendance Integration", 
    "🧮 3. Payroll & Statutory Compliance", 
    "🏦 4. Salary Disbursement & ESS"
]
choice = st.sidebar.selectbox("Modules", menu)
# ==========================================
# MODULE 0: DASHBOARD & VIEW (FRONT TAB)
# ==========================================
if "Dashboard & View" in choice:
    st.subheader("📊 Central HR & Operations Hub")
    
    # 1. Pull the newly seeded data framework
    df_dashboard = db.get_dashboard_data()
    
    if df_dashboard.empty:
        st.info("💡 The database ledger is currently empty. Run seed_data.py or onboard employees to populate records.")
    else:
        # Create sub-tabs to view analytics and the raw logs side-by-side cleanly
        tab_analytics, tab_database = st.tabs(["📈 Operational Analytics", "📋 View Master Records"])
        
        with tab_analytics:
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="Active Onboarded Staff", value=int(df_dashboard["Employee ID"].nunique()))
            with col2:
                # Fill missing attendance data with 0 temporarily for metric calculation safely
                avg_attendance = df_dashboard["Days Present"].fillna(0).mean()
                st.metric(label="Average Team Attendance", value=f"{avg_attendance:.2f} / 30")
            
            st.markdown("### Team Attendance Breakdown")
            # Create a bar chart tracking days present against employee names
            chart_data = df_dashboard.dropna(subset=["Days Present"]).set_index("Name")[["Days Present"]]
            if not chart_data.empty:
                st.bar_chart(chart_data)
            else:
                st.caption("No attendance logs found to plot yet.")
                
        with tab_database:
            st.markdown("### Master Ledger Logs")
            # Render the structural dataframe directly onto the page
            st.dataframe(df_dashboard, use_container_width=True, hide_index=True)

# ==========================================
# MODULE 1: EMPLOYEE ONBOARDING & VALIDATION
# ==========================================
if choice == "👤 1. Employee Onboarding":
    st.subheader("New Employee Registration & Document Validation")
    
    with st.form("onboarding_form"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Personal Details")
            name = st.text_input("Full Name")
            email = st.text_input("Official Email ID")
            role = st.text_input("Designation")
            pan = st.text_input("PAN Card Number (10 Digits)")
        with col2:
            st.markdown("### Statutory Bank Account Verification")
            bank = st.text_input("Bank Name")
            acc = st.text_input("Account Number")
            ifsc = st.text_input("IFSC Code")
            
        submitted = st.form_submit_button("Validate & Onboard Employee")
        if submitted:
            # Simple UI Validations
            if len(pan) != 10:
                st.error("Invalid PAN format! Must be 10 characters.")
            elif not name or not email:
                st.error("Name and Email are mandatory fields.")
            else:
                success = db.onboard_employee(name, email, role, bank, acc, ifsc, pan)
                if success:
                    st.success(f"🎉 System Onboarded: {name}. Profiles synced with database.")
                else:
                    st.error("Email already registered!")

# ==========================================
# MODULE 2: INTEGRATION WITH HR SYSTEMS
# ==========================================
elif choice == "🔌 2. HR & Attendance Integration":
    st.subheader("Sync Attendance Data from HR Systems")
    emp_map = db.get_employee_dropdown()
    
    if not emp_map:
        st.info("No employees found. Complete onboarding first.")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_emp = st.selectbox("Select Employee", options=list(emp_map.keys()), format_func=lambda x: emp_map[x])
        with col2:
            month = st.selectbox("Payroll Month", ["July 2026", "August 2026", "September 2026"])
        with col3:
            days_present = st.number_input("Days Present (Max 30)", min_value=0.0, max_value=30.0, value=30.0, step=0.5)
            
        if st.button("Sync Attendance to Ledger"):
            db.update_attendance(selected_emp, month, days_present)
            st.success(f"Linked {days_present} active days for calculation.")

# ==========================================
# MODULE 3: PAYROLL CALCULATION & COMPLIANCE
# ==========================================
elif choice == "🧮 3. Payroll & Statutory Compliance":
    st.subheader("Automated Statutory Deductions Engine")
    
    # Fetch base variables
    base_ctc = st.number_input("Enter Standard Base CTC for processing (Monthly Component)", min_value=10000.0, value=50000.0)
    
    st.markdown("### Standard Rules Engine (Indian Labor Laws Structure)")
    
    # Formulas implementation
    pf = base_ctc * 0.12     # Employee PF contribution (12%)
    esi = base_ctc * 0.0075  # ESI contribution (0.75%)
    prof_tax = 200.00        # Standard professional tax slab
    tds = base_ctc * 0.10    # Projected tax deduction slab (10%)
    net_pay = base_ctc - (pf + esi + prof_tax + tds)
    
    # Display the breakdown variables clearly using containers
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Gross Monthly Pay:** ₹{base_ctc:,.2f}")
        st.error(f"**Provident Fund (PF - 12%):** ₹{pf:,.2f}")
        st.error(f"**Employee State Insurance (ESI - 0.75%):** ₹{esi:,.2f}")
    with col2:
        st.error(f"**Professional Tax (PT):** ₹{prof_tax:,.2f}")
        st.error(f"**TDS/Income Tax Slab:** ₹{tds:,.2f}")
        st.success(f"**Take Home Net Pay:** ₹{net_pay:,.2f}")

    st.warning("⚠️ **Compliance Checklist:** Submitting updates compiles PF Form-5 & ESI monthly statutory contributions automatically for legal audits.")

# ==========================================
# MODULE 4: SALARY DISBURSEMENT & ESS (SELF SERVICE)
# ==========================================
elif choice == "🏦 4. Salary Disbursement & ESS":
    st.subheader("Salary Bank Vault Transfer & Employee Self-Service Panel")
    
    tab1, tab2 = st.tabs(["🏛️ Admin Disbursement Vault", "🔐 Employee Self-Service Dashboard"])
    
    with tab1:
        st.markdown("### Process Bulk Payouts")
        st.caption("Integrated Node simulator for RazorpayX / Bank APIs")
        st.button("⚡ Dispatch Funds via Direct Bank Transfer IMPS/NEFT")
        
    with tab2:
        st.markdown("### Secure Employee Pay Slip Engine")
        emp_map = db.get_employee_dropdown()
        
        if emp_map:
            user_view = st.selectbox("Identify Profile", options=list(emp_map.keys()), format_func=lambda x: emp_map[x])
            
            # Fetch backend profile info and its matching predefined salary breakdown
            emp_info = db.get_employee_full_details(user_view)
            sal_breakdown = db.get_salary_structure(emp_info["role"])
            
            # Show live preview metrics directly inside the Streamlit UI
            st.markdown(f"#### 📄 Live Statement Preview for **{emp_info['name']}**")
            
            preview_col1, preview_col2 = st.columns(2)
            with preview_col1:
                st.info(f"**Predefined Gross Salary:** ₹{sal_breakdown['base']:,.2f}")
                st.caption(f"Assigned Tier Profile based on designation: *{emp_info['role']}*")
            with preview_col2:
                st.success(f"**Computed Net Payout:** ₹{sal_breakdown['net_pay']:,.2f}")
                st.caption("All mandatory EPF, ESI, PT, and TDS metrics successfully applied.")
            
            # Compile the clean detailed PDF structure
            pdf_bytes = db.generate_detailed_payslip_pdf(user_view)
            
            # Download trigger
            st.download_button(
                label="📥 Download Detailed Payslip PDF",
                data=bytes(pdf_bytes),
                file_name=f"Detailed_Payslip_ID_{user_view}.pdf",
                mime="application/pdf"
            )