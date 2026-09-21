"""
Reports - Glamour Hub Beauty Business
Profit/Loss, best sellers, staff performance, payment analytics.
Owner-focused: clear numbers, no jargon.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
        if hasattr(v,"strftime"): return v.strftime("%b %Y")
        return pd.to_datetime(v).strftime("%b %Y")
    except: return str(v)


def _css():
    st.markdown("""
    <style>
    .kpi-mini{background:white;border-radius:10px;padding:14px;
              border-left:4px solid #3b82f6;
              box-shadow:0 1px 4px rgba(0,0,0,.05);
              text-align:center;margin-bottom:8px;}
    .section{color:#1e293b;font-size:16px;font-weight:600;margin:0 0 12px 0;}
    </style>
    """, unsafe_allow_html=True)


# ── Profit & Loss ─────────────────────────────────────────────────────────────

def _profit_loss():
    st.markdown('<p class="section">📊 Profit & Loss — Last 6 Months</p>',
                unsafe_allow_html=True)

    df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_PROFIT_LOSS)
    if df is None or df.empty:
        st.info("Not enough data yet.")
        return

    df["label"]       = pd.to_datetime(df["month"], errors="coerce").dt.strftime("%b %Y")
    df["net_profit"]  = df["net_profit"].apply(safe)
    df["gross_profit"]= df["gross_profit"].apply(safe)
    df["revenue"]     = df["revenue"].apply(safe)
    df["cogs"]        = df["cogs"].apply(safe)
    df["operating_expenses"] = df["operating_expenses"].apply(safe)

    # Bar chart
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["label"], y=df["revenue"],
                         name="Revenue", marker_color="#3b82f6",
                         hovertemplate="Revenue: KES %{y:,.0f}<extra></extra>"))
    fig.add_trace(go.Bar(x=df["label"], y=df["cogs"],
                         name="COGS", marker_color="#f59e0b",
                         hovertemplate="COGS: KES %{y:,.0f}<extra></extra>"))
    fig.add_trace(go.Bar(x=df["label"], y=df["operating_expenses"],
                         name="Expenses", marker_color="#dc2626",
                         hovertemplate="Expenses: KES %{y:,.0f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=df["label"], y=df["net_profit"],
                             name="Net Profit", mode="lines+markers",
                             line=dict(color="#16a34a",width=3),
                             marker=dict(size=8),
                             hovertemplate="Net Profit: KES %{y:,.0f}<extra></extra>"))
    fig.update_layout(
        height=340, barmode="group",
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=0,r=0,t=10,b=0), font=dict(size=11),
        legend=dict(orientation="h",y=1.1,x=1,xanchor="right"),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True,gridcolor="#f1f5f9",title="KES"),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True,
                    config={"displayModeBar":False})

    # P&L table
    disp = df[["label","revenue","cogs","gross_profit",
               "operating_expenses","net_profit"]].copy()
    for col in ["revenue","cogs","gross_profit","operating_expenses","net_profit"]:
        disp[col] = disp[col].apply(kes_full)
    disp.columns = ["Month","Revenue","COGS","Gross Profit","Expenses","Net Profit"]
    st.dataframe(disp, use_container_width=True, hide_index=True)

    # Summary
    total_rev = df["revenue"].sum()
    total_net = df["net_profit"].sum()
    avg_margin = (total_net / total_rev * 100) if total_rev else 0
    m1,m2,m3 = st.columns(3)
    m1.metric("6-Month Revenue", kes(total_rev))
    m2.metric("6-Month Net Profit", kes(total_net))
    m3.metric("Avg Net Margin", f"{avg_margin:.1f}%")


# ── Best sellers ──────────────────────────────────────────────────────────────

def _best_sellers():
    st.markdown('<p class="section">🏆 Best Selling Products (Last 30 Days)</p>',
                unsafe_allow_html=True)

    df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_BEST_SELLERS)
    if df is None or df.empty:
        st.info("No sales data yet.")
        return

    col1,col2 = st.columns([3,2])

    with col1:
        fig = px.bar(
            df.head(10), x="name", y="units_sold",
            color="profit", color_continuous_scale="Greens",
            text="units_sold",
            labels={"name":"Product","units_sold":"Units Sold"},
            title="Top 10 by Units Sold",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            height=320, plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(l=0,r=0,t=30,b=0), font=dict(size=11),
            coloraxis_showscale=False, showlegend=False,
            xaxis=dict(showgrid=False, tickangle=-25),
            yaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
        )
        st.plotly_chart(fig, use_container_width=True,
                        config={"displayModeBar":False})

    with col2:
        tbl = df.copy()
        tbl["revenue"] = tbl["revenue"].apply(kes)
        tbl["profit"]  = tbl["profit"].apply(kes)
        tbl = tbl[["name","brand","units_sold","revenue","profit"]]
        tbl.columns = ["Product","Brand","Units","Revenue","Profit"]
        st.dataframe(tbl, use_container_width=True, hide_index=True)

    # Category breakdown
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="section">📦 Sales by Category (Last 30 Days)</p>',
                unsafe_allow_html=True)
    cat_df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_CATEGORY_SALES)
    if cat_df is not None and not cat_df.empty:
        col3,col4 = st.columns(2)
        with col3:
            fig2 = px.pie(
                cat_df[cat_df["revenue"]>0],
                values="revenue", names="category",
                title="Revenue by Category",
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig2.update_layout(height=260, paper_bgcolor="white",
                               margin=dict(l=0,r=0,t=30,b=0), font=dict(size=11))
            st.plotly_chart(fig2, use_container_width=True,
                            config={"displayModeBar":False})
        with col4:
            tbl2 = cat_df.copy()
            tbl2["revenue"] = tbl2["revenue"].apply(kes)
            tbl2["profit"]  = tbl2["profit"].apply(kes)
            tbl2 = tbl2[["category","transactions","units_sold","revenue","profit"]]
            tbl2.columns = ["Category","Transactions","Units","Revenue","Profit"]
            st.dataframe(tbl2, use_container_width=True, hide_index=True)


# ── Staff performance ─────────────────────────────────────────────────────────

def _staff_performance():
    st.markdown('<p class="section">👩 Staff Performance (Last 30 Days)</p>',
                unsafe_allow_html=True)

    df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_STAFF_PERFORMANCE)
    if df is None or df.empty:
        st.info("No staff data available.")
        return

    for rank,(_,r) in enumerate(df.iterrows(),1):
        medal = {1:"🥇",2:"🥈",3:"🥉"}.get(rank,f"#{rank}")
        revenue = safe(r.get("revenue",0))
        avg_sale= safe(r.get("avg_sale",0))
        discs   = safe(r.get("discounts_given",0))
        sales   = int(safe(r.get("sales_count",0)))
        days    = int(safe(r.get("days_worked",0)))
        daily   = (revenue/days) if days else 0

        st.markdown(f"""
        <div style="background:white;border-radius:10px;padding:14px 18px;
                    border:1px solid #e2e8f0;margin-bottom:8px;">
            <div style="display:flex;justify-content:space-between;align-items:center">
                <div>
                    <span style="font-size:18px">{medal}</span>
                    <strong style="color:#1e293b;margin-left:8px;font-size:15px">
                        {r.get('full_name','')}</strong>
                    <span style="color:#64748b;font-size:12px;margin-left:6px">
                        · {r.get('role','')}</span>
                </div>
                <span style="color:#16a34a;font-weight:700;font-size:16px">
                    {kes(revenue)}</span>
            </div>
            <div style="display:grid;grid-template-columns:repeat(4,1fr);
                        gap:8px;margin-top:10px">
                <div style="text-align:center;background:#f8fafc;
                            border-radius:6px;padding:6px">
                    <p style="color:#64748b;font-size:10px;margin:0">SALES</p>
                    <p style="color:#3b82f6;font-weight:700;margin:2px 0">
                        {sales}</p>
                </div>
                <div style="text-align:center;background:#f8fafc;
                            border-radius:6px;padding:6px">
                    <p style="color:#64748b;font-size:10px;margin:0">AVG SALE</p>
                    <p style="color:#1e293b;font-weight:700;margin:2px 0">
                        {kes(avg_sale)}</p>
                </div>
                <div style="text-align:center;background:#f8fafc;
                            border-radius:6px;padding:6px">
                    <p style="color:#64748b;font-size:10px;margin:0">DISCOUNTS</p>
                    <p style="color:#f59e0b;font-weight:700;margin:2px 0">
                        {kes(discs)}</p>
                </div>
                <div style="text-align:center;background:#f8fafc;
                            border-radius:6px;padding:6px">
                    <p style="color:#64748b;font-size:10px;margin:0">DAILY AVG</p>
                    <p style="color:#16a34a;font-weight:700;margin:2px 0">
                        {kes(daily)}</p>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    if len(df) >= 2:
        fig = px.bar(
            df, x="full_name", y="revenue",
            color="revenue", color_continuous_scale="Teal",
            text="sales_count",
            labels={"full_name":"Staff","revenue":"Revenue (KES)"},
            title="Revenue Generated per Staff Member",
        )
        fig.update_traces(
            texttemplate="%{text} sales", textposition="outside")
        fig.update_layout(
            height=280, plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(l=0,r=0,t=30,b=0), font=dict(size=11),
            coloraxis_showscale=False, showlegend=False,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True,gridcolor="#f1f5f9"),
        )
        st.plotly_chart(fig, use_container_width=True,
                        config={"displayModeBar":False})


# ── Attendance history ────────────────────────────────────────────────────────

def _attendance():
    st.markdown('<p class="section">🕐 Staff Attendance (Last 30 Days)</p>',
                unsafe_allow_html=True)

    df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_ATTENDANCE_HISTORY)
    if df is None or df.empty:
        st.info("No attendance records yet.")
        return

    df["check_in"]  = df["check_in"].apply(
        lambda v: str(v)[:5] if v is not None else "—")
    df["check_out"] = df["check_out"].apply(
        lambda v: str(v)[:5] if v is not None else "Still in")
    df["hours_worked"] = df["hours_worked"].apply(
        lambda v: str(v)[:5] if v is not None else "—")
    df["work_date"] = df["work_date"].apply(fmt_date)
    df.columns = ["Staff","Date","Check In","Check Out","Hours"]
    st.dataframe(df, use_container_width=True, hide_index=True)


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    AuthenticationManager.require_login()
    _css()

    user = AuthenticationManager.get_current_user()
    if not user:
        st.error("Session expired."); st.stop()

    # Only owner/manager can see reports
    if user.get("role") not in ("Owner","Manager"):
        st.error("🔒 Reports are only available to the Owner and Manager.")
        st.stop()

    st.markdown("""
    <div style="padding:16px 0 20px 0;border-bottom:1px solid #e2e8f0;
                margin-bottom:24px;">
        <h1 style="color:#1e293b;margin:0;font-size:26px;font-weight:700;">
            📈 Reports & Analytics
        </h1>
        <p style="color:#64748b;margin:4px 0 0 0;font-size:14px;">
            Profit & Loss, best sellers, staff performance and more.
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab1,tab2,tab3,tab4 = st.tabs([
        "📊 Profit & Loss",
        "🏆 Best Sellers",
        "👩 Staff Performance",
        "🕐 Attendance",
    ])

    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        _profit_loss()

    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        _best_sellers()

    with tab3:
        st.markdown("<br>", unsafe_allow_html=True)
        _staff_performance()

    with tab4:
        st.markdown("<br>", unsafe_allow_html=True)
        _attendance()


if __name__ == "__main__":
    main()
