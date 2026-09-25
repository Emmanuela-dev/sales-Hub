"""Internal staff account management."""

import streamlit as st
import pandas as pd

from auth import AuthenticationManager
from db_connection import DatabaseConnection
import sql_queries


def _css():
    st.markdown("""
    <style>
    .section { color:#1e293b; font-size:16px; font-weight:600;
               margin:0 0 12px 0; }
    </style>
    """, unsafe_allow_html=True)


def _create_account(current_role: str):
    st.markdown('<p class="section">Create Staff Account</p>',
                unsafe_allow_html=True)
    st.caption("Give the staff member these credentials so they can sign in.")

    with st.form("create_staff_account"):
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full name", key="new_staff_name")
            username = st.text_input("Username", key="new_staff_username")
            email = st.text_input("Email (optional)", key="new_staff_email")
        with col2:
            phone = st.text_input("Phone (optional)", key="new_staff_phone")
            password = st.text_input("Temporary password", type="password",
                                     key="new_staff_password")
            confirm = st.text_input("Confirm password", type="password",
                                    key="new_staff_confirm")

        role = "Staff"
        if current_role == "Owner":
            role = st.selectbox("Account role", ["Staff", "Manager"],
                                key="new_staff_role")

        submitted = st.form_submit_button("Create Account", type="primary",
                                          use_container_width=True)

    if not submitted:
        return

    username = username.strip()
    full_name = full_name.strip()
    if not full_name or not username or not password:
        st.error("Full name, username, and password are required.")
        return
    if password != confirm:
        st.error("Passwords do not match.")
        return
    if len(password) < 6:
        st.error("Password must be at least 6 characters.")
        return

    password_hash = AuthenticationManager.hash_password(password)
    ok = DatabaseConnection.execute_query(
        sql_queries.QUERY_CREATE_USER,
        (username, full_name, email.strip() or None, phone.strip() or None,
         password_hash, role),
    )
    if ok:
        st.success(f"Account created for {full_name}. They can now log in as {username}.")
        st.rerun()


def _accounts():
    st.markdown('<p class="section">Existing Accounts</p>',
                unsafe_allow_html=True)
    df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_ALL_STAFF)
    if df is None or df.empty:
        st.info("No accounts found.")
        return

    display = df.copy()
    display["status"] = display["is_active"].map(
        {True: "Active", False: "Inactive"})
    display = display[["full_name", "username", "role", "email", "phone",
                       "status", "last_login"]]
    display.columns = ["Name", "Username", "Role", "Email", "Phone",
                       "Status", "Last Login"]
    st.dataframe(display, use_container_width=True, hide_index=True)

    current_user = AuthenticationManager.get_current_user()
    manageable = display[display["Username"] != current_user.get("username")]
    if manageable.empty:
        return

    st.markdown("**Change account status**")
    selected = st.selectbox("Account", manageable["Username"].tolist(),
                            key="status_account")
    selected_row = df[df["username"] == selected].iloc[0]
    next_status = not bool(selected_row["is_active"])
    label = "Activate" if next_status else "Deactivate"
    if st.button(label, key="change_account_status"):
        DatabaseConnection.execute_query(
            sql_queries.QUERY_UPDATE_USER_STATUS,
            (next_status, int(selected_row["user_id"])),
        )
        st.success(f"{selected} is now {'active' if next_status else 'inactive'}.")
        st.rerun()


def main():
    AuthenticationManager.require_login()
    user = AuthenticationManager.get_current_user()
    if not user or user.get("role") not in ("Owner", "Manager"):
        st.error("Only the Owner or Manager can manage staff accounts.")
        st.stop()

    _css()
    st.markdown("""
    <div style="padding:16px 0 20px 0;border-bottom:1px solid #e2e8f0;
                margin-bottom:24px;">
        <h1 style="color:#1e293b;margin:0;font-size:26px;font-weight:700;">
            👤 Staff Accounts
        </h1>
        <p style="color:#64748b;margin:4px 0 0 0;font-size:14px;">
            Create and manage internal user access for the business.
        </p>
    </div>
    """, unsafe_allow_html=True)
    _create_account(user["role"])
    st.markdown("<br>", unsafe_allow_html=True)
    _accounts()


if __name__ == "__main__":
    main()