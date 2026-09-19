"""
Sales Module Page
Manage sales entries, view sales history, and filter sales data
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from db_connection import DatabaseConnection
from auth import AuthenticationManager
import sql_queries

def render_sales_form():
    """Render form to add new sale"""
    
    st.markdown("<h3 style='color: #1e293b;'>➕ Add New Sale</h3>", unsafe_allow_html=True)
    
    with st.form("add_sale_form", border=False):
        col1, col2 = st.columns(2)
        
        with col1:
            # Get current user's branch or allow selection if Super Admin
            user = AuthenticationManager.get_current_user()
            branches_df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_ALL_BRANCHES)
            
            if user['role'] == 'Super Admin' and branches_df is not None:
                branch_options = dict(zip(branches_df['branch_name'], branches_df['branch_id']))
                branch_name = st.selectbox("Branch", list(branch_options.keys()))
                branch_id = branch_options[branch_name]
            else:
                branch_id = user['branch_id']
                branch_name = DatabaseConnection.fetch_one(
                    "SELECT branch_name FROM branches WHERE branch_id = %s",
                    (branch_id,)
                )[0]
                st.write(f"**Branch:** {branch_name}")
            
            customer_name = st.text_input("Customer Name", placeholder="Enter customer name")
            customer_phone = st.text_input("Phone", placeholder="Enter phone number")
            customer_email = st.text_input("Email", placeholder="Enter email address")
        
        with col2:
            product_category = st.selectbox(
                "Product Category",
                ["Standard", "Professional Services", "Enterprise"]
            )
            product_description = st.text_area("Product Description", height=100)
        
        col3, col4 = st.columns(2)
        
        with col3:
            sale_amount = st.number_input("Sale Amount ($)", min_value=0.0, step=100.0)
            sale_date = st.date_input("Sale Date", value=date.today())
        
        with col4:
            notes = st.text_area("Additional Notes", height=100, placeholder="Optional notes...")
        
        col_submit, col_cancel = st.columns([1, 1])
        
        with col_submit:
            if st.form_submit_button("✓ Add Sale", use_container_width=True, type="primary"):
                if not customer_name:
                    st.error("Customer name is required")
                elif sale_amount <= 0:
                    st.error("Sale amount must be greater than 0")
                else:
                    try:
                        result = DatabaseConnection.execute_query(
                            sql_queries.QUERY_ADD_SALE,
                            (
                                branch_id,
                                customer_name,
                                customer_phone,
                                customer_email,
                                product_category,
                                product_description,
                                sale_amount,
                                sale_date,
                                "Open",
                                notes
                            )
                        )
                        
                        if result:
                            st.success("✓ Sale added successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to add sale")
                    except Exception as e:
                        st.error(f"Error: {e}")
        
        with col_cancel:
            if st.form_submit_button("✕ Clear", use_container_width=True):
                pass

def render_sales_filters_and_table():
    """Render sales view with filters"""
    
    st.markdown("<h3 style='color: #1e293b;'>📋 Sales Records</h3>", unsafe_allow_html=True)
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        user = AuthenticationManager.get_current_user()
        if user['role'] == 'Super Admin':
            branches_df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_ALL_BRANCHES)
            if branches_df is not None:
                branch_filter = st.selectbox(
                    "Filter by Branch",
                    ["All Branches"] + list(branches_df['branch_name']),
                    key="branch_filter"
                )
            else:
                branch_filter = "All Branches"
        else:
            branch_filter = "Current Branch"
    
    with col2:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "Open", "Partial", "Closed"],
            key="status_filter"
        )
    
    with col3:
        category_filter = st.selectbox(
            "Filter by Category",
            ["All", "Standard", "Professional Services", "Enterprise"],
            key="category_filter"
        )
    
    with col4:
        date_range = st.selectbox(
            "Date Range",
            ["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days"],
            key="date_range"
        )
    
    # Build query based on filters
    sales_df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_ALL_SALES_WITH_DETAILS)
    
    if sales_df is not None and not sales_df.empty:
        # Apply branch filter
        if user['role'] != 'Super Admin' or branch_filter != "All Branches":
            if branch_filter != "All Branches":
                sales_df = sales_df[sales_df['branch_name'] == branch_filter]
            else:
                sales_df = sales_df[sales_df['branch_name'] == user.get('branch_name', '')]
        
        # Apply status filter
        if status_filter != "All":
            sales_df = sales_df[sales_df['payment_status'] == status_filter]
        
        # Apply category filter
        if category_filter != "All":
            sales_df = sales_df[sales_df['product_category'] == category_filter]
        
        # Apply date filter
        from datetime import timedelta
        sales_df['sale_date'] = pd.to_datetime(sales_df['sale_date'])
        
        if date_range == "Last 7 Days":
            cutoff = datetime.now() - timedelta(days=7)
            sales_df = sales_df[sales_df['sale_date'] >= cutoff]
        elif date_range == "Last 30 Days":
            cutoff = datetime.now() - timedelta(days=30)
            sales_df = sales_df[sales_df['sale_date'] >= cutoff]
        elif date_range == "Last 90 Days":
            cutoff = datetime.now() - timedelta(days=90)
            sales_df = sales_df[sales_df['sale_date'] >= cutoff]
        
        # Format for display
        display_df = sales_df[[
            'sale_id', 'customer_name', 'branch_name', 'product_category',
            'sale_amount', 'received_amount', 'pending_amount', 'payment_status', 'sale_date'
        ]].copy()
        
        display_df.columns = ['ID', 'Customer', 'Branch', 'Category', 'Sale Amt', 'Received', 'Pending', 'Status', 'Date']
        display_df['Sale Amt'] = display_df['Sale Amt'].apply(lambda x: f"${x:,.2f}")
        display_df['Received'] = display_df['Received'].apply(lambda x: f"${x:,.2f}")
        display_df['Pending'] = display_df['Pending'].apply(lambda x: f"${x:,.2f}")
        display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Summary stats
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        
        with col_stat1:
            st.metric("Total Records", len(sales_df))
        
        with col_stat2:
            total_amount = sales_df['sale_amount'].sum()
            st.metric("Total Sales", f"${total_amount:,.2f}")
        
        with col_stat3:
            received = sales_df['received_amount'].sum()
            st.metric("Total Received", f"${received:,.2f}")
        
        with col_stat4:
            pending = sales_df['pending_amount'].sum()
            st.metric("Total Pending", f"${pending:,.2f}")
    else:
        st.info("No sales records found")

def main():
    """Main entry point for sales page"""
    AuthenticationManager.require_login()
    
    st.markdown("""
        <div style='padding: 20px 0; border-bottom: 1px solid #e2e8f0;'>
            <h1 style='color: #1e293b; margin: 0; font-size: 32px;'>💰 Sales Management</h1>
            <p style='color: #64748b; margin: 5px 0 0 0; font-size: 14px;'>
                Create sales entries and track collection status
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    
    tab1, tab2 = st.tabs(["Add New Sale", "View Sales"])
    
    with tab1:
        st.markdown("")
        render_sales_form()
    
    with tab2:
        st.markdown("")
        render_sales_filters_and_table()

if __name__ == "__main__":
    main()
