"""
Dashboard Page
Main KPI dashboard with professional analytics and visualization
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from db_connection import DatabaseConnection
from auth import AuthenticationManager
import sql_queries

def apply_professional_styling():
    """Apply professional CSS styling"""
    st.markdown("""
        <style>
        /* Main theme colors */
        :root {
            --primary: #1e293b;
            --secondary: #64748b;
            --accent: #3b82f6;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --light: #f8fafc;
            --border: #e2e8f0;
        }
        
        /* Metric cards styling */
        .metric-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }
        
        /* Chart containers */
        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            margin: 10px 0;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }
        </style>
    """, unsafe_allow_html=True)

def get_dashboard_metrics():
    """Fetch key metrics from database"""
    
    # Total Sales
    total_sales_result = DatabaseConnection.fetch_one(sql_queries.QUERY_TOTAL_SALES)
    total_sales = float(total_sales_result[0]) if total_sales_result else 0
    
    # Total Received
    total_received_result = DatabaseConnection.fetch_one(sql_queries.QUERY_TOTAL_RECEIVED)
    total_received = float(total_received_result[0]) if total_received_result else 0
    
    # Total Pending
    total_pending_result = DatabaseConnection.fetch_one(sql_queries.QUERY_TOTAL_PENDING)
    total_pending = float(total_pending_result[0]) if total_pending_result else 0
    
    # Collection Percentage
    collection_pct_result = DatabaseConnection.fetch_one(sql_queries.QUERY_COLLECTION_PERCENTAGE)
    collection_percentage = float(collection_pct_result[0]) if collection_pct_result and collection_pct_result[0] else 0
    
    return {
        'total_sales': total_sales,
        'total_received': total_received,
        'total_pending': total_pending,
        'collection_percentage': collection_percentage
    }

def render_metric_card(label: str, value: float, delta: float = None, currency: bool = False):
    """Render a professional metric card"""
    
    # Format value
    if currency:
        formatted_value = f"${value:,.2f}"
    else:
        formatted_value = f"{value:,.2f}" if isinstance(value, float) else f"{value:,}"
    
    # Delta styling
    delta_html = ""
    if delta is not None:
        delta_color = "#10b981" if delta > 0 else "#ef4444"
        delta_symbol = "↑" if delta > 0 else "↓"
        delta_html = f"<span style='color: {delta_color}; font-size: 12px;'>{delta_symbol} {abs(delta):.1f}%</span>"
    
    st.markdown(f"""
        <div style='
            background: white;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #3b82f6;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        '>
            <p style='color: #64748b; font-size: 12px; margin: 0; text-transform: uppercase; letter-spacing: 0.5px;'>
                {label}
            </p>
            <p style='color: #1e293b; font-size: 28px; margin: 8px 0 4px 0; font-weight: 700;'>
                {formatted_value}
            </p>
            {delta_html}
        </div>
    """, unsafe_allow_html=True)

def render_dashboard():
    """Main dashboard rendering"""
    
    apply_professional_styling()
    
    # Header
    st.markdown("""
        <div style='padding: 20px 0; border-bottom: 1px solid #e2e8f0;'>
            <h1 style='color: #1e293b; margin: 0; font-size: 32px;'>Dashboard</h1>
            <p style='color: #64748b; margin: 5px 0 0 0; font-size: 14px;'>
                Last 30 Days Performance Metrics
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    
    # Fetch metrics
    metrics = get_dashboard_metrics()
    
    # KPI Cards Row 1
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card("Total Sales", metrics['total_sales'], currency=True)
    
    with col2:
        render_metric_card("Total Received", metrics['total_received'], currency=True)
    
    with col3:
        render_metric_card("Total Pending", metrics['total_pending'], currency=True)
    
    with col4:
        render_metric_card("Collection Rate", metrics['collection_percentage'], currency=False)
    
    st.markdown("")
    st.markdown("")
    
    # Charts Section
    tab1, tab2, tab3, tab4 = st.tabs(["Sales Trends", " Branch Analytics", "Payment Methods", "📊 Status Distribution"])
    
    # Tab 1: Sales Trends
    with tab1:
        st.markdown("<h3 style='color: #1e293b;'>Monthly Sales & Revenue Trend</h3>", unsafe_allow_html=True)
        
        monthly_trend_df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_MONTHLY_SALES_TREND)
        
        if monthly_trend_df is not None and not monthly_trend_df.empty:
            # Process data - convert DATE_TRUNC result
            monthly_trend_df['month'] = pd.to_datetime(monthly_trend_df['month'], errors='coerce')
            monthly_trend_df = monthly_trend_df.sort_values('month')
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=monthly_trend_df['month'].dt.strftime('%b %Y'),
                y=monthly_trend_df['total_sales'],
                name='Total Sales',
                marker=dict(color='#3b82f6', line=dict(color='#1e40af', width=1)),
                hovertemplate='<b>%{x}</b><br>Sales: $%{y:,.0f}<extra></extra>'
            ))
            
            fig.update_layout(
                title=None,
                xaxis_title="Month",
                yaxis_title="Amount ($)",
                hovermode='x unified',
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family="sans-serif", size=11, color="#1e293b"),
                margin=dict(l=0, r=0, t=0, b=0),
                height=400,
                xaxis=dict(showgrid=False, zeroline=False),
                yaxis=dict(showgrid=True, gridwidth=1, gridcolor='#e2e8f0', zeroline=False)
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("No data available for the selected period")
    
    # Tab 2: Branch Analytics
    with tab2:
        st.markdown("<h3 style='color: #1e293b;'>Branch-Wise Performance</h3>", unsafe_allow_html=True)
        
        branch_df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_BRANCH_WISE_SALES)
        
        if branch_df is not None and not branch_df.empty:
            # Create visualization
            fig = px.bar(
                branch_df,
                x='branch_name',
                y='total_sales_amount',
                color='collection_percentage',
                color_continuous_scale='RdYlGn',
                text='total_sales_amount',
                hover_data={'total_sales_amount': ':.0f', 'collection_percentage': ':.1f'},
                labels={
                    'branch_name': 'Branch',
                    'total_sales_amount': 'Sales Amount',
                    'collection_percentage': 'Collection %'
                }
            )
            
            fig.update_traces(
                texttemplate='$%{text:,.0f}',
                textposition='outside',
                marker=dict(line=dict(width=0))
            )
            
            fig.update_layout(
                title=None,
                xaxis_title="Branch",
                yaxis_title="Sales Amount ($)",
                hovermode='x',
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
        else:
            st.info("No branch data available")
    
    # Tab 3: Payment Methods
    with tab3:
        st.markdown("<h3 style='color: #1e293b;'>Payment Method Breakdown</h3>", unsafe_allow_html=True)
        
        payment_df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_PAYMENT_METHOD_BREAKDOWN)
        
        if payment_df is not None and not payment_df.empty:
            colors = {'Cash': '#3b82f6', 'UPI': '#10b981', 'Card': '#f59e0b'}
            
            fig = go.Figure(data=[
                go.Pie(
                    labels=payment_df['payment_method'],
                    values=payment_df['total_amount'],
                    marker=dict(
                        colors=[colors.get(method, '#3b82f6') for method in payment_df['payment_method']],
                        line=dict(color='white', width=2)
                    ),
                    textposition='auto',
                    texttemplate='%{label}<br>$%{value:,.0f}<br>(%{percent})',
                    hovertemplate='<b>%{label}</b><br>Amount: $%{value:,.2f}<br>Transactions: %{customdata}<extra></extra>',
                    customdata=payment_df['transaction_count']
                )
            ])
            
            fig.update_layout(
                title=None,
                paper_bgcolor='white',
                font=dict(family="sans-serif", size=11, color="#1e293b"),
                margin=dict(l=0, r=0, t=0, b=0),
                height=400,
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("No payment data available")
    
    # Tab 4: Status Distribution
    with tab4:
        st.markdown("<h3 style='color: #1e293b;'>Sales Status Distribution</h3>", unsafe_allow_html=True)
        
        status_df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_PAYMENT_STATUS_DISTRIBUTION)
        
        if status_df is not None and not status_df.empty:
            status_colors = {'Closed': '#10b981', 'Partial': '#f59e0b', 'Open': '#ef4444'}
            
            fig = px.bar(
                status_df,
                x='payment_status',
                y='total_amount',
                color='payment_status',
                text='total_amount',
                color_discrete_map=status_colors,
                labels={
                    'payment_status': 'Status',
                    'total_amount': 'Amount',
                    'count': 'Count'
                },
                hover_data={'count': True, 'percentage': ':.1f'}
            )
            
            fig.update_traces(
                texttemplate='$%{text:,.0f}',
                textposition='outside',
                marker=dict(line=dict(width=0))
            )
            
            fig.update_layout(
                title=None,
                xaxis_title="Payment Status",
                yaxis_title="Amount ($)",
                showlegend=False,
                hovermode='x',
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family="sans-serif", size=11, color="#1e293b"),
                margin=dict(l=0, r=0, t=0, b=0),
                height=400,
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridwidth=1, gridcolor='#e2e8f0')
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("No status data available")
    
    # Bottom Section: Detailed Tables
    st.markdown("")
    st.markdown("---")
    st.markdown("")
    
    col_top, col_pending = st.columns(2)
    
    with col_top:
        st.markdown("<h3 style='color: #1e293b; margin-top: 0;'> Top Performing Branches</h3>", unsafe_allow_html=True)
        
        top_branches = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_TOP_BRANCHES)
        
        if top_branches is not None and not top_branches.empty:
            top_branches['total_sales'] = top_branches['total_sales'].apply(lambda x: f"${x:,.2f}")
            top_branches.columns = ['Branch', 'Sales', 'Count']
            st.dataframe(top_branches, use_container_width=True, hide_index=True)
        else:
            st.info("No branch data")
    
    with col_pending:
        st.markdown("<h3 style='color: #1e293b; margin-top: 0;'> Highest Pending Collections</h3>", unsafe_allow_html=True)
        
        pending = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_PENDING_COLLECTIONS)
        
        if pending is not None and not pending.empty:
            pending = pending.head(5)
            pending['pending_amount'] = pending['pending_amount'].apply(lambda x: f"${x:,.2f}")
            pending = pending[['customer_name', 'branch_name', 'pending_amount', 'days_pending']]
            pending.columns = ['Customer', 'Branch', 'Pending', 'Days']
            st.dataframe(pending, use_container_width=True, hide_index=True)
        else:
            st.info("No pending collections")

def main():
    """Main entry point for dashboard page"""
    AuthenticationManager.require_login()
    render_dashboard()

if __name__ == "__main__":
    main()
