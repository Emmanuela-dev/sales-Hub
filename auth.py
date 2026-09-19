"""
Authentication Module
Handles user authentication, session management, and role-based access control
"""

import streamlit as st
import bcrypt
from datetime import datetime
from db_connection import DatabaseConnection
import sql_queries

class AuthenticationManager:
    """
    Manages user authentication, sessions, and permissions
    """
    
    SESSION_KEY = "user_session"
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def verify_password(stored_hash: str, provided_password: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hash.encode('utf-8'))
        except Exception:
            return False
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> dict:
        """
        Authenticate user against database
        
        Args:
            username: Username
            password: Password
            
        Returns:
            User info dict if successful, None otherwise
        """
        try:
            user_data = DatabaseConnection.fetch_one(
                sql_queries.QUERY_USER_BY_USERNAME,
                (username,)
            )
            
            if user_data is None:
                return None
            
            user_id, stored_username, email, role, branch_id, is_active, password_hash = user_data
            
            if not is_active:
                return None
            
            if AuthenticationManager.verify_password(password_hash, password):
                return {
                    'user_id': user_id,
                    'username': stored_username,
                    'email': email,
                    'role': role,
                    'branch_id': branch_id,
                    'is_active': is_active
                }
            
            return None
            
        except Exception as e:
            st.error(f"Authentication error: {e}")
            return None
    
    @staticmethod
    def login(username: str, password: str) -> bool:
        """
        Login user and create session
        
        Args:
            username: Username
            password: Password
            
        Returns:
            True if login successful
        """
        user = AuthenticationManager.authenticate_user(username, password)
        
        if user:
            st.session_state[AuthenticationManager.SESSION_KEY] = user
            st.session_state.login_time = datetime.now()
            return True
        
        return False
    
    @staticmethod
    def logout():
        """Logout user and clear session"""
        if AuthenticationManager.SESSION_KEY in st.session_state:
            del st.session_state[AuthenticationManager.SESSION_KEY]
        if 'login_time' in st.session_state:
            del st.session_state['login_time']
    
    @staticmethod
    def is_logged_in() -> bool:
        """Check if user is logged in"""
        return AuthenticationManager.SESSION_KEY in st.session_state
    
    @staticmethod
    def get_current_user() -> dict:
        """Get current logged-in user info"""
        if AuthenticationManager.is_logged_in():
            return st.session_state[AuthenticationManager.SESSION_KEY]
        return None
    
    @staticmethod
    def get_user_role() -> str:
        """Get current user's role"""
        user = AuthenticationManager.get_current_user()
        return user['role'] if user else None
    
    @staticmethod
    def get_user_branch() -> int:
        """Get current user's branch ID"""
        user = AuthenticationManager.get_current_user()
        return user['branch_id'] if user else None
    
    @staticmethod
    def require_login():
        """Redirect to login if not authenticated"""
        if not AuthenticationManager.is_logged_in():
            st.warning("Please login to access this page")
            st.stop()
    
    @staticmethod
    def require_role(*allowed_roles):
        """
        Require user to have specific role
        
        Args:
            allowed_roles: Tuple of allowed roles
        """
        user_role = AuthenticationManager.get_user_role()
        if user_role not in allowed_roles:
            st.error("❌ Insufficient permissions. Access denied.")
            st.stop()
    
    @staticmethod
    def is_admin() -> bool:
        """Check if user is Super Admin"""
        return AuthenticationManager.get_user_role() == 'Super Admin'
    
    @staticmethod
    def is_branch_admin() -> bool:
        """Check if user is Admin"""
        return AuthenticationManager.get_user_role() == 'Admin'
    
    @staticmethod
    def can_view_all_branches() -> bool:
        """Check if user can view all branches"""
        return AuthenticationManager.is_admin()
    
    @staticmethod
    def apply_branch_filter(branch_id_param: int = None) -> int:
        """
        Apply branch filter based on user role
        
        Args:
            branch_id_param: Optional branch ID parameter
            
        Returns:
            Filtered branch ID
        """
        user = AuthenticationManager.get_current_user()
        
        if user['role'] == 'Super Admin':
            return branch_id_param
        elif user['role'] == 'Admin':
            return user['branch_id']
        else:
            return user['branch_id']


def initialize_auth():
    """Initialize authentication on app startup"""
    if AuthenticationManager.SESSION_KEY not in st.session_state:
        st.session_state[AuthenticationManager.SESSION_KEY] = None


def show_login_page():
    """Display login page"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("---")
        st.markdown(
            """
            <div style='text-align: center; padding: 40px 0;'>
                <h1 style='color: #1e293b; font-size: 32px; margin-bottom: 10px;'>
                    📊 Sales Intelligence Hub
                </h1>
                <p style='color: #64748b; font-size: 16px;'>
                    Professional Business Intelligence Platform
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("---")
        
        col_space1, col_input, col_space2 = st.columns([0.5, 2, 0.5])
        
        with col_input:
            st.markdown(
                "<h3 style='color: #1e293b; text-align: center;'>Login to Your Account</h3>",
                unsafe_allow_html=True
            )
            
            username = st.text_input(
                "Username",
                placeholder="Enter your username",
                key="login_username"
            )
            
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                key="login_password"
            )
            
            col_btn1, col_btn2 = st.columns([1, 1])
            
            with col_btn1:
                if st.button("🔐 Login", use_container_width=True, type="primary"):
                    if username and password:
                        if AuthenticationManager.login(username, password):
                            st.success("✓ Login successful!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password")
                    else:
                        st.warning("Please enter username and password")
            
            st.markdown("")
            
            st.markdown(
                """
                <p style='color: #64748b; font-size: 12px; text-align: center; margin-top: 30px;'>
                    <strong>Demo Credentials:</strong><br>
                    Username: <code>superadmin</code> | Password: <code>admin123</code><br>
                    or<br>
                    Username: <code>ny_admin</code> | Password: <code>admin123</code>
                </p>
                """,
                unsafe_allow_html=True
            )
        
        st.markdown("---")
