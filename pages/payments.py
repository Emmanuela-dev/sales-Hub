"""
Payments Module Page
Manage payment splits and track payment history
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from db_connection import DatabaseConnection
from auth import AuthenticationManager
import sql_queries

def render_payment_form():
    """Render form to add new payment"""
    
    st.markdown("<h3 style='color: #1e293b;'>➕ Record Payment</h3>", unsafe_allow_html=True)
    
    # Get open sales
    user = AuthenticationManager.get_current_user()
    
    if user['role'] == 'Super Admin':
        open_sales_query = """
            SELECT sale_id, customer_name, sale_amount, pending_amount, branch_name
            FROM customer_sales 
            JOIN branches ON customer_sales.branch_id = branches.branch_id
            WHERE payment_status IN ('Open', 'Partial')
            ORDER BY customer_name
        """
    else:
        open_sales_query = """
            SELECT sale_id, customer_name, sale_amount, pending_amount, branch_name
            FROM customer_sales 
            JOIN branches ON customer_sales.branch_id = branches.branch_id
            WHERE customer_sales.branch_id = %s AND payment_status IN ('Open', 'Partial')
            ORDER BY customer_name
        """
        
    if user['role'] == 'Super Admin':
        open_sales = DatabaseConnection.fetch_dataframe(open_sales_query)
    else:
        open_sales = DatabaseConnection.fetch_dataframe(open_sales_query, params=(user['branch_id'],))
    
    if open_sales is None or open_sales.empty:
        st.info("No open sales to record payments for")
        return
    
    with st.form("add_payment_form", border=False):
        col1, col2 = st.columns(2)
        
        with col1:
            # Sale selection
            sale_options = [f"{row['customer_name']} (ID: {row['sale_id']}) - Pending: ${row['pending_amount']:,.2f}" 
                           for _, row in open_sales.iterrows()]
            selected_sale_idx = st.selectbox("Select Sale", range(len(sale_options)), 
                                            format_func=lambda i: sale_options[i])
            
            selected_sale = open_sales.iloc[selected_sale_idx]
            sale_id = selected_sale['sale_id']
            branch_id = DatabaseConnection.fetch_one(
                "SELECT branch_id FROM customer_sales WHERE sale_id = %s",
                (sale_id,)
            )[0]
            
            # Display sale details
            st.markdown(f"""
                <div style='background: #f8fafc; padding: 15px; border-radius: 6px; border-left: 3px solid #3b82f6;'>
                    <p style='margin: 5px 0; color: #64748b; font-size: 12px;'><strong>Sale Details</strong></p>
                    <p style='margin: 5px 0; color: #1e293b;'><strong>Customer:</strong> {selected_sale['customer_name']}</p>
                    <p style='margin: 5px 0; color: #1e293b;'><strong>Total Amount:</strong> ${selected_sale['sale_amount']:,.2f}</p>
                    <p style='margin: 5px 0; color: #1e293b;'><strong>Pending:</strong> ${selected_sale['pending_amount']:,.2f}</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("")
            
            payment_amount = st.number_input(
                "Payment Amount ($)",
                min_value=0.01,
                max_value=float(selected_sale['pending_amount']),
                step=100.0
            )
        
        with col2:
            payment_method = st.selectbox(
                "Payment Method",
                ["Cash", "UPI", "Card"]
            )
            
            payment_date = st.date_input("Payment Date", value=date.today())
            
            transaction_reference = st.text_input(
                "Transaction Reference",
                placeholder="e.g., UPI_123456789 or Card Last 4 digits"
            )
            
            payment_notes = st.text_area(
                "Notes",
                height=100,
                placeholder="Optional notes about this payment"
            )
        
        col_submit, col_cancel = st.columns([1, 1])
        
        with col_submit:
            if st.form_submit_button("✓ Record Payment", use_container_width=True, type="primary"):
                if payment_amount <= 0:
                    st.error("Payment amount must be greater than 0")
                elif payment_amount > selected_sale['pending_amount']:
                    st.error("Payment amount cannot exceed pending amount")
                else:
                    try:
                        result = DatabaseConnection.execute_query(
                            sql_queries.QUERY_ADD_PAYMENT,
                            (
                                sale_id,
                                branch_id,
                                payment_amount,
                                payment_method,
                                payment_date,
                                transaction_reference,
                                payment_notes
                            )
                        )
                        
                        if result:
                            st.success("✓ Payment recorded successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to record payment")
                    except Exception as e:
                        st.error(f"Error: {e}")
        
        with col_cancel:
            if st.form_submit_button("✕ Clear", use_container_width=True):
                pass

def render_payment_history():
    """Render payment history table"""
    
    st.markdown("<h3 style='color: #1e293b;'>📊 Payment History</h3>", unsafe_allow_html=True)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    user = AuthenticationManager.get_current_user()
    
    with col1:
        if user['role'] == 'Super Admin':
            method_filter = st.selectbox(
                "Filter by Payment Method",
                ["All", "Cash", "UPI", "Card"],
                key="method_filter"
            )
        else:
            method_filter = "All"
    
    with col2:
        date_range = st.selectbox(
            "Date Range",
            ["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days"],
            key="date_range_payment"
        )
    
    with col3:
        sort_by = st.selectbox(
            "Sort by",
            ["Latest", "Oldest", "Highest Amount", "Lowest Amount"],
            key="sort_by_payment"
        )
    
    # Fetch payments
    payments_df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_ALL_PAYMENTS_WITH_DETAILS)
    
    if payments_df is not None and not payments_df.empty:
        # Apply branch filter for non-admin users
        if user['role'] != 'Super Admin':
            payments_df = payments_df[payments_df['branch_name'] == 
                                     DatabaseConnection.fetch_one(
                                         "SELECT branch_name FROM branches WHERE branch_id = %s",
                                         (user['branch_id'],)
                                     )[0]]
        
        # Apply payment method filter
        if method_filter != "All":
            payments_df = payments_df[payments_df['payment_method'] == method_filter]
        
        # Apply date filter
        from datetime import timedelta
        payments_df['payment_date'] = pd.to_datetime(payments_df['payment_date'])
        
        if date_range == "Last 7 Days":
            cutoff = datetime.now() - timedelta(days=7)
            payments_df = payments_df[payments_df['payment_date'] >= cutoff]
        elif date_range == "Last 30 Days":
            cutoff = datetime.now() - timedelta(days=30)
            payments_df = payments_df[payments_df['payment_date'] >= cutoff]
        elif date_range == "Last 90 Days":
            cutoff = datetime.now() - timedelta(days=90)
            payments_df = payments_df[payments_df['payment_date'] >= cutoff]
        
        # Apply sorting
        if sort_by == "Latest":
            payments_df = payments_df.sort_values('payment_date', ascending=False)
        elif sort_by == "Oldest":
            payments_df = payments_df.sort_values('payment_date', ascending=True)
        elif sort_by == "Highest Amount":
            payments_df = payments_df.sort_values('amount', ascending=False)
        elif sort_by == "Lowest Amount":
            payments_df = payments_df.sort_values('amount', ascending=True)
        
        # Format for display
        display_df = payments_df[[
            'payment_id', 'sale_id', 'customer_name', 'branch_name', 'amount',
            'payment_method', 'payment_date', 'transaction_reference'
        ]].copy()
        
        display_df.columns = ['ID', 'Sale ID', 'Customer', 'Branch', 'Amount', 'Method', 'Date', 'Reference']
        display_df['Amount'] = display_df['Amount'].apply(lambda x: f"${x:,.2f}")
        display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Summary stats
        st.markdown("---")
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        
        with col_stat1:
            st.metric("Total Payments", len(payments_df))
        
        with col_stat2:
            total_amount = payments_df['amount'].sum()
            st.metric("Total Amount", f"${total_amount:,.2f}")
        
        with col_stat3:
            cash_count = len(payments_df[payments_df['payment_method'] == 'Cash'])
            st.metric("Cash Payments", cash_count)
        
        with col_stat4:
            digital_count = len(payments_df[payments_df['payment_method'].isin(['UPI', 'Card'])])
            st.metric("Digital Payments", digital_count)
    else:
        st.info("No payment records found")

def render_pending_collections():
    """Render pending collections table"""
    
    st.markdown("<h3 style='color: #1e293b;'>⏳ Pending Collections</h3>", unsafe_allow_html=True)
    
    user = AuthenticationManager.get_current_user()
    
    # Get pending collections
    pending_df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_PENDING_COLLECTIONS)
    
    if pending_df is not None and not pending_df.empty:
        # Apply branch filter for non-admin users
        if user['role'] != 'Super Admin':
            pending_df = pending_df[pending_df['branch_name'] == 
                                   DatabaseConnection.fetch_one(
                                       "SELECT branch_name FROM branches WHERE branch_id = %s",
                                       (user['branch_id'],)
                                   )[0]]
        
        # Sort by pending amount (descending)
        pending_df = pending_df.sort_values('pending_amount', ascending=False)
        
        # Format for display
        display_df = pending_df[[
            'sale_id', 'customer_name', 'branch_name', 'sale_amount',
            'received_amount', 'pending_amount', 'payment_status', 'days_pending'
        ]].copy()
        
        display_df.columns = ['Sale ID', 'Customer', 'Branch', 'Total', 'Received', 'Pending', 'Status', 'Days']
        display_df['Total'] = display_df['Total'].apply(lambda x: f"${x:,.2f}")
        display_df['Received'] = display_df['Received'].apply(lambda x: f"${x:,.2f}")
        display_df['Pending'] = display_df['Pending'].apply(lambda x: f"${x:,.2f}")
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Key metrics
        st.markdown("---")
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        
        with col_stat1:
            st.metric("Total Pending", len(pending_df))
        
        with col_stat2:
            total_pending = pending_df['pending_amount'].sum()
            st.metric("Pending Amount", f"${total_pending:,.2f}")
        
        with col_stat3:
            overdue = len(pending_df[pending_df['days_pending'] > 30])
            st.metric("Overdue (>30 days)", overdue)
    else:
        st.info("No pending collections")

def main():
    """Main entry point for payments page"""
    AuthenticationManager.require_login()
    
    st.markdown("""
        <div style='padding: 20px 0; border-bottom: 1px solid #e2e8f0;'>
            <h1 style='color: #1e293b; margin: 0; font-size: 32px;'>💳 Payment Management</h1>
            <p style='color: #64748b; margin: 5px 0 0 0; font-size: 14px;'>
                Record payments and track collection status
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    
    tab1, tab2, tab3 = st.tabs(["Record Payment", "Payment History", "Pending Collections"])
    
    with tab1:
        st.markdown("")
        render_payment_form()
    
    with tab2:
        st.markdown("")
        render_payment_history()
    
    with tab3:
        st.markdown("")
        render_pending_collections()

if __name__ == "__main__":
    main()
