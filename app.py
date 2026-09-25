"""Glamour Hub internal sales and business operations system."""

import streamlit as st
from db_connection import DatabaseConnection
from auth import AuthenticationManager, show_login_page, initialize_auth
import pages.dashboard  as dashboard
import pages.sales      as sales
import pages.inventory  as inventory
import pages.expenses   as expenses
import pages.reports    as reports
import pages.staff      as staff

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Glamour Hub",
    page_icon="💄",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Glamour Hub — Beauty Business Management v1.0"},
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

# ── Nav config ────────────────────────────────────────────────────────────────

NAV_ITEMS = [
    ("Dashboard",  "📊", "dashboard",  None),
    ("Sales / POS","🛍", "sales",      None),
    ("Inventory",  "📦", "inventory",  ["Owner", "Manager"]),
    ("Expenses",   "💼", "expenses",   ["Owner", "Manager"]),
    ("Reports",    "📈", "reports",    ["Owner","Manager"]),
    ("Staff Accounts", "👤", "staff",   ["Owner","Manager"]),
]


def _has_access(roles_allowed, role):
    return roles_allowed is None or role in roles_allowed


# ── Sidebar ───────────────────────────────────────────────────────────────────

def render_sidebar(user: dict):
    with st.sidebar:
        # Brand
        st.markdown("""
        <div style="padding:24px 20px 16px;text-align:center;">
            <div style="font-size:36px">💄</div>
            <p style="font-size:16px;font-weight:700;color:#f9a8d4;margin:4px 0 0 0">
                Glamour Hub</p>
            <p style="font-size:11px;color:#64748b;margin:2px 0 0 0">
                Beauty Business Manager</p>
        </div>
        """, unsafe_allow_html=True)

        # User
        role = user.get("role","Staff")
        role_color = {
            "Owner":"#ec4899","Manager":"#8b5cf6","Staff":"#3b82f6"
        }.get(role,"#64748b")

        st.markdown(f"""
        <div style="margin:0 12px 16px;background:rgba(255,255,255,.06);
                    border-radius:10px;padding:10px 14px">
            <p style="font-size:13px;font-weight:600;color:#f1f5f9;margin:0">
                👤 {user.get('full_name','')}</p>
            <span style="display:inline-block;margin-top:4px;padding:2px 10px;
                         border-radius:20px;font-size:11px;font-weight:600;
                         background:{role_color}30;color:{role_color}">
                {role}</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(
            "<p style='font-size:10px;text-transform:uppercase;"
            "letter-spacing:.8px;color:#475569;padding:0 14px;"
            "margin:0 0 6px 0'>Menu</p>",
            unsafe_allow_html=True)

        current = st.session_state.get("page","dashboard")

        for label,icon,key,roles in NAV_ITEMS:
            if not _has_access(roles, role):
                continue
            css = "nav-btn-active nav-btn" if current==key else "nav-btn"
            st.markdown(f"<div class='{css}'>", unsafe_allow_html=True)
            if st.button(f"{icon}  {label}", key=f"nav_{key}",
                         use_container_width=True):
                st.session_state.page = key
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            "<hr style='border:none;border-top:1px solid rgba(255,255,255,.08);"
            "margin:16px 0'>", unsafe_allow_html=True)

        # Low stock badge
        low = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_LOW_STOCK)
        if low is not None and not low.empty:
            st.markdown(f"""
            <div style="margin:0 12px 12px;background:#dc262620;border-radius:8px;
                        padding:8px 14px;border-left:3px solid #dc2626">
                <p style="color:#fca5a5;font-size:12px;font-weight:600;margin:0">
                    📦 {len(low)} item(s) low on stock</p>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div class='nav-btn'>", unsafe_allow_html=True)
        if st.button("🚪  Logout", key="nav_logout", use_container_width=True):
            AuthenticationManager.logout(); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div style="position:absolute;bottom:16px;left:0;right:0;
                    text-align:center;padding:0 16px">
            <p style="font-size:10px;color:#334155;margin:0">
                © 2026 Glamour Hub v1.0</p>
        </div>""", unsafe_allow_html=True)


# ── Router ────────────────────────────────────────────────────────────────────

def route(page_key: str):
    {
        "dashboard": dashboard.main,
        "sales":     sales.main,
        "inventory": inventory.main,
        "expenses":  expenses.main,
        "reports":   reports.main,
        "staff":     staff.main,
    }.get(page_key, dashboard.main)()


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    import sql_queries as sq
    global sql_queries
    sql_queries = sq

    initialize_auth()
    DatabaseConnection.initialize_pool()

    if not AuthenticationManager.is_logged_in():
        show_login_page(); return

    user = AuthenticationManager.get_current_user()
    if not user:
        show_login_page(); return

    if "page" not in st.session_state:
        st.session_state.page = "dashboard"

    render_sidebar(user)

    current = st.session_state.get("page","dashboard")
    role    = user.get("role","Staff")

    # Gate check
    for _,_,key,roles in NAV_ITEMS:
        if key == current and not _has_access(roles, role):
            st.error("🔒 You don't have permission to view this page.")
            st.session_state.page = "dashboard"
            st.rerun()

    route(current)


if __name__ == "__main__":
    main()
