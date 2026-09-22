"""
Owner Dashboard - Glamour Hub Beauty Business
Remote monitoring: see everything happening in your shop in real time.
Refreshes every 60 seconds automatically.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date
from db_connection import DatabaseConnection
from auth import AuthenticationManager
import sql_queries

# ── auto-refresh every 60 s ───────────────────────────────────────────────────
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=60_000, key="dash_refresh")
except ImportError:
    pass   # works fine without it; owner can manually refresh


# ── helpers ───────────────────────────────────────────────────────────────────

def kes(v) -> str:
    try:
        f = float(v)
        if f >= 1_000_000: return f"KES {f/1_000_000:.1f}M"
        if f >= 1_000:     return f"KES {f/1_000:.1f}K"
        return f"KES {f:,.0f}"
    except: return "KES 0"

def safe(v, default=0.0):
    try:    return float(v)
    except: return default

def fmt_time(v) -> str:
    if v is None: return "—"
    try:
        if hasattr(v,"strftime"): return v.strftime("%H:%M")
        return str(v)[:5]
    except: return str(v)

def pct_change(today, yesterday):
    try:
        t, y = float(today), float(yesterday)
        if y == 0: return None
        return round((t - y) / y * 100, 1)
    except: return None


# ── CSS ───────────────────────────────────────────────────────────────────────

def _css():
    st.markdown("""
    <style>
    .kpi { background:white; border-radius:12px; padding:20px 22px;
           box-shadow:0 2px 8px rgba(0,0,0,.07); margin-bottom:8px; }
    .kpi-label  { color:#64748b; font-size:11px; text-transform:uppercase;
                  letter-spacing:.6px; margin:0; }
    .kpi-value  { color:#1e293b; font-size:26px; font-weight:700;
                  margin:6px 0 2px 0; }
    .kpi-sub    { font-size:12px; margin:0; }
    .up         { color:#16a34a; }
    .down       { color:#dc2626; }
    .neutral    { color:#64748b; }
    .alert-card { background:#fef2f2; border-left:4px solid #dc2626;
                  border-radius:8px; padding:12px 16px; margin-bottom:8px; }
    .warn-card  { background:#fffbeb; border-left:4px solid #f59e0b;
                  border-radius:8px; padding:12px 16px; margin-bottom:8px; }
    .good-card  { background:#f0fdf4; border-left:4px solid #16a34a;
                  border-radius:8px; padding:12px 16px; margin-bottom:8px; }
    .info-card  { background:#eff6ff; border-left:4px solid #3b82f6;
                  border-radius:8px; padding:12px 16px; margin-bottom:8px; }
    .section    { color:#1e293b; font-size:16px; font-weight:600;
                  margin:0 0 12px 0; }
    .staff-row  { background:white; border-radius:8px; padding:12px 16px;
                  border:1px solid #e2e8f0; margin-bottom:6px;
                  display:flex; justify-content:space-between; }
    .dot-green  { display:inline-block; width:8px; height:8px;
                  border-radius:50%; background:#16a34a; margin-right:6px; }
    .dot-grey   { display:inline-block; width:8px; height:8px;
                  border-radius:50%; background:#94a3b8; margin-right:6px; }
    </style>
    """, unsafe_allow_html=True)


def _kpi(label, value, sub="", border="#16a34a", sub_cls="neutral"):
    st.markdown(f"""
    <div class="kpi" style="border-left:4px solid {border}">
        <p class="kpi-label">{label}</p>
        <p class="kpi-value">{value}</p>
        <p class="kpi-sub {sub_cls}">{sub}</p>
    </div>""", unsafe_allow_html=True)


# ── sections ──────────────────────────────────────────────────────────────────

def _today_kpis():
    today   = DatabaseConnection.fetch_one(sql_queries.QUERY_TODAY_SUMMARY)
    profit  = DatabaseConnection.fetch_one(sql_queries.QUERY_TODAY_PROFIT)
    yest    = DatabaseConnection.fetch_one(sql_queries.QUERY_YESTERDAY_REVENUE)
    month   = DatabaseConnection.fetch_one(sql_queries.QUERY_THIS_MONTH_SUMMARY)
    expenses= DatabaseConnection.fetch_one(sql_queries.QUERY_THIS_MONTH_EXPENSES)

    txns    = int(safe(today[0] if today else 0))
    revenue = safe(today[1] if today else 0)
    yest_rev= safe(yest[0]   if yest  else 0)
    gp      = safe(profit[2] if profit else 0)
    m_rev   = safe(month[1]  if month  else 0)
    m_exp   = safe(expenses[0] if expenses else 0)
    net     = m_rev - m_exp

    rev_delta = pct_change(revenue, yest_rev)
    rev_sub   = (f"{'▲' if rev_delta>=0 else '▼'} {abs(rev_delta):.1f}% vs yesterday"
                 if rev_delta is not None else "No sales yesterday")
    rev_cls   = "up" if (rev_delta or 0) >= 0 else "down"

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    with c1: _kpi("Today's Sales",     kes(revenue), rev_sub,        "#16a34a", rev_cls)
    with c2: _kpi("Transactions",      str(txns),    "today",        "#3b82f6", "neutral")
    with c3: _kpi("Gross Profit Today",kes(gp),      "after product cost","#8b5cf6","up" if gp>0 else "down")
    with c4: _kpi("Month Revenue",     kes(m_rev),   f"{month[1] if month else 0:.0f} KES","#0ea5e9","neutral")
    with c5: _kpi("Month Expenses",    kes(m_exp),   "recorded costs","#f59e0b","down" if m_exp>0 else "neutral")
    with c6: _kpi("Net Profit (month)",kes(net),     "revenue − expenses","#16a34a" if net>=0 else "#dc2626","up" if net>=0 else "down")


def _stock_alerts():
    st.markdown('<p class="section">🚨 Stock Alerts</p>', unsafe_allow_html=True)
    low   = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_LOW_STOCK)
    oosq  = DatabaseConnection.fetch_one(sql_queries.QUERY_OUT_OF_STOCK)
    oos   = int(safe(oosq[0] if oosq else 0))

    if low is None or low.empty:
        st.markdown('<div class="good-card">✅ All products are well stocked!</div>',
                    unsafe_allow_html=True)
        return

    out   = low[low["qty_in_stock"] == 0]
    warn  = low[low["qty_in_stock"] >  0]

    if not out.empty:
        st.markdown(f'<div class="alert-card">🔴 <strong>{len(out)} product(s) OUT OF STOCK</strong> — '
                f'sales may be interrupted until restocked.</div>', unsafe_allow_html=True)
    if not warn.empty:
        st.markdown(f'<div class="warn-card">🟡 <strong>{len(warn)} product(s) running low</strong> — '
                    f'restock soon.</div>', unsafe_allow_html=True)

    for _, row in low.iterrows():
        qty   = int(row["qty_in_stock"])
        color = "#dc2626" if qty == 0 else "#f59e0b"
        label = "OUT OF STOCK" if qty == 0 else f"Only {qty} left"
        st.markdown(f"""
        <div style="background:white;border-radius:8px;padding:10px 14px;
                    border-left:3px solid {color};border:1px solid #e2e8f0;
                    margin-bottom:6px;display:flex;justify-content:space-between">
            <div>
                <strong style="color:#1e293b">{row['name']}</strong>
                <span style="color:#64748b;font-size:12px"> · {row.get('brand','') or ''}</span><br>
                <span style="color:#64748b;font-size:12px">{row.get('category','')}</span>
            </div>
            <div style="text-align:right">
                <span style="color:{color};font-weight:700">{label}</span><br>
                <span style="color:#64748b;font-size:12px">
                    Reorder: {int(row['reorder_qty'])} units
                </span>
            </div>
        </div>""", unsafe_allow_html=True)


def _staff_status():
    st.markdown('<p class="section">👥 Staff Activity Today</p>', unsafe_allow_html=True)
    df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_STAFF_TODAY)
    if df is None or df.empty:
        st.info("No staff data available.")
        return

    for _, row in df.iterrows():
        checked_in  = row.get("check_in")  is not None and str(row.get("check_in","")) not in ("","None","NaT")
        checked_out = row.get("check_out") is not None and str(row.get("check_out","")) not in ("","None","NaT")
        dot  = "dot-green" if (checked_in and not checked_out) else "dot-grey"
        status_txt  = (
            f"✅ In since {fmt_time(row.get('check_in'))}" if checked_in and not checked_out
            else f"Left at {fmt_time(row.get('check_out'))}" if checked_out
            else "Not checked in"
        )
        sales_made  = int(safe(row.get("sales_made",0)))
        revenue     = safe(row.get("revenue_generated",0))

        st.markdown(f"""
        <div style="background:white;border-radius:8px;padding:12px 16px;
                    border:1px solid #e2e8f0;margin-bottom:6px;">
            <div style="display:flex;justify-content:space-between;align-items:center">
                <div>
                    <span class="{dot}"></span>
                    <strong style="color:#1e293b">{row['full_name']}</strong>
                    <span style="color:#64748b;font-size:12px"> · {row.get('role','')}</span>
                </div>
                <span style="color:#64748b;font-size:12px">{status_txt}</span>
            </div>
            <div style="margin-top:6px;display:flex;gap:20px">
                <span style="font-size:12px;color:#3b82f6">
                    🛍 {sales_made} sale(s)
                </span>
                <span style="font-size:12px;color:#16a34a;font-weight:600">
                    {kes(revenue)}
                </span>
            </div>
        </div>""", unsafe_allow_html=True)


def _revenue_chart():
    st.markdown('<p class="section">📈 Revenue — Last 7 Days</p>', unsafe_allow_html=True)
    df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_LAST_7_DAYS)
    if df is None or df.empty:
        st.info("No sales data yet.")
        return

    df["sale_date"] = pd.to_datetime(df["sale_date"], errors="coerce")
    df["label"]     = df["sale_date"].dt.strftime("%a %d %b")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["label"], y=df["revenue"],
        marker_color="#3b82f6",
        hovertemplate="<b>%{x}</b><br>KES %{y:,.0f}<extra></extra>",
        name="Revenue",
    ))
    fig.add_trace(go.Scatter(
        x=df["label"], y=df["txn_count"],
        mode="lines+markers", yaxis="y2",
        line=dict(color="#f59e0b", width=2),
        marker=dict(size=7),
        name="Transactions",
        hovertemplate="%{y} txns<extra></extra>",
    ))
    fig.update_layout(
        height=280, plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=0,r=0,t=10,b=0), font=dict(size=11,color="#1e293b"),
        yaxis=dict(title="KES", showgrid=True, gridcolor="#f1f5f9"),
        yaxis2=dict(title="Transactions", overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h", y=1.05, x=1, xanchor="right"),
        xaxis=dict(showgrid=False), hovermode="x unified",
        bargap=0.4,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})


def _hourly_chart():
    st.markdown('<p class="section">🕐 Sales by Hour (Today)</p>', unsafe_allow_html=True)
    df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_HOURLY_SALES_TODAY)
    if df is None or df.empty:
        st.info("No sales recorded today yet.")
        return

    # Fill all hours 8-20
    all_hours = pd.DataFrame({"hour_of_day": range(8, 21)})
    df = all_hours.merge(df, on="hour_of_day", how="left").fillna(0)
    df["label"] = df["hour_of_day"].apply(
        lambda h: f"{h:02d}:00")

    peak_hour = int(df.loc[df["revenue"].idxmax(), "hour_of_day"]) if df["revenue"].sum() > 0 else None
    if peak_hour:
        st.markdown(
            f'<div class="info-card">🔥 Peak hour today: <strong>{peak_hour:02d}:00</strong></div>',
            unsafe_allow_html=True)

    fig = px.bar(
        df, x="label", y="revenue",
        color="revenue", color_continuous_scale="Blues",
        labels={"label":"Hour","revenue":"KES"},
    )
    fig.update_layout(
        height=220, plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=0,r=0,t=10,b=0), font=dict(size=11),
        xaxis=dict(showgrid=False), yaxis=dict(showgrid=True,gridcolor="#f1f5f9"),
        coloraxis_showscale=False, showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})


def _payment_methods_today():
    st.markdown('<p class="section">💳 Payment Methods Today</p>', unsafe_allow_html=True)
    df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_TODAY_PAYMENT_METHODS)
    if df is None or df.empty:
        st.info("No payments yet today.")
        return

    colors = {"M-Pesa":"#16a34a","Cash":"#3b82f6","Card":"#f59e0b","Split":"#8b5cf6"}
    fig = go.Figure(go.Pie(
        labels=df["payment_method"], values=df["total_amount"],
        hole=0.55,
        marker=dict(
            colors=[colors.get(m,"#94a3b8") for m in df["payment_method"]],
            line=dict(color="white",width=2)),
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>KES %{value:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        height=240, paper_bgcolor="white",
        margin=dict(l=0,r=0,t=10,b=0), font=dict(size=11),
        annotations=[dict(text="Today", x=0.5, y=0.5,
                          font_size=13, showarrow=False)],
        showlegend=True,
        legend=dict(orientation="h", y=-0.1),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})


def _recent_transactions():
    st.markdown('<p class="section">🧾 Recent Transactions</p>', unsafe_allow_html=True)
    df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_RECENT_SALES)
    if df is None or df.empty:
        st.info("No transactions today yet.")
        return

    for _, row in df.iterrows():
        method = str(row.get("payment_method",""))
        icons  = {"M-Pesa":"📱","Cash":"💵","Card":"💳","Split":"🔀"}
        icon   = icons.get(method,"💰")
        ref    = f" · Ref: {row['mpesa_ref']}" if row.get("mpesa_ref") else ""
        st.markdown(f"""
        <div style="background:white;border-radius:8px;padding:10px 14px;
                    border:1px solid #e2e8f0;margin-bottom:5px;
                    display:flex;justify-content:space-between;align-items:center">
            <div>
                <strong style="color:#1e293b">Transaction #{row.get('sale_id','—')}</strong>
                <span style="color:#64748b;font-size:11px">
                 · {fmt_time(row.get('sale_time'))}
                 · {row.get('served_by','')}
                </span>
            </div>
            <div style="text-align:right">
                <span style="color:#16a34a;font-weight:700">
                    {kes(row.get('total_amount',0))}
                </span><br>
                <span style="color:#64748b;font-size:11px">
                    {icon} {method}{ref}
                </span>
            </div>
        </div>""", unsafe_allow_html=True)


def _monthly_trend():
    st.markdown('<p class="section">📊 Monthly Revenue (12 months)</p>',
                unsafe_allow_html=True)
    df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_MONTHLY_TREND)
    if df is None or df.empty:
        st.info("Not enough data yet.")
        return

    df["label"] = pd.to_datetime(df["month"], errors="coerce").dt.strftime("%b %Y")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["label"], y=df["revenue"],
        marker_color="#3b82f6", name="Revenue",
        hovertemplate="<b>%{x}</b><br>KES %{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        height=260, plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=0,r=0,t=10,b=0), font=dict(size=11),
        xaxis=dict(showgrid=False,tickangle=-30),
        yaxis=dict(showgrid=True,gridcolor="#f1f5f9",title="KES"),
        bargap=0.3, showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    AuthenticationManager.require_login()
    _css()

    user = AuthenticationManager.get_current_user()
    if not user:
        st.error("Session expired. Please log in again.")
        st.stop()

    role = user.get("role", "Staff")
    now  = datetime.now()
    greeting = (
        "Good morning" if now.hour < 12
        else "Good afternoon" if now.hour < 17
        else "Good evening"
    )

    # ── Staff gets a completely different, privacy-respecting dashboard ──
    if role == "Staff":
        _staff_dashboard(user, now, greeting)
        return

    # ── Owner / Manager: full business dashboard ──
    st.markdown(f"""
    <div style="padding:16px 0 20px 0;border-bottom:1px solid #e2e8f0;margin-bottom:24px;">
        <h1 style="color:#1e293b;margin:0;font-size:26px;font-weight:700;">
            💄 Glamour Hub — Business Dashboard
        </h1>
        <p style="color:#64748b;margin:4px 0 0 0;font-size:14px;">
            {greeting}, <strong>{user.get('full_name','')}</strong> &nbsp;·&nbsp;
            {now.strftime('%A, %d %B %Y')} &nbsp;·&nbsp; {now.strftime('%I:%M %p')}
            &nbsp;·&nbsp;
            <span style="color:#16a34a">● Live</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

    _today_kpis()
    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs([
        "📊 Today's Overview",
        "📈 Trends",
        "🚨 Alerts & Staff",
    ])

    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        col_left, col_right = st.columns([3, 2])
        with col_left:
            _revenue_chart()
            st.markdown("<br>", unsafe_allow_html=True)
            _recent_transactions()
        with col_right:
            _hourly_chart()
            st.markdown("<br>", unsafe_allow_html=True)
            _payment_methods_today()

    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        _monthly_trend()

        st.markdown('<p class="section">📅 Daily Revenue — Last 30 Days</p>',
                    unsafe_allow_html=True)
        df30 = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_LAST_30_DAYS)
        if df30 is not None and not df30.empty:
            df30["sale_date"] = pd.to_datetime(df30["sale_date"], errors="coerce")
            fig2 = px.area(
                df30, x="sale_date", y="revenue",
                labels={"sale_date":"Date","revenue":"KES"},
                color_discrete_sequence=["#3b82f6"],
            )
            fig2.update_traces(fill="tozeroy", line=dict(width=2))
            fig2.update_layout(
                height=250, plot_bgcolor="white", paper_bgcolor="white",
                margin=dict(l=0,r=0,t=10,b=0), font=dict(size=11),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True,gridcolor="#f1f5f9",title="KES"),
                showlegend=False,
            )
            st.plotly_chart(fig2, use_container_width=True,
                            config={"displayModeBar":False})

    with tab3:
        st.markdown("<br>", unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        with col_a:
            _stock_alerts()
        with col_b:
            _staff_status()


# ── Staff-only dashboard ──────────────────────────────────────────────────────

def _staff_dashboard(user: dict, now: datetime, greeting: str):
    """
    Stripped dashboard shown to Staff only.
    No revenue totals, no profit, no stock info, no other staff data.
    Just: their own sales today, payment method breakdown of THEIR sales,
    and check-in / check-out.
    """
    uid = user["user_id"]

    st.markdown(f"""
    <div style="padding:16px 0 20px 0;border-bottom:1px solid #e2e8f0;margin-bottom:24px;">
        <h1 style="color:#1e293b;margin:0;font-size:26px;font-weight:700;">
            👋 {greeting}, {user.get('full_name','').split()[0]}
        </h1>
        <p style="color:#64748b;margin:4px 0 0 0;font-size:14px;">
            {now.strftime('%A, %d %B %Y')} &nbsp;·&nbsp; {now.strftime('%I:%M %p')}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Check-in status banner ──
    att = DatabaseConnection.fetch_one(
        sql_queries.QUERY_MY_ATTENDANCE_TODAY, (uid,))
    check_in  = att[0] if att else None
    check_out = att[1] if att else None

    def _fmt_t(v):
        if v is None: return "—"
        try:
            if hasattr(v,"strftime"): return v.strftime("%H:%M")
            return str(v)[:5]
        except: return str(v)

    if check_in and not check_out:
        st.markdown(
            f'<div class="good-card">✅ You checked in at <strong>{_fmt_t(check_in)}</strong>. '
            f'Have a great shift!</div>',
            unsafe_allow_html=True)
    elif check_in and check_out:
        st.markdown(
            f'<div class="info-card">You worked today: '
            f'{_fmt_t(check_in)} — {_fmt_t(check_out)}</div>',
            unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="warn-card">⚠️ You haven\'t checked in yet today. '
            'Go to <strong>Sales / POS → Check-In</strong> to clock in.</div>',
            unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── My sales today ──
    my_sales_df = DatabaseConnection.fetch_dataframe(
        sql_queries.QUERY_MY_SALES_TODAY, params=(uid,))

    my_count   = len(my_sales_df) if my_sales_df is not None else 0
    my_total   = my_sales_df["total_amount"].apply(safe).sum() if my_sales_df is not None and not my_sales_df.empty else 0
    total_items = 0
    if my_sales_df is not None and not my_sales_df.empty and "items_sold" in my_sales_df.columns:
        total_items = int(my_sales_df["items_sold"].apply(safe).sum())

    # KPI cards — my own counts + my own collected amount
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="kpi" style="border-left:4px solid #3b82f6">
            <p class="kpi-label">My Sales Today</p>
            <p class="kpi-value">{my_count}</p>
            <p class="kpi-sub neutral">transactions</p>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi" style="border-left:4px solid #16a34a">
            <p class="kpi-label">My Total Collected</p>
            <p class="kpi-value">{kes(my_total)}</p>
            <p class="kpi-sub neutral">from my sales today</p>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="kpi" style="border-left:4px solid #ec4899">
            <p class="kpi-label">Items Sold</p>
            <p class="kpi-value">{total_items}</p>
            <p class="kpi-sub neutral">product units today</p>
        </div>""", unsafe_allow_html=True)
    with c4:
        # Time on shift
        duration = "—"
        if check_in and not check_out:
            try:
                from datetime import datetime as dt
                ci    = check_in if hasattr(check_in,"hour") else dt.strptime(str(check_in)[:5],"%H:%M").time()
                ci_dt = dt.combine(datetime.today().date(), ci)
                mins  = int((datetime.now() - ci_dt).total_seconds() / 60)
                hours = mins // 60
                duration = f"{hours}h {mins % 60}m" if hours else f"{mins}m"
            except Exception:
                pass
        st.markdown(f"""
        <div class="kpi" style="border-left:4px solid #8b5cf6">
            <p class="kpi-label">Time on Shift</p>
            <p class="kpi-value">{duration}</p>
            <p class="kpi-sub neutral">since check-in</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── My sales list — WITH amounts ──
    st.markdown('<p class="section">🧾 My Sales Today</p>', unsafe_allow_html=True)

    if my_sales_df is None or my_sales_df.empty:
        st.info("No sales recorded yet today. Head to Sales / POS to start.")
    else:
        def _fmt_time(v):
            if v is None: return ""
            try:
                if hasattr(v,"strftime"): return v.strftime("%H:%M")
                return str(v)[:5]
            except: return str(v)

        for _, row in my_sales_df.iterrows():
            icons  = {"M-Pesa":"📱","Cash":"💵","Card":"💳","Split":"🔀"}
            icon   = icons.get(str(row.get("payment_method","")),"💰")
            mpesa  = f" · {row['mpesa_ref']}" if row.get("mpesa_ref") else ""
            amount = safe(row.get("total_amount", 0))
            items  = int(safe(row.get("items_sold", 0)))
            st.markdown(f"""
            <div style="background:white;border-radius:8px;padding:12px 16px;
                        border:1px solid #e2e8f0;margin-bottom:6px;
                        display:flex;justify-content:space-between;align-items:center">
                <div>
                    <strong style="color:#1e293b">Sale #{row['sale_id']}</strong>
                    <span style="color:#64748b;font-size:12px">
                        &nbsp;·&nbsp; {_fmt_time(row.get('sale_time'))}
                        &nbsp;·&nbsp; {items} item(s)
                    </span><br>
                    <span style="color:#64748b;font-size:12px">
                        {icon} {row.get('payment_method','')}{mpesa}
                    </span>
                </div>
                <span style="color:#16a34a;font-weight:700;font-size:16px">
                    {kes(amount)}
                </span>
            </div>""", unsafe_allow_html=True)

        # Running total at the bottom
        st.markdown(f"""
        <div style="background:#f0fdf4;border-radius:8px;padding:12px 16px;
                    border:1px solid #bbf7d0;margin-top:8px;
                    display:flex;justify-content:space-between;align-items:center">
            <strong style="color:#166534">My Total Today ({my_count} sale(s))</strong>
            <strong style="color:#16a34a;font-size:18px">{kes(my_total)}</strong>
        </div>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
