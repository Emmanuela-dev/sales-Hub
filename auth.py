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
            
            user_id, stored_username, full_name, email, phone, password_hash, role, is_active = user_data

            if not is_active:
                return None

            if AuthenticationManager.verify_password(password_hash, password):
                # Update last login
                DatabaseConnection.execute_query(
                    sql_queries.QUERY_UPDATE_LAST_LOGIN, (user_id,))
                return {
                    'user_id':   user_id,
                    'username':  stored_username,
                    'full_name': full_name,
                    'email':     email,
                    'phone':     phone,
                    'role':      role,
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
    # Do NOT set the key to None — that would make is_logged_in() return True
    # while get_current_user() returns None, crashing every role check.
    # We only ensure any stale None value is cleaned up.
    if st.session_state.get(AuthenticationManager.SESSION_KEY) is None:
        if AuthenticationManager.SESSION_KEY in st.session_state:
            del st.session_state[AuthenticationManager.SESSION_KEY]


def _no_users_exist() -> bool:
    """Return True if the users table has zero rows."""
    try:
        result = DatabaseConnection.fetch_one("SELECT COUNT(*) FROM users")
        return (result is None) or (int(result[0]) == 0)
    except Exception:
        return False


def show_setup_wizard():
    """
    First-launch setup wizard — shown only when there are no users at all.
    Creates the Owner account so the system can be used.
    """
    st.markdown("""
    <style>
    .main { background: linear-gradient(135deg, #1a0a2e 0%, #2d1b69 100%) !important; }
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center;margin-bottom:28px;">
            <div style="font-size:48px">💄</div>
            <h1 style="color:#f9a8d4;font-size:26px;font-weight:700;margin:8px 0 4px 0">
                Glamour Hub</h1>
            <p style="color:#a78bfa;font-size:13px;margin:0">
                Welcome! Let's set up your account first.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background:white;border-radius:16px;padding:32px 28px;
                    box-shadow:0 20px 60px rgba(0,0,0,.5);">
        """, unsafe_allow_html=True)

        st.markdown("""
        <h3 style="color:#1e293b;text-align:center;margin:0 0 6px 0;font-size:18px">
            👑 Create Owner Account</h3>
        <p style="color:#64748b;text-align:center;font-size:13px;margin:0 0 24px 0">
            This is the main account for the business owner.
            You can add managers and staff after logging in.
        </p>
        """, unsafe_allow_html=True)

        full_name = st.text_input("Your Full Name *",
                                  placeholder="e.g. Amina Wanjiku",
                                  key="setup_name")
        username  = st.text_input("Choose a Username *",
                                  placeholder="e.g. amina_owner  (no spaces)",
                                  key="setup_username")
        phone     = st.text_input("Phone Number",
                                  placeholder="0722 001 001",
                                  key="setup_phone")
        email     = st.text_input("Email (optional)",
                                  placeholder="amina@glamourhub.co.ke",
                                  key="setup_email")

        st.markdown("<hr style='border:none;border-top:1px solid #f1f5f9;margin:16px 0'>",
                    unsafe_allow_html=True)

        password = st.text_input("Create Password *",
                                 type="password",
                                 placeholder="At least 6 characters",
                                 key="setup_password")
        confirm  = st.text_input("Confirm Password *",
                                 type="password",
                                 key="setup_confirm")

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🚀 Set Up My Account", use_container_width=True,
                     type="primary", key="setup_submit"):
            # Validation
            if not full_name or not username or not password:
                st.error("Full name, username, and password are all required.")
            elif " " in username:
                st.error("Username cannot contain spaces.")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters.")
            elif password != confirm:
                st.error("Passwords do not match.")
            else:
                pw_hash = AuthenticationManager.hash_password(password)
                ok = DatabaseConnection.execute_query(
                    """INSERT INTO users
                       (username, full_name, email, phone, password_hash, role, is_active)
                       VALUES (%s, %s, %s, %s, %s, 'Owner', TRUE)""",
                    (username, full_name, email or None, phone or None, pw_hash)
                )
                if ok:
                    st.success(
                        f"✅ Account created! Welcome, **{full_name}**. "
                        "Please sign in below.")
                    st.rerun()
                else:
                    st.error("Something went wrong. Please try again.")

        st.markdown("</div>", unsafe_allow_html=True)


def show_login_page():
    """Display login page — shown when users exist but nobody is logged in."""
    st.markdown("""
    <style>
    .main { background: linear-gradient(135deg, #1a0a2e 0%, #2d1b69 100%) !important; }
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center;margin-bottom:28px;">
            <div style="font-size:48px">💄</div>
            <h1 style="color:#f9a8d4;font-size:26px;font-weight:700;margin:8px 0 4px 0">
                Glamour Hub</h1>
            <p style="color:#a78bfa;font-size:13px;margin:0">
                Beauty Business Manager</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background:white;border-radius:16px;padding:32px 28px;
                    box-shadow:0 20px 60px rgba(0,0,0,.5);">
        """, unsafe_allow_html=True)

        st.markdown(
            "<h3 style='color:#1e293b;text-align:center;margin:0 0 24px 0;"
            "font-size:18px'>Sign in to your account</h3>",
            unsafe_allow_html=True)

        username = st.text_input("Username", placeholder="Enter your username",
                                 key="login_username")
        password = st.text_input("Password", type="password",
                                 placeholder="Enter your password",
                                 key="login_password")

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🔐 Sign In", use_container_width=True,
                     type="primary", key="login_submit"):
            if username and password:
                if AuthenticationManager.login(username, password):
                    st.rerun()
                else:
                    st.error("❌ Incorrect username or password.")
            else:
                st.warning("Please enter both your username and password.")

        st.markdown("</div>", unsafe_allow_html=True)
