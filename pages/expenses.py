"""
Payments & Expenses - Glamour Hub Beauty Business
Track all money coming in (payment breakdown) and going out (expenses).
Gives the owner a clear cash-flow picture.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
from db_connection import DatabaseConnection
from auth import AuthenticationManager
import sql_queries


def kes(v) -> str:
    try:
        f = float(v)
        if f >= 1_000_000: return f"KES {f/1_000_000:.1f}M"
        if f >= 1_000:     return f"KES {f/1_000:.1f}K"
        return f"KES {f:,.0f}"
    except: return "KES 0"

def kes_full(v) -> str:
    try:    return f"KES {float(v):,.2f}"
    except: return "KES 0.00"

def safe(v, d=0.0):
    try:    return float(v)
    except: return d

def fmt_date(v) -> str:
    if v is None: return "—"
    try:
        if hasattr(v,"strftime"): return v.strftime("%d %b %Y")
        return pd.to_datetime(v).strftime("%d %b %Y")
    except: return str(v)


EXPENSE_CATEGORIES = [
    "Rent","Salaries","Utilities","Stock Purchase",
    "Marketing","Equipment","Transport","Other"
]

CAT_ICONS = {
    "Rent":"🏠","Salaries":"👩","Utilities":"💡",
    "Stock Purchase":"📦","Marketing":"📣",
    "Equipment":"🔧","Transport":"🚗","Other":"📌",
}

METHOD_ICON = {"M-Pesa":"📱","Cash":"💵","Bank Transfer":"🏦"}


def _css():
    st.markdown("""
    <style>
    .kpi-mini{background:white;border-radius:10px;padding:14px;
              border-left:4px solid #16a34a;
              box-shadow:0 1px 4px rgba(0,0,0,.05);
              text-align:center;margin-bottom:8px;}
    .exp-card{background:white;border-radius:8px;padding:12px 16px;
              border:1px solid #e2e8f0;margin-bottom:6px;}
    .section{color:#1e293b;font-size:16px;font-weight:600;margin:0 0 12px 0;}
    </style>
    """, unsafe_allow_html=True)


# ── Cash-flow KPIs ────────────────────────────────────────────────────────────

def _cashflow_kpis():
    # Income this month
    month_row = DatabaseConnection.fetch_one(sql_queries.QUERY_THIS_MONTH_SUMMARY)
    revenue   = safe(month_row[1] if month_row else 0)

    # Expenses this month
    exp_row   = DatabaseConnection.fetch_one(sql_queries.QUERY_THIS_MONTH_EXPENSES)
    expenses  = safe(exp_row[0] if exp_row else 0)
    net       = revenue - expenses

    # Payment method breakdown this month
    pm_df = DatabaseConnection.fetch_dataframe(
        sql_queries.QUERY_PAYMENT_METHOD_REPORT)
    mpesa_total = 0
    cash_total  = 0
    if pm_df is not None and not pm_df.empty:
        for _,r in pm_df.iterrows():
            if r["payment_method"] == "M-Pesa":
                mpesa_total = safe(r["total_amount"])
            elif r["payment_method"] == "Cash":
                cash_total  = safe(r["total_amount"])

    c1,c2,c3,c4,c5 = st.columns(5)
    cards = [
        (c1,"Revenue (month)",  kes(revenue),  "#16a34a"),
        (c2,"Expenses (month)", kes(expenses), "#dc2626"),
        (c3,"Net Cash Flow",    kes(net),      "#16a34a" if net>=0 else "#dc2626"),
        (c4,"M-Pesa In",        kes(mpesa_total),"#16a34a"),
        (c5,"Cash In",          kes(cash_total), "#3b82f6"),
    ]
    for col,label,value,color in cards:
        with col:
            st.markdown(f"""
            <div class="kpi-mini" style="border-left-color:{color}">
                <p style="color:#64748b;font-size:11px;text-transform:uppercase;
                          letter-spacing:.5px;margin:0">{label}</p>
                <p style="color:#1e293b;font-size:20px;font-weight:700;
                          margin:5px 0 0 0">{value}</p>
            </div>""", unsafe_allow_html=True)


# ── Income (payment) summary ──────────────────────────────────────────────────

def _income_summary():
    st.markdown('<p class="section">💰 Income by Payment Method (This Month)</p>',
                unsafe_allow_html=True)

    df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_PAYMENT_METHOD_REPORT)
    if df is None or df.empty:
        st.info("No sales this month yet.")
        return

    col1,col2 = st.columns(2)
    colors = {"M-Pesa":"#16a34a","Cash":"#3b82f6",
               "Card":"#f59e0b","Split":"#8b5cf6"}

    with col1:
        fig = go.Figure(go.Pie(
            labels=df["payment_method"],
            values=df["total_amount"],
            hole=0.55,
            marker=dict(
                colors=[colors.get(m,"#94a3b8") for m in df["payment_method"]],
                line=dict(color="white",width=2)),
            textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>KES %{value:,.0f}<extra></extra>",
        ))
        fig.update_layout(
            height=260, paper_bgcolor="white",
            margin=dict(l=0,r=0,t=10,b=0), font=dict(size=11),
            annotations=[dict(text="Income", x=0.5, y=0.5,
                              font_size=13, showarrow=False)],
            showlegend=True,
            legend=dict(orientation="h",y=-0.15),
        )
        st.plotly_chart(fig, use_container_width=True,
                        config={"displayModeBar":False})

    with col2:
        tbl = df.copy()
        tbl["total_amount"] = tbl["total_amount"].apply(kes_full)
        tbl["pct"] = tbl["pct"].apply(lambda x: f"{safe(x):.1f}%")
        tbl.columns = ["Method","Transactions","Amount","Share"]
        st.dataframe(tbl, use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)
        total = df["total_amount"].apply(safe).sum()
        st.markdown(f"""
        <div style="background:#f0fdf4;border-radius:8px;padding:12px 16px;
                    border:1px solid #bbf7d0">
            <strong>Total Income This Month:</strong>
            <span style="color:#16a34a;font-weight:700;font-size:16px;
                          margin-left:8px">{kes_full(total)}</span>
        </div>""", unsafe_allow_html=True)


# ── Add expense ───────────────────────────────────────────────────────────────

def _add_expense_form(user: dict):
    st.markdown("### ➕ Record Expense")

    with st.form("add_expense_form", clear_on_submit=True):
        col1,col2 = st.columns(2)
        with col1:
            category    = st.selectbox("Category *", EXPENSE_CATEGORIES)
            description = st.text_input("Description *",
                                        placeholder="e.g. Monthly rent - November 2026")
            amount      = st.number_input("Amount (KES) *",
                                          min_value=0.0, step=100.0)
        with col2:
            expense_date = st.date_input("Date", value=date.today())
            method       = st.selectbox("Payment Method",
                                        ["Cash","M-Pesa","Bank Transfer"])
            reference    = st.text_input(
                "Reference / Receipt No.",
                placeholder="e.g. M-Pesa ref or receipt number")
            notes        = st.text_area("Notes", height=68)

        submitted = st.form_submit_button(
            "💾 Save Expense", use_container_width=True, type="primary")

        if submitted:
            if not description or amount <= 0:
                st.error("Description and amount are required.")
            else:
                ok = DatabaseConnection.execute_query(
                    sql_queries.QUERY_ADD_EXPENSE,
                    (category, description, amount, expense_date,
                     method, reference or None,
                     user["user_id"], notes or None)
                )
                if ok:
                    st.success(
                        f"✅ Expense recorded: **{category}** — {kes_full(amount)}")
                    st.rerun()
                else:
                    st.error("Failed to save.")


# ── Expense history ───────────────────────────────────────────────────────────

def _expense_history():
    st.markdown('<p class="section">📋 Expense History</p>',
                unsafe_allow_html=True)

    df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_ALL_EXPENSES)
    if df is None or df.empty:
        st.info("No expenses recorded yet.")
        return

    col1,col2,col3 = st.columns(3)
    with col1:
        cat_f = st.selectbox("Category",
                              ["All"] + EXPENSE_CATEGORIES, key="exp_cat")
    with col2:
        method_f = st.selectbox("Method",
                                ["All","Cash","M-Pesa","Bank Transfer"],
                                key="exp_method")
    with col3:
        period = st.selectbox("Period",
                              ["All Time","This Month","Last 30 Days",
                               "Last 90 Days"], key="exp_period")

    df["expense_date"] = pd.to_datetime(df["expense_date"], errors="coerce")
    today = pd.Timestamp.today().normalize()

    if period == "This Month":
        df = df[df["expense_date"].dt.to_period("M") == today.to_period("M")]
    elif period == "Last 30 Days":
        df = df[df["expense_date"] >= today - pd.Timedelta(days=30)]
    elif period == "Last 90 Days":
        df = df[df["expense_date"] >= today - pd.Timedelta(days=90)]

    if cat_f    != "All": df = df[df["category"]       == cat_f]
    if method_f != "All": df = df[df["payment_method"] == method_f]

    if df.empty:
        st.info("No expenses match.")
        return

    total = df["amount"].apply(safe).sum()
    st.markdown(
        f"<div style='background:#fef2f2;border-radius:8px;padding:10px 16px;"
        f"border:1px solid #fecaca;margin-bottom:12px'>"
        f"Total: <strong style='color:#dc2626'>{kes_full(total)}</strong> "
        f"across {len(df)} expense(s)</div>",
        unsafe_allow_html=True)

    for _,r in df.iterrows():
        icon = CAT_ICONS.get(str(r.get("category","")),"📌")
        micon= METHOD_ICON.get(str(r.get("payment_method","")),"💰")
        st.markdown(f"""
        <div class="exp-card">
            <div style="display:flex;justify-content:space-between;align-items:center">
                <div>
                    <span style="font-size:16px">{icon}</span>
                    <strong style="color:#1e293b;margin-left:6px">
                        {r['category']}</strong>
                    <span style="color:#64748b;font-size:12px;margin-left:6px">
                        · {r['description']}</span><br>
                    <span style="color:#64748b;font-size:11px">
                        📅 {fmt_date(r.get('expense_date'))} &nbsp;·&nbsp;
                        {micon} {r.get('payment_method','')}
                        {f" · Ref: {r['reference']}" if r.get('reference') else ""}
                        &nbsp;·&nbsp; By: {r.get('recorded_by','—')}
                    </span>
                </div>
                <strong style="color:#dc2626;font-size:15px">
                    {kes_full(r['amount'])}</strong>
            </div>
        </div>""", unsafe_allow_html=True)


# ── Expense analytics ─────────────────────────────────────────────────────────

def _expense_analytics():
    st.markdown('<p class="section">📊 Expense Breakdown (This Month)</p>',
                unsafe_allow_html=True)

    df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_EXPENSES_THIS_MONTH)
    trend = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_EXPENSE_TREND)

    col1,col2 = st.columns(2)

    with col1:
        if df is not None and not df.empty:
            fig = px.pie(
                df, values="total", names="category",
                title="Expenses by Category",
                color_discrete_sequence=px.colors.qualitative.Set3,
                hole=0.45,
            )
            fig.update_layout(height=280, paper_bgcolor="white",
                               margin=dict(l=0,r=0,t=30,b=0), font=dict(size=11))
            st.plotly_chart(fig, use_container_width=True,
                            config={"displayModeBar":False})

            tbl = df.copy()
            tbl["total"] = tbl["total"].apply(kes_full)
            tbl.columns = ["Category","Total","Transactions"]
            st.dataframe(tbl, use_container_width=True, hide_index=True)
        else:
            st.info("No expenses this month.")

    with col2:
        if trend is not None and not trend.empty:
            trend["label"] = pd.to_datetime(
                trend["month"], errors="coerce").dt.strftime("%b %Y")
            fig2 = px.bar(
                trend, x="label", y="total_expenses",
                title="Monthly Expenses (6 months)",
                color="total_expenses", color_continuous_scale="Reds",
                labels={"label":"Month","total_expenses":"KES"},
            )
            fig2.update_layout(
                height=280, plot_bgcolor="white", paper_bgcolor="white",
                margin=dict(l=0,r=0,t=30,b=0), font=dict(size=11),
                coloraxis_showscale=False, showlegend=False,
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True,gridcolor="#f1f5f9"),
            )
            st.plotly_chart(fig2, use_container_width=True,
                            config={"displayModeBar":False})
        else:
            st.info("Not enough data for trend.")


# ── Cash-flow summary panel ───────────────────────────────────────────────────

def _cashflow_summary():
    st.markdown('<p class="section">💼 Cash-Flow Summary (This Month)</p>',
                unsafe_allow_html=True)

    month_row = DatabaseConnection.fetch_one(sql_queries.QUERY_THIS_MONTH_SUMMARY)
    exp_df    = DatabaseConnection.fetch_dataframe(
        sql_queries.QUERY_EXPENSES_THIS_MONTH)
    profit_row= DatabaseConnection.fetch_one(sql_queries.QUERY_THIS_MONTH_PROFIT)

    revenue  = safe(month_row[1] if month_row else 0)
    cogs     = safe(profit_row[1] if profit_row else 0)
    gross_p  = safe(profit_row[2] if profit_row else 0)
    op_exp   = 0
    if exp_df is not None and not exp_df.empty:
        op_exp = exp_df["total"].apply(safe).sum()
    net_p    = gross_p - op_exp

    rows = [
        ("Revenue",           revenue,  "#16a34a"),
        ("Cost of Goods Sold",cogs,     "#f59e0b"),
        ("Gross Profit",      gross_p,  "#3b82f6"),
        ("Operating Expenses",op_exp,   "#dc2626"),
        ("Net Profit",        net_p,    "#16a34a" if net_p>=0 else "#dc2626"),
    ]

    for label, amount, color in rows:
        bold = "font-weight:700;font-size:15px" if "Profit" in label else ""
        border = f"border-top:2px solid {color}" if "Net" in label else ""
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;
                    padding:8px 16px;background:white;
                    border-radius:6px;border:1px solid #e2e8f0;
                    margin-bottom:4px;{border}">
            <span style="color:#1e293b;{bold}">{label}</span>
            <span style="color:{color};{bold}">{kes_full(amount)}</span>
        </div>""", unsafe_allow_html=True)


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    AuthenticationManager.require_login()
    _css()

    user = AuthenticationManager.get_current_user()
    if not user:
        st.error("Session expired."); st.stop()
    if user.get("role") not in ("Owner", "Manager"):
        st.error("Only the Owner or Manager can access expenses.")
        st.stop()

    st.markdown("""
    <div style="padding:16px 0 20px 0;border-bottom:1px solid #e2e8f0;
                margin-bottom:24px;">
        <h1 style="color:#1e293b;margin:0;font-size:26px;font-weight:700;">
            💼 Payments & Expenses
        </h1>
        <p style="color:#64748b;margin:4px 0 0 0;font-size:14px;">
            Track all money in and out. Know your real profit at a glance.
        </p>
    </div>
    """, unsafe_allow_html=True)

    _cashflow_kpis()
    st.markdown("<br>", unsafe_allow_html=True)

    tab1,tab2,tab3,tab4 = st.tabs([
        "💼 Cash-Flow Summary",
        "💰 Income Breakdown",
        "➕ Record Expense",
        "📋 Expense History",
    ])

    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        _cashflow_summary()
        st.markdown("---")
        _expense_analytics()

    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        _income_summary()

    with tab3:
        st.markdown("<br>", unsafe_allow_html=True)
        _add_expense_form(user)

    with tab4:
        st.markdown("<br>", unsafe_allow_html=True)
        _expense_history()


if __name__ == "__main__":
    main()
