"""
Reports Module Page
Advanced analytics and reporting
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from db_connection import DatabaseConnection
from auth import AuthenticationManager
import sql_queries

def _fmt_currency(value) -> str:
    """Format a value as currency, returning Ksh0.00 for None/NaN."""
    try:
        return f"${float(value):,.2f}"
    except (TypeError, ValueError):
        return "Ksh0.00"

def _fmt_percent(value) -> str:
    """Format a value as percentage, returning 0.0% for None/NaN."""
    try:
        return f"{float(value):.1f}%"
    except (TypeError, ValueError):
        return "0.0%"

def _fmt_int(value) -> str:
    """Format a value as integer string, returning 0 for None/NaN."""
    try:
        return str(int(float(value)))
    except (TypeError, ValueError):
        return "0"

def _fmt_date(value, fmt='%Y-%m-%d') -> str:
    """Format a date/datetime/string value safely, returning empty string on failure."""
    if value is None:
        return ""
    try:
        if hasattr(value, 'strftime'):          # date or datetime object
            return value.strftime(fmt)
        return pd.to_datetime(value).strftime(fmt)
    except Exception:
        return str(value)
    except (TypeError, ValueError):
        return "0"

def render_revenue_analysis():
    """Render revenue analysis report"""
    
    st.markdown("<h3 style='color: #1e293b;'> Revenue Analysis</h3>", unsafe_allow_html=True)
    
    # Get revenue data
    revenue_df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_TOTAL_REVENUE_ANALYSIS)
    
    if revenue_df is not None and not revenue_df.empty:
        row = revenue_df.iloc[0]
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Sales", _fmt_currency(row.get('total_sales')))
        
        with col2:
            st.metric("Total Received", _fmt_currency(row.get('total_received')))
        
        with col3:
            st.metric("Total Pending", _fmt_currency(row.get('total_pending')))
        
        with col4:
            st.metric("Collection Rate", _fmt_percent(row.get('collection_rate')))

def render_branch_performance():
    """Render branch performance report"""
    
    st.markdown("<h3 style='color: #1e293b;'> Branch Performance Report</h3>", unsafe_allow_html=True)
    
    branch_df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_BRANCH_EFFICIENCY)
    
    if branch_df is not None and not branch_df.empty:
        # Performance metrics by branch
        display_df = branch_df[[
            'branch_name', 'total_sales', 'closed_sales', 'closing_percentage', 'avg_days_open'
        ]].copy()
        
        display_df.columns = ['Branch', 'Total Sales', 'Closed', 'Closing %', 'Avg Days Open']
        display_df['Closing %'] = display_df['Closing %'].apply(_fmt_percent)
        display_df['Avg Days Open'] = display_df['Avg Days Open'].apply(_fmt_int)
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Chart
        fig = px.bar(
            branch_df,
            x='branch_name',
            y='closing_percentage',
            color='closing_percentage',
            color_continuous_scale='RdYlGn',
            text='closing_percentage',
            labels={'branch_name': 'Branch', 'closing_percentage': 'Closing %'},
            title="Branch Closing Efficiency"
        )
        
        fig.update_traces(
            texttemplate='%{text:.1f}%',
            textposition='outside',
            marker=dict(line=dict(width=0))
        )
        
        fig.update_layout(
            title=None,
            xaxis_title="Branch",
            yaxis_title="Closing Percentage (%)",
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="sans-serif", size=11, color="#1e293b"),
            margin=dict(l=0, r=0, t=0, b=0),
            height=400,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridwidth=1, gridcolor='#e2e8f0')
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def render_collection_efficiency():
    """Render collection efficiency report"""
    
    st.markdown("<h3 style='color: #1e293b;'> Collection Efficiency Report</h3>", unsafe_allow_html=True)
    
    collection_df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_COLLECTION_EFFICIENCY)
    
    if collection_df is not None and not collection_df.empty:
        display_df = collection_df[[
            'branch_name', 'total_sales', 'collected_sales', 'total_amount',
            'collected_amount', 'collection_percentage', 'avg_payment_days'
        ]].copy()
        
        display_df.columns = ['Branch', 'Total Sales', 'Collected', 'Total Amount', 'Collected Amt', 'Collection %', 'Avg Days']
        display_df['Total Amount'] = display_df['Total Amount'].apply(_fmt_currency)
        display_df['Collected Amt'] = display_df['Collected Amt'].apply(_fmt_currency)
        display_df['Collection %'] = display_df['Collection %'].apply(_fmt_percent)
        display_df['Avg Days'] = display_df['Avg Days'].apply(_fmt_int)
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)

def render_top_sales():
    """Render highest sales report"""
    
    st.markdown("<h3 style='color: #1e293b;'> Top Sales Records</h3>", unsafe_allow_html=True)
    
    top_sales_df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_HIGHEST_SALES)
    
    if top_sales_df is not None and not top_sales_df.empty:
        display_df = top_sales_df[[
            'sale_id', 'customer_name', 'branch_name', 'product_category',
            'sale_amount', 'received_amount', 'payment_status', 'sale_date'
        ]].copy()
        
        display_df.columns = ['ID', 'Customer', 'Branch', 'Category', 'Amount', 'Received', 'Status', 'Date']
        display_df['Amount'] = display_df['Amount'].apply(_fmt_currency)
        display_df['Received'] = display_df['Received'].apply(_fmt_currency)
        display_df['Date'] = display_df['Date'].apply(_fmt_date)
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)

def render_top_customers():
    """Render top customers report"""
    
    st.markdown("<h3 style='color: #1e293b;'> Top Customers by Sales</h3>", unsafe_allow_html=True)
    
    customers_df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_TOP_CUSTOMERS)
    
    if customers_df is not None and not customers_df.empty:
        display_df = customers_df[[
            'customer_name', 'branch_name', 'purchase_count', 'total_purchase_amount', 'total_paid'
        ]].copy()
        
        display_df.columns = ['Customer', 'Branch', 'Purchases', 'Total', 'Paid']
        display_df['Total'] = display_df['Total'].apply(_fmt_currency)
        display_df['Paid'] = display_df['Paid'].apply(_fmt_currency)
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Chart
        fig = px.bar(
            customers_df.head(10),
            x='customer_name',
            y='total_purchase_amount',
            color='total_purchase_amount',
            color_continuous_scale='Blues',
            text='total_purchase_amount',
            labels={'customer_name': 'Customer', 'total_purchase_amount': 'Total Sales'},
            title="Top 10 Customers"
        )
        
        fig.update_traces(
            texttemplate='$%{text:,.0f}',
            textposition='outside',
            marker=dict(line=dict(width=0))
        )
        
        fig.update_layout(
            title=None,
            xaxis_title="Customer",
            yaxis_title="Sales Amount ($)",
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="sans-serif", size=10, color="#1e293b"),
            margin=dict(l=0, r=0, t=0, b=0),
            height=400,
            xaxis=dict(showgrid=False, tickangle=-45),
            yaxis=dict(showgrid=True, gridwidth=1, gridcolor='#e2e8f0')
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def render_payment_method_analysis():
    """Render payment method analysis"""
    
    st.markdown("<h3 style='color: #1e293b;'> Payment Method Analysis</h3>", unsafe_allow_html=True)
    
    payment_df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_PAYMENT_METHOD_BREAKDOWN)
    
    if payment_df is not None and not payment_df.empty:
        display_df = payment_df[[
            'payment_method', 'transaction_count', 'total_amount', 'percentage'
        ]].copy()
        
        display_df.columns = ['Method', 'Transactions', 'Amount', 'Percentage']
        display_df['Amount'] = display_df['Amount'].apply(_fmt_currency)
        display_df['Percentage'] = display_df['Percentage'].apply(_fmt_percent)
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Create detailed visualization
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(
                payment_df,
                values='total_amount',
                names='payment_method',
                title="Revenue by Payment Method",
                color_discrete_map={'Cash': '#3b82f6', 'UPI': '#10b981', 'Card': '#f59e0b'}
            )
            
            fig.update_layout(
                title=None,
                paper_bgcolor='white',
                font=dict(family="sans-serif", size=11, color="#1e293b"),
                margin=dict(l=0, r=0, t=0, b=0),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with col2:
            fig = px.bar(
                payment_df,
                x='payment_method',
                y='transaction_count',
                color='payment_method',
                text='transaction_count',
                color_discrete_map={'Cash': '#3b82f6', 'UPI': '#10b981', 'Card': '#f59e0b'},
                labels={'payment_method': 'Method', 'transaction_count': 'Count'},
                title="Transaction Count by Method"
            )
            
            fig.update_traces(
                textposition='outside',
                marker=dict(line=dict(width=0))
            )
            
            fig.update_layout(
                title=None,
                xaxis_title="Method",
                yaxis_title="Count",
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family="sans-serif", size=11, color="#1e293b"),
                margin=dict(l=0, r=0, t=0, b=0),
                height=400,
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridwidth=1, gridcolor='#e2e8f0')
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def render_category_analysis():
    """Render product category analysis"""
    
    st.markdown("<h3 style='color: #1e293b;'>Product Category Analysis</h3>", unsafe_allow_html=True)
    
    category_df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_PRODUCT_CATEGORY_BREAKDOWN)
    
    if category_df is not None and not category_df.empty:
        display_df = category_df[[
            'product_category', 'count', 'total_amount', 'total_received', 'collection_rate'
        ]].copy()
        
        display_df.columns = ['Category', 'Count', 'Total', 'Received', 'Collection %']
        display_df['Total'] = display_df['Total'].apply(_fmt_currency)
        display_df['Received'] = display_df['Received'].apply(_fmt_currency)
        display_df['Collection %'] = display_df['Collection %'].apply(_fmt_percent)
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Chart
        fig = px.bar(
            category_df,
            x='product_category',
            y='total_amount',
            color='collection_rate',
            color_continuous_scale='RdYlGn',
            text='total_amount',
            labels={'product_category': 'Category', 'total_amount': 'Amount', 'collection_rate': 'Collection %'},
            title="Sales by Category"
        )
        
        fig.update_traces(
            texttemplate='$%{text:,.0f}',
            textposition='outside',
            marker=dict(line=dict(width=0))
        )
        
        fig.update_layout(
            title=None,
            xaxis_title="Category",
            yaxis_title="Amount ($)",
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="sans-serif", size=11, color="#1e293b"),
            margin=dict(l=0, r=0, t=0, b=0),
            height=400,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridwidth=1, gridcolor='#e2e8f0'),
            coloraxis_colorbar=dict(title="Collection %")
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def render_overdue_analysis():
    """Render overdue collections analysis"""
    
    st.markdown("<h3 style='color: #1e293b;'> Overdue Collections (>30 Days)</h3>", unsafe_allow_html=True)
    
    overdue_df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_OVERDUE_COLLECTIONS)
    
    if overdue_df is not None and not overdue_df.empty:
        display_df = overdue_df[[
            'sale_id', 'customer_name', 'branch_name', 'pending_amount', 'days_overdue'
        ]].copy()
        
        display_df.columns = ['Sale ID', 'Customer', 'Branch', 'Pending', 'Days Overdue']
        display_df['Pending'] = display_df['Pending'].apply(_fmt_currency)
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Summary
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Overdue Records", len(overdue_df))
        
        with col2:
            total_overdue = overdue_df['pending_amount'].sum()
            st.metric("Total Overdue Amount", f"${total_overdue:,.2f}")
        
        with col3:
            avg_days = overdue_df['days_overdue'].mean()
            st.metric("Avg Days Overdue", f"{int(avg_days)}" if pd.notna(avg_days) else "N/A")
    else:
        st.info("No overdue collections")

def main():
    """Main entry point for reports page"""
    AuthenticationManager.require_login()
    
    st.markdown("""
        <div style='padding: 20px 0; border-bottom: 1px solid #e2e8f0;'>
            <h1 style='color: #1e293b; margin: 0; font-size: 32px;'> Reports & Analytics</h1>
            <p style='color: #64748b; margin: 5px 0 0 0; font-size: 14px;'>
                Comprehensive business intelligence and analytics
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Revenue",
        "Branch Performance",
        "Collection",
        "Top Sales",
        "Payment Methods",
        "Categories",
        "Overdue"
    ])
    
    with tab1:
        st.markdown("")
        render_revenue_analysis()
    
    with tab2:
        st.markdown("")
        render_branch_performance()
    
    with tab3:
        st.markdown("")
        render_collection_efficiency()
    
    with tab4:
        st.markdown("")
        render_top_sales()
        st.markdown("---")
        render_top_customers()
    
    with tab5:
        st.markdown("")
        render_payment_method_analysis()
    
    with tab6:
        st.markdown("")
        render_category_analysis()
    
    with tab7:
        st.markdown("")
        render_overdue_analysis()

if __name__ == "__main__":
    main()
