"""
Glamour Hub - Internal Business Operations System
Sales, Inventory, Expenses, Reports, Staff Management.
Staff see only their own work. Owner/Manager see everything.
"""

import streamlit as st
import sql_queries
from db_connection import DatabaseConnection
from auth import (AuthenticationManager, show_login_page,
                  show_setup_wizard, initialize_auth, _no_users_exist)
import pages.dashboard as dashboard
import pages.sales     as sales
import pages.inventory as inventory
import pages.expenses  as expenses
import pages.reports   as reports
import pages.staff     as staff

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Glamour Hub",
    page_icon="💄",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Glamour Hub — Internal Operations v1.0"},
)

# ── Global CSS ────────────────────────────────────────────────────────────────

st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', sans-serif;
    color: #1e293b;
}
.main { background: #f8fafc; }
[data-testid="stSidebar"] { background: #1a0a2e !important; }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
#MainMenu, footer, header { visibility: hidden; }
.stButton > button { border-radius: 8px; font-weight: 500; transition: all .2s; }
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {
    border-radius: 8px !important;
    border: 1px solid #e2e8f0 !important;
    background: #ffffff !important;
}
.stTabs [data-baseweb="tab"] { font-size: 13px; font-weight: 500; }
.nav-btn > button {
    background: transparent !important; border: none !important;
    text-align: left !important; width: 100% !important;
    padding: 10px 14px !important; border-radius: 8px !important;
    font-size: 14px !important; color: #cbd5e1 !important;
    font-weight: 400 !important; margin-bottom: 2px !important;
}
.nav-btn > button:hover {
    background: rgba(255,255,255,.08) !important;
    color: #ffffff !important; box-shadow: none !important;
}
.nav-btn-active > button {
    background: rgba(236,72,153,.2) !important;
    color: #f9a8d4 !important; font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Navigation ────────────────────────────────────────────────────────────────
# Staff see ONLY Sales/POS and their own dashboard.
# Inventory, Expenses, Reports, Staff Accounts are Owner/Manager only.

OWNER_MANAGER_NAV = [
    ("Dashboard",      "📊", "dashboard"),
    ("Sales / POS",    "🛍", "sales"),
    ("Inventory",      "📦", "inventory"),
    ("Expenses",       "💼", "expenses"),
    ("Reports",        "📈", "reports"),
    ("Staff Accounts", "👤", "staff"),
]

STAFF_NAV = [
    ("My Dashboard",   "📊", "dashboard"),
    ("Sales / POS",    "🛍", "sales"),
]

ROUTER = {
    "dashboard": dashboard.main,
    "sales":     sales.main,
    "inventory": inventory.main,
    "expenses":  expenses.main,
    "reports":   reports.main,
    "staff":     staff.main,
}

# Pages staff are explicitly blocked from, even if they somehow navigate there
STAFF_BLOCKED = {"inventory", "expenses", "reports", "staff"}


def _nav_items(role: str) -> list:
    return STAFF_NAV if role == "Staff" else OWNER_MANAGER_NAV


# ── Sidebar ───────────────────────────────────────────────────────────────────

def render_sidebar(user: dict):
    role = user.get("role", "Staff")
    role_color = {
        "Owner":   "#ec4899",
        "Manager": "#8b5cf6",
        "Staff":   "#3b82f6",
    }.get(role, "#64748b")

    with st.sidebar:

        # Brand header
        st.markdown("""
        <div style="padding:24px 20px 14px;text-align:center;">
            <div style="font-size:34px">💄</div>
            <p style="font-size:15px;font-weight:700;color:#f9a8d4;margin:6px 0 2px 0">
                Glamour Hub</p>
            <p style="font-size:11px;color:#64748b;margin:0">
                Internal Operations</p>
        </div>
        """, unsafe_allow_html=True)

        # Logged-in user chip
        st.markdown(f"""
        <div style="margin:0 12px 14px;background:rgba(255,255,255,.06);
                    border-radius:10px;padding:10px 14px;">
            <p style="font-size:13px;font-weight:600;color:#f1f5f9;margin:0">
                👤 {user.get('full_name', '')}</p>
            <span style="display:inline-block;margin-top:4px;padding:2px 10px;
                         border-radius:20px;font-size:11px;font-weight:600;
                         background:{role_color}30;color:{role_color};">
                {role}</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(
            "<p style='font-size:10px;text-transform:uppercase;letter-spacing:.8px;"
            "color:#475569;padding:0 14px;margin:0 0 6px 0;'>Menu</p>",
            unsafe_allow_html=True)

        current = st.session_state.get("page", "dashboard")

        for label, icon, key in _nav_items(role):
            css = "nav-btn-active nav-btn" if current == key else "nav-btn"
            st.markdown(f"<div class='{css}'>", unsafe_allow_html=True)
            if st.button(f"{icon}  {label}", key=f"nav_{key}",
                         use_container_width=True):
                st.session_state.page = key
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            "<hr style='border:none;border-top:1px solid rgba(255,255,255,.08);"
            "margin:14px 0;'>",
            unsafe_allow_html=True)

        # Low-stock alert badge — only for Owner/Manager
        if role != "Staff":
            try:
                low = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_LOW_STOCK)
                if low is not None and not low.empty:
                    st.markdown(f"""
                    <div style="margin:0 12px 10px;background:#dc262620;border-radius:8px;
                                padding:8px 14px;border-left:3px solid #dc2626;">
                        <p style="color:#fca5a5;font-size:12px;font-weight:600;margin:0;">
                            📦 {len(low)} item(s) low / out of stock</p>
                    </div>""", unsafe_allow_html=True)
            except Exception:
                pass

        # Logout
        st.markdown("<div class='nav-btn'>", unsafe_allow_html=True)
        if st.button("🚪  Logout", key="nav_logout", use_container_width=True):
            AuthenticationManager.logout()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div style="position:absolute;bottom:14px;left:0;right:0;
                    text-align:center;padding:0 16px;">
            <p style="font-size:10px;color:#334155;margin:0;">
                © 2026 Glamour Hub v1.0</p>
        </div>""", unsafe_allow_html=True)


# ── Main entry point ──────────────────────────────────────────────────────────

def main():
    initialize_auth()
    DatabaseConnection.initialize_pool()

    # First launch — no users in DB yet → show owner setup wizard
    if _no_users_exist():
        show_setup_wizard()
        return

    # Not logged in → show login page
    if not AuthenticationManager.is_logged_in():
        show_login_page()
        return

    user = AuthenticationManager.get_current_user()
    if not user:
        show_login_page()
        return

    # Default page
    if "page" not in st.session_state:
        st.session_state.page = "dashboard"

    render_sidebar(user)

    current = st.session_state.get("page", "dashboard")
    role    = user.get("role", "Staff")

    # Hard block: staff cannot access restricted pages
    if role == "Staff" and current in STAFF_BLOCKED:
        st.session_state.page = "dashboard"
        st.rerun()

    # Render the active page, passing role context via session state
    st.session_state["current_role"] = role
    ROUTER.get(current, dashboard.main)()


if __name__ == "__main__":
    main()
