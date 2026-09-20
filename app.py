"""
Sales Intelligence Hub - Main Application
Professional Sales Management & Financial Tracking System
"""

import streamlit as st
from db_connection import DatabaseConnection, verify_db_connection
from auth import AuthenticationManager, show_login_page, initialize_auth
import pages.dashboard as dashboard
import pages.sales as sales
import pages.payments as payments
import pages.reports as reports

# ============================================
# PAGE CONFIGURATION
# ============================================

st.set_page_config(
    page_title="Sales Intelligence Hub",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "Sales Intelligence Hub v1.0 - Professional Business Intelligence Platform"
    }
)

# ============================================
# GLOBAL STYLING
# ============================================

st.markdown("""
    <style>
    /* Root variables */
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
    
    /* Main app styling */
    .main {
        background-color: #ffffff;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Hide default menu */
    #MainMenu {
        visibility: hidden;
    }
    
    /* Footer */
    footer {
        visibility: hidden;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #1e293b;
        font-weight: 600;
    }
    
    /* Text */
    body {
        color: #1e293b;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
    }
    
    /* Cards and containers */
    .st-emotion-cache-1r4qj8v {
        background-color: white;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #3b82f6;
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 500;
        padding: 8px 24px;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #2563eb;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    /* Input fields */
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input,
    .stSelectbox>div>div>select,
    .stTextArea>div>div>textarea {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 10px 12px;
        font-size: 14px;
        color: #1e293b;
    }
    
    .stTextInput>div>div>input:focus,
    .stNumberInput>div>div>input:focus,
    .stSelectbox>div>div>select:focus,
    .stTextArea>div>div>textarea:focus {
        border-color: #3b82f6;
        outline: none;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    /* Metrics */
    .st-emotion-cache-1wmy9hl {
        background-color: white;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        padding: 20px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    
    /* Success/Error messages */
    .st-emotion-cache-1gulkj5 {
        background-color: #dcfce7;
        border-radius: 6px;
        border-left: 4px solid #10b981;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 14px;
        font-weight: 500;
    }
    
    /* Dataframe */
    .stDataFrame {
        border-radius: 6px;
        border: 1px solid #e2e8f0;
    }
    
    /* Option menu styling */
    .nav-link {
        border-radius: 6px;
        margin-bottom: 8px;
        transition: all 0.3s ease;
    }
    
    /* Sidebar menu items */
    .css-1d391kg {
        padding: 0;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# INITIALIZATION
# ============================================

def initialize_app():
    """Initialize application on startup"""
    initialize_auth()
    DatabaseConnection.initialize_pool()

# ============================================
# MAIN APPLICATION
# ============================================

def render_sidebar():
    """Render sidebar navigation"""
    
    with st.sidebar:
        # Logo and branding
        st.markdown("""
            <div style='
                background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                margin-bottom: 30px;
                color: white;
            '>
                <h2 style='margin: 0; font-size: 24px; color: white;'></h2>
                <h3 style='margin: 10px 0 0 0; font-size: 18px; color: white; font-weight: 700;'>
                    Sales Intelligence
                </h3>
                <p style='margin: 5px 0 0 0; font-size: 12px; color: #cbd5e1;'>
                    Business Intelligence Hub
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # User info
        user = AuthenticationManager.get_current_user()
        if user:
            st.markdown(f"""
                <div style='
                    background: #f8fafc;
                    padding: 15px;
                    border-radius: 6px;
                    border: 1px solid #e2e8f0;
                    margin-bottom: 20px;
                '>
                    <p style='margin: 0 0 8px 0; font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px;'>
                        Logged in as
                    </p>
                    <p style='margin: 0; font-size: 14px; font-weight: 600; color: #1e293b;'>
                        {user['username']}
                    </p>
                    <p style='margin: 5px 0 0 0; font-size: 12px; color: #64748b;'>
                        <strong>Role:</strong> {user['role']}
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation menu
        with st.container():
            st.markdown("<p style='color: #64748b; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 15px;'><strong>Navigation</strong></p>", unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button(" Dashboard", use_container_width=True, key="nav_dashboard"):
                    st.session_state.page = "Dashboard"
                    st.rerun()
                
                if st.button(" Sales", use_container_width=True, key="nav_sales"):
                    st.session_state.page = "Sales"
                    st.rerun()
            
            with col2:
                if st.button(" Payments", use_container_width=True, key="nav_payments"):
                    st.session_state.page = "Payments"
                    st.rerun()
                
                if st.button(" Reports", use_container_width=True, key="nav_reports"):
                    st.session_state.page = "Reports"
                    st.rerun()
        
        st.markdown("---")
        
        # Admin section
        if user and user['role'] in ['Super Admin', 'Admin']:
            st.markdown("<p style='color: #64748b; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 15px;'><strong>Admin</strong></p>", unsafe_allow_html=True)
            st.info(" Admin features coming in v2.0")
        
        st.markdown("---")
        
        # Logout button
        col_logout1, col_logout2 = st.columns([1, 1])
        
        with col_logout1:
            if st.button(" Logout", use_container_width=True):
                AuthenticationManager.logout()
                st.rerun()
        
        with col_logout2:
            if st.button("About", use_container_width=True):
                st.session_state.page = "About"
                st.rerun()
        
        st.markdown("")
        st.markdown("""
            <div style='
                background: #f8fafc;
                padding: 15px;
                border-radius: 6px;
                border: 1px solid #e2e8f0;
                font-size: 11px;
                color: #64748b;
                text-align: center;
                margin-top: 40px;
            '>
                <p style='margin: 0;'><strong>Sales Intelligence Hub</strong></p>
                <p style='margin: 5px 0 0 0;'>v1.0</p>
                <p style='margin: 8px 0 0 0; font-size: 10px;'>© 2026 All Rights Reserved</p>
            </div>
        """, unsafe_allow_html=True)

def render_about_page():
    """Render about page"""
    
    st.markdown("""
        <div style='padding: 40px 0;'>
            <h1 style='color: #1e293b; text-align: center; font-size: 36px; margin-bottom: 20px;'>
                Sales Intelligence Hub
            </h1>
            <p style='color: #64748b; text-align: center; font-size: 16px; margin-bottom: 40px;'>
                Professional Business Intelligence & Sales Management Platform
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div style='
                background: white;
                padding: 25px;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                height: 100%;
            '>
                <h3 style='color: #3b82f6; font-size: 24px; margin-bottom: 15px;'>🎯 Mission</h3>
                <p style='color: #64748b; line-height: 1.6;'>
                    Empower businesses with real-time sales insights and financial tracking to make data-driven decisions and optimize revenue growth.
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div style='
                background: white;
                padding: 25px;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                height: 100%;
            '>
                <h3 style='color: #10b981; font-size: 24px; margin-bottom: 15px;'>⚡ Features</h3>
                <ul style='color: #64748b; line-height: 1.8;'>
                    <li>Real-time Dashboard</li>
                    <li>Sales Management</li>
                    <li>Payment Tracking</li>
                    <li>Advanced Reports</li>
                    <li>Role-Based Access</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div style='
                background: white;
                padding: 25px;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                height: 100%;
            '>
                <h3 style='color: #f59e0b; font-size: 24px; margin-bottom: 15px;'>🛠️ Tech Stack</h3>
                <ul style='color: #64748b; line-height: 1.8;'>
                    <li>Python 3.9+</li>
                    <li>Streamlit</li>
                    <li>MySQL</li>
                    <li>Plotly</li>
                    <li>Pandas</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

def main():
    """Main application entry point"""
    
    # Initialize app
    initialize_app()
    
    # Check authentication
    if not AuthenticationManager.is_logged_in():
        show_login_page()
        return
    
    # Render sidebar
    render_sidebar()
    
    # Initialize page state
    if 'page' not in st.session_state:
        st.session_state.page = "Dashboard"
    
    # Route to selected page
    if st.session_state.page == "Dashboard":
        dashboard.main()
    elif st.session_state.page == "Sales":
        sales.main()
    elif st.session_state.page == "Payments":
        payments.main()
    elif st.session_state.page == "Reports":
        reports.main()
    elif st.session_state.page == "About":
        render_about_page()

if __name__ == "__main__":
    main()
