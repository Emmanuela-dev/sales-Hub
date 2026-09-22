"""
Staff Accounts - Glamour Hub Beauty Business
Owner can create Manager and Staff accounts.
Manager can create Staff accounts only.
Staff cannot access this page.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from db_connection import DatabaseConnection
from auth import AuthenticationManager
import sql_queries


# ── helpers ───────────────────────────────────────────────────────────────────

def _hash(password: str) -> str:
    return AuthenticationManager.hash_password(password)


def _css():
    st.markdown("""
    <style>
    .staff-card {
        background: white; border-radius: 10px; padding: 16px 20px;
        border: 1px solid #e2e8f0; margin-bottom: 10px;
        box-shadow: 0 1px 4px rgba(0,0,0,.05);
        display: flex; justify-content: space-between; align-items: center;
    }
    .role-badge {
        display: inline-block; padding: 3px 12px; border-radius: 20px;
        font-size: 11px; font-weight: 600;
    }
    .section { color:#1e293b; font-size:16px; font-weight:600; margin:0 0 14px 0; }
    </style>
    """, unsafe_allow_html=True)


ROLE_STYLE = {
    "Owner":   ("#ec4899", "#fdf2f8"),
    "Manager": ("#8b5cf6", "#f5f3ff"),
    "Staff":   ("#3b82f6", "#eff6ff"),
}


# ── Staff list ────────────────────────────────────────────────────────────────

def _staff_list(current_user: dict):
    st.markdown('<p class="section">👥 Team Accounts</p>', unsafe_allow_html=True)

    df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_ALL_STAFF)
    if df is None or df.empty:
        st.info("No staff accounts found.")
        return

    role = current_user.get("role", "Staff")

    for _, row in df.iterrows():
        tc, tbg = ROLE_STYLE.get(str(row.get("role", "")), ("#64748b", "#f1f5f9"))
        last_login = row.get("last_login")
        last_login_str = (
            pd.to_datetime(last_login).strftime("%d %b %Y %H:%M")
            if last_login is not None and str(last_login) not in ("", "None", "NaT")
            else "Never"
        )
        is_active = bool(row.get("is_active", True))
        status_color = "#16a34a" if is_active else "#dc2626"
        status_txt   = "Active" if is_active else "Deactivated"

        col_info, col_actions = st.columns([5, 1])

        with col_info:
            st.markdown(f"""
            <div class="staff-card">
                <div>
                    <p style="font-weight:700;color:#1e293b;margin:0;font-size:14px">
                        {row['full_name']}
                        <span class="role-badge"
                              style="background:{tbg};color:{tc};margin-left:8px">
                            {row['role']}</span>
                    </p>
                    <p style="color:#64748b;font-size:12px;margin:4px 0 0 0">
                        👤 @{row['username']}
                        {f" &nbsp;·&nbsp; ✉ {row['email']}" if row.get('email') else ""}
                        {f" &nbsp;·&nbsp; 📞 {row['phone']}" if row.get('phone') else ""}
                    </p>
                    <p style="font-size:11px;margin:3px 0 0 0">
                        <span style="color:{status_color}">● {status_txt}</span>
                        &nbsp;·&nbsp;
                        <span style="color:#64748b">Last login: {last_login_str}</span>
                    </p>
                </div>
            </div>""", unsafe_allow_html=True)

        with col_actions:
            uid = int(row["user_id"])
            user_role = str(row.get("role", ""))

            # Owner can deactivate/reactivate anyone except themselves
            # Manager can only deactivate/reactivate Staff
            can_toggle = (
                (role == "Owner" and uid != current_user["user_id"]) or
                (role == "Manager" and user_role == "Staff")
            )

            if can_toggle:
                label = "🔴 Deactivate" if is_active else "🟢 Activate"
                if st.button(label, key=f"toggle_{uid}", use_container_width=True):
                    DatabaseConnection.execute_query(
                        "UPDATE users SET is_active = %s WHERE user_id = %s",
                        (not is_active, uid)
                    )
                    st.success(
                        f"{'Deactivated' if is_active else 'Activated'} "
                        f"**{row['full_name']}**"
                    )
                    st.rerun()


# ── Create account form ───────────────────────────────────────────────────────

def _create_account_form(current_user: dict):
    role = current_user.get("role", "Staff")

    # What roles this user can create
    if role == "Owner":
        allowed_roles = ["Manager", "Staff"]
    elif role == "Manager":
        allowed_roles = ["Staff"]
    else:
        st.error("🔒 You don't have permission to create accounts.")
        return

    st.markdown("### ➕ Create New Account")

    with st.form("create_account_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            full_name = st.text_input(
                "Full Name *", placeholder="e.g. Sharon Mwende")
            username  = st.text_input(
                "Username *",
                placeholder="e.g. sharon_m  (used to log in)",
                help="Lowercase, no spaces. This is what they use to sign in.")
            email     = st.text_input(
                "Email (optional)", placeholder="sharon@gmail.com")
            phone     = st.text_input(
                "Phone (optional)", placeholder="0712 345 678")

        with col2:
            new_role  = st.selectbox("Role *", allowed_roles)
            password  = st.text_input(
                "Password *", type="password",
                placeholder="Min 6 characters",
                help="The staff member will use this to sign in.")
            confirm   = st.text_input(
                "Confirm Password *", type="password",
                placeholder="Re-enter password")

            if new_role == "Manager":
                st.info(
                    "💡 Managers can view Reports, manage Staff accounts, "
                    "and access all pages except owner-only settings.")
            else:
                st.info(
                    "💡 Staff can record sales, manage customers, "
                    "update inventory and log expenses.")

        submitted = st.form_submit_button(
            "💾 Create Account", use_container_width=True, type="primary")

        if submitted:
            # Validation
            if not full_name or not username or not password:
                st.error("Full name, username and password are required.")
                return
            if len(password) < 6:
                st.error("Password must be at least 6 characters.")
                return
            if password != confirm:
                st.error("Passwords do not match.")
                return
            if " " in username:
                st.error("Username cannot contain spaces.")
                return

            # Check username is not taken
            existing = DatabaseConnection.fetch_one(
                "SELECT user_id FROM users WHERE username = %s", (username,))
            if existing:
                st.error(
                    f"Username **{username}** is already taken. "
                    "Please choose a different one.")
                return

            # Create the account
            pw_hash = _hash(password)
            ok = DatabaseConnection.execute_query(
                """INSERT INTO users
                   (username, full_name, email, phone, password_hash, role, is_active)
                   VALUES (%s, %s, %s, %s, %s, %s, TRUE)""",
                (username, full_name, email or None,
                 phone or None, pw_hash, new_role)
            )

            if ok:
                st.success(
                    f"✅ Account created! "
                    f"**{full_name}** can now sign in as "
                    f"**{new_role}** with username `{username}`."
                )
                st.rerun()
            else:
                st.error("Failed to create account. Please try again.")


# ── Reset password ────────────────────────────────────────────────────────────

def _reset_password(current_user: dict):
    role = current_user.get("role", "Staff")

    st.markdown("### 🔑 Reset a Password")
    st.caption(
        "Use this if a staff member forgets their password. "
        "Set a temporary password and ask them to change it after logging in.")

    df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_ALL_STAFF)
    if df is None or df.empty:
        st.info("No accounts found.")
        return

    # Filter who this user can reset
    if role == "Owner":
        eligible = df[df["user_id"] != current_user["user_id"]]
    elif role == "Manager":
        eligible = df[df["role"] == "Staff"]
    else:
        eligible = pd.DataFrame()

    if eligible.empty:
        st.info("No accounts available to reset.")
        return

    user_map = {
        f"{r['full_name']} (@{r['username']}) — {r['role']}": r["user_id"]
        for _, r in eligible.iterrows()
    }

    with st.form("reset_password_form", clear_on_submit=True):
        selected    = st.selectbox("Select Staff Member", list(user_map.keys()))
        new_pass    = st.text_input("New Password *", type="password",
                                    placeholder="Min 6 characters")
        confirm_pass= st.text_input("Confirm New Password *", type="password")

        submitted = st.form_submit_button(
            "🔑 Reset Password", use_container_width=True, type="primary")

        if submitted:
            if not new_pass:
                st.error("Password is required.")
                return
            if len(new_pass) < 6:
                st.error("Password must be at least 6 characters.")
                return
            if new_pass != confirm_pass:
                st.error("Passwords do not match.")
                return

            uid = user_map[selected]
            pw_hash = _hash(new_pass)
            ok = DatabaseConnection.execute_query(
                "UPDATE users SET password_hash = %s WHERE user_id = %s",
                (pw_hash, uid)
            )
            if ok:
                name = selected.split("(")[0].strip()
                st.success(
                    f"✅ Password reset for **{name}**. "
                    "Please share the new password with them securely.")
            else:
                st.error("Failed to reset password.")


# ── Change own password ───────────────────────────────────────────────────────

def _change_own_password(current_user: dict):
    st.markdown("### 🔒 Change My Password")

    with st.form("change_own_pw_form", clear_on_submit=True):
        old_pass  = st.text_input("Current Password *", type="password")
        new_pass  = st.text_input("New Password *", type="password",
                                  placeholder="Min 6 characters")
        conf_pass = st.text_input("Confirm New Password *", type="password")

        submitted = st.form_submit_button(
            "💾 Update Password", use_container_width=True, type="primary")

        if submitted:
            if not old_pass or not new_pass:
                st.error("All fields are required.")
                return
            if len(new_pass) < 6:
                st.error("New password must be at least 6 characters.")
                return
            if new_pass != conf_pass:
                st.error("New passwords do not match.")
                return

            # Verify current password
            row = DatabaseConnection.fetch_one(
                "SELECT password_hash FROM users WHERE user_id = %s",
                (current_user["user_id"],))
            if not row or not AuthenticationManager.verify_password(row[0], old_pass):
                st.error("Current password is incorrect.")
                return

            pw_hash = _hash(new_pass)
            ok = DatabaseConnection.execute_query(
                "UPDATE users SET password_hash = %s WHERE user_id = %s",
                (pw_hash, current_user["user_id"])
            )
            if ok:
                st.success("✅ Password updated! You'll use the new password next time you log in.")
            else:
                st.error("Failed to update password.")


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    AuthenticationManager.require_login()
    _css()

    user = AuthenticationManager.get_current_user()
    if not user:
        st.error("Session expired. Please log in again.")
        st.stop()

    role = user.get("role", "Staff")

    if role == "Staff":
        st.error("🔒 Staff members cannot access account management.")
        st.stop()

    st.markdown("""
    <div style="padding:16px 0 20px 0;border-bottom:1px solid #e2e8f0;margin-bottom:24px;">
        <h1 style="color:#1e293b;margin:0;font-size:26px;font-weight:700;">
            👤 Staff Accounts
        </h1>
        <p style="color:#64748b;margin:4px 0 0 0;font-size:14px;">
            Manage who has access to Glamour Hub and what they can do.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Role capability summary
    if role == "Owner":
        st.markdown("""
        <div style="background:#fdf2f8;border-left:4px solid #ec4899;
                    border-radius:8px;padding:12px 16px;margin-bottom:20px">
            <strong style="color:#9d174d">👑 Owner Access</strong>
            <span style="color:#64748b;font-size:13px;margin-left:8px">
                You can create Manager and Staff accounts, reset any password,
                and deactivate any account except your own.
            </span>
        </div>""", unsafe_allow_html=True)
    elif role == "Manager":
        st.markdown("""
        <div style="background:#f5f3ff;border-left:4px solid #8b5cf6;
                    border-radius:8px;padding:12px 16px;margin-bottom:20px">
            <strong style="color:#6d28d9">🔑 Manager Access</strong>
            <span style="color:#64748b;font-size:13px;margin-left:8px">
                You can create Staff accounts, reset staff passwords,
                and activate/deactivate staff members.
            </span>
        </div>""", unsafe_allow_html=True)

    # Build tabs based on role
    if role == "Owner":
        tab1, tab2, tab3, tab4 = st.tabs([
            "👥 All Accounts",
            "➕ Create Account",
            "🔑 Reset Password",
            "🔒 My Password",
        ])
    else:  # Manager
        tab1, tab2, tab3, tab4 = st.tabs([
            "👥 All Accounts",
            "➕ Add Staff",
            "🔑 Reset Password",
            "🔒 My Password",
        ])

    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        _staff_list(user)

    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        _create_account_form(user)

    with tab3:
        st.markdown("<br>", unsafe_allow_html=True)
        _reset_password(user)

    with tab4:
        st.markdown("<br>", unsafe_allow_html=True)
        _change_own_password(user)


if __name__ == "__main__":
    main()
