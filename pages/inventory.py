"""
Inventory Management - Glamour Hub Beauty Business
Stock levels, restock alerts, add/edit products, stock movements audit trail.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from db_connection import DatabaseConnection
from auth import AuthenticationManager
import sql_queries


# ── helpers ───────────────────────────────────────────────────────────────────

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

def fmt_dt(v) -> str:
    if v is None: return "—"
    try:
        if hasattr(v,"strftime"): return v.strftime("%d %b %Y %H:%M")
        return pd.to_datetime(v).strftime("%d %b %Y %H:%M")
    except: return str(v)


UNITS = ["piece","bottle","tube","sachet","set","kit","jar","box","ml","g","litre","pair"]

STATUS_STYLE = {
    "Out of Stock": ("#dc2626","#fef2f2"),
    "Low Stock":    ("#f59e0b","#fffbeb"),
    "In Stock":     ("#16a34a","#f0fdf4"),
}


def _css():
    st.markdown("""
    <style>
    .prod-card{background:white;border-radius:10px;padding:14px 16px;
               border:1px solid #e2e8f0;margin-bottom:8px;
               box-shadow:0 1px 4px rgba(0,0,0,.05);}
    .badge{display:inline-block;padding:3px 10px;border-radius:20px;
           font-size:11px;font-weight:600;}
    .kpi-mini{background:white;border-radius:10px;padding:16px;
              border-left:4px solid #3b82f6;
              box-shadow:0 1px 4px rgba(0,0,0,.05);
              text-align:center;margin-bottom:8px;}
    .section{color:#1e293b;font-size:16px;font-weight:600;margin:0 0 12px 0;}
    </style>
    """, unsafe_allow_html=True)


# ── KPI bar ───────────────────────────────────────────────────────────────────

def _inventory_kpis():
    row = DatabaseConnection.fetch_one(sql_queries.QUERY_STOCK_VALUE)
    cost_val   = safe(row[0] if row else 0)
    retail_val = safe(row[1] if row else 0)
    prod_count = int(safe(row[2] if row else 0))
    oos        = int(safe(row[3] if row else 0))
    low        = int(safe(row[4] if row else 0))

    c1,c2,c3,c4,c5 = st.columns(5)
    cards = [
        (c1,"Total Products",   str(prod_count),  "#3b82f6"),
        (c2,"Stock Cost Value", kes(cost_val),     "#8b5cf6"),
        (c3,"Retail Value",     kes(retail_val),   "#0ea5e9"),
        (c4,"Low Stock Items",  str(low),          "#f59e0b"),
        (c5,"Out of Stock",     str(oos),          "#dc2626"),
    ]
    for col,label,value,color in cards:
        with col:
            st.markdown(f"""
            <div class="kpi-mini" style="border-left-color:{color}">
                <p style="color:#64748b;font-size:11px;text-transform:uppercase;
                          letter-spacing:.5px;margin:0">{label}</p>
                <p style="color:#1e293b;font-size:22px;font-weight:700;
                          margin:6px 0 0 0">{value}</p>
            </div>""", unsafe_allow_html=True)


# ── Stock overview table ──────────────────────────────────────────────────────

def _stock_overview():
    st.markdown('<p class="section">📦 Current Stock Levels</p>',
                unsafe_allow_html=True)

    df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_ALL_PRODUCTS)
    if df is None or df.empty:
        st.info("No products found. Add your first product below.")
        return

    # Filters
    col1,col2,col3 = st.columns(3)
    with col1:
        search = st.text_input("🔍 Search product / brand", key="inv_search")
    with col2:
        cats = ["All Categories"] + sorted(df["category"].dropna().unique().tolist())
        cat_f = st.selectbox("Category", cats, key="inv_cat")
    with col3:
        status_f = st.selectbox(
            "Stock Status",
            ["All","Out of Stock","Low Stock","In Stock"],
            key="inv_status")

    fdf = df.copy()
    if search:
        mask = (fdf["name"].str.contains(search,case=False,na=False) |
                fdf["brand"].str.contains(search,case=False,na=False))
        fdf = fdf[mask]
    if cat_f != "All Categories":
        fdf = fdf[fdf["category"] == cat_f]
    if status_f != "All":
        fdf = fdf[fdf["stock_status"] == status_f]

    if fdf.empty:
        st.info("No products match your filters.")
        return

    # Card view
    for i in range(0, len(fdf), 2):
        cols = st.columns(2)
        for j,col in enumerate(cols):
            if i+j >= len(fdf): break
            r = fdf.iloc[i+j]
            sc,sbg = STATUS_STYLE.get(str(r["stock_status"]),("#64748b","#f1f5f9"))
            qty    = int(safe(r["qty_in_stock"]))
            reorder= int(safe(r["reorder_level"]))
            margin = safe(r.get("margin_pct",0))
            pct    = min(int(qty / max(reorder*2,1) * 100), 100)
            bar_color = "#dc2626" if qty==0 else "#f59e0b" if qty<=reorder else "#16a34a"

            with col:
                st.markdown(f"""
                <div class="prod-card">
                  <div style="display:flex;justify-content:space-between;
                              align-items:start;margin-bottom:6px">
                    <div>
                      <p style="font-weight:700;color:#1e293b;margin:0;font-size:14px">
                        {r['name']}</p>
                      <p style="color:#64748b;font-size:12px;margin:2px 0">
                        🏷 {r.get('brand','') or '—'} &nbsp;·&nbsp;
                        {r.get('category','') or '—'}</p>
                    </div>
                    <span class="badge" style="background:{sbg};color:{sc}">
                      {r['stock_status']}</span>
                  </div>
                  <div style="background:#f1f5f9;border-radius:4px;height:6px;margin:8px 0">
                    <div style="width:{pct}%;background:{bar_color};
                                height:6px;border-radius:4px"></div>
                  </div>
                  <div style="display:flex;justify-content:space-between;
                              align-items:center">
                    <span style="font-size:13px;color:{bar_color};font-weight:600">
                      {qty} {r.get('unit','pcs')} in stock
                    </span>
                    <div style="text-align:right">
                      <span style="font-size:13px;font-weight:700;color:#16a34a">
                        {kes_full(r['selling_price'])}</span><br>
                      <span style="font-size:11px;color:#64748b">
                        Cost: {kes_full(r['buying_price'])} ·
                        Margin: {margin:.1f}%</span>
                    </div>
                  </div>
                  <p style="color:#64748b;font-size:11px;margin:4px 0 0 0">
                    SKU: {r.get('sku','—')} &nbsp;·&nbsp;
                    Reorder at: {reorder} &nbsp;·&nbsp;
                    Restock qty: {int(safe(r.get('reorder_qty',0)))}
                  </p>
                </div>""", unsafe_allow_html=True)

    st.caption(f"Showing {len(fdf)} of {len(df)} products")


# ── Restock alerts panel ──────────────────────────────────────────────────────

def _restock_alerts():
    st.markdown('<p class="section">🚨 Restock Alerts</p>', unsafe_allow_html=True)
    df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_LOW_STOCK)
    if df is None or df.empty:
        st.success("✅ All products are well stocked!")
        return

    total_restock_cost = 0
    for _,r in df.iterrows():
        qty    = int(safe(r["qty_in_stock"]))
        needed = int(safe(r["reorder_qty"]))
        cost   = safe(r["selling_price"]) * needed   # rough estimate
        total_restock_cost += cost
        color  = "#dc2626" if qty==0 else "#f59e0b"
        label  = "OUT OF STOCK" if qty==0 else f"{qty} left"

        st.markdown(f"""
        <div style="background:white;border-radius:8px;padding:12px 16px;
                    border-left:4px solid {color};border:1px solid #e2e8f0;
                    margin-bottom:6px;display:flex;
                    justify-content:space-between;align-items:center">
          <div>
            <strong style="color:#1e293b">{r['name']}</strong>
            <span style="color:#64748b;font-size:12px">
              · {r.get('brand','') or ''} · {r.get('category','')}</span><br>
            <span style="color:{color};font-weight:600;font-size:13px">{label}</span>
          </div>
          <div style="text-align:right">
            <p style="margin:0;font-size:13px;color:#1e293b;font-weight:600">
              Order {needed} units</p>
            <p style="margin:0;font-size:11px;color:#64748b">
              SKU: {r.get('sku','—')}</p>
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:#fffbeb;border-radius:8px;padding:12px 16px;
                border:1px solid #fde68a;margin-top:8px">
        <strong>Estimated restock cost: ~{kes(total_restock_cost)}</strong>
        (at current selling prices)
    </div>""", unsafe_allow_html=True)


# ── Add product form ──────────────────────────────────────────────────────────

def _add_product_form(user: dict):
    st.markdown("### ➕ Add New Product")
    cats_df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_ALL_CATEGORIES)
    cat_map = {}
    if cats_df is not None and not cats_df.empty:
        cat_map = dict(zip(cats_df["name"], cats_df["category_id"]))

    with st.form("add_product_form", clear_on_submit=True):
        col1,col2 = st.columns(2)
        with col1:
            name          = st.text_input("Product Name *",
                                          placeholder="e.g. Nivea Body Lotion 400ml")
            brand         = st.text_input("Brand",
                                          placeholder="e.g. Nivea")
            sku           = st.text_input("SKU / Barcode",
                                          placeholder="e.g. NIV-BL-400")
            cat_opts      = ["-- Select Category --"] + list(cat_map.keys())
            cat_sel       = st.selectbox("Category", cat_opts)
            unit          = st.selectbox("Unit", UNITS)

        with col2:
            buying_price  = st.number_input("Buying Price (KES) *",
                                            min_value=0.0, step=10.0)
            selling_price = st.number_input("Selling Price (KES) *",
                                            min_value=0.0, step=10.0)
            if selling_price > 0 and buying_price > 0:
                margin = (selling_price - buying_price) / selling_price * 100
                color  = "#16a34a" if margin >= 30 else "#f59e0b" if margin >= 15 else "#dc2626"
                st.markdown(f"<p style='color:{color};font-size:13px'>"
                            f"Margin: {margin:.1f}%</p>", unsafe_allow_html=True)
            qty_in_stock  = st.number_input("Opening Stock *",
                                            min_value=0, step=1)
            reorder_level = st.number_input("Reorder Alert Level",
                                            min_value=0, step=1, value=5,
                                            help="Alert when stock falls to this level")
            reorder_qty   = st.number_input("Suggested Restock Qty",
                                            min_value=1, step=1, value=10)

        description = st.text_area("Description (optional)", height=60)

        submitted = st.form_submit_button(
            "💾 Add Product", use_container_width=True, type="primary")

        if submitted:
            if not name:
                st.error("Product name is required.")
            elif selling_price <= 0:
                st.error("Selling price must be greater than 0.")
            else:
                cat_id = cat_map.get(cat_sel) if cat_sel != "-- Select Category --" else None
                ok = DatabaseConnection.execute_query(
                    sql_queries.QUERY_ADD_PRODUCT,
                    (cat_id, name, brand or None, sku or None,
                     description or None, buying_price, selling_price,
                     qty_in_stock, reorder_level, reorder_qty, unit)
                )
                if ok:
                    # Log opening stock movement if qty > 0
                    if qty_in_stock > 0:
                        pid_row = DatabaseConnection.fetch_one(
                            "SELECT product_id FROM products WHERE name=%s ORDER BY product_id DESC LIMIT 1",
                            (name,))
                        if pid_row:
                            DatabaseConnection.execute_query(
                                sql_queries.QUERY_LOG_MOVEMENT,
                                (pid_row[0],"Restock",qty_in_stock,
                                 0, qty_in_stock,
                                 "Opening stock",user["user_id"]))
                    st.success(f"✅ **{name}** added to inventory!")
                    st.rerun()
                else:
                    st.error("Failed to save product.")


# ── Restock form ──────────────────────────────────────────────────────────────

def _restock_form(user: dict):
    st.markdown("### 📥 Record Restock / Stock Purchase")
    df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_ALL_PRODUCTS)
    if df is None or df.empty:
        st.warning("No products yet.")
        return

    prod_map = {
        f"{r['name']} — {r.get('brand','') or ''} ({int(safe(r['qty_in_stock']))} in stock)":
        (r["product_id"], r["qty_in_stock"])
        for _,r in df.iterrows()
    }

    with st.form("restock_form", clear_on_submit=True):
        selected = st.selectbox("Select Product *", list(prod_map.keys()))
        pid, cur_qty = prod_map[selected]

        col1,col2 = st.columns(2)
        with col1:
            qty   = st.number_input("Quantity Received *", min_value=1, step=1)
            cost  = st.number_input("Cost per Unit (KES)",
                                    min_value=0.0, step=10.0,
                                    help="Leave 0 to keep existing buying price")
        with col2:
            notes = st.text_area("Notes / Supplier",
                                 placeholder="e.g. Ordered from XYZ Distributors",
                                 height=100)

        submitted = st.form_submit_button(
            "📥 Record Restock", use_container_width=True, type="primary")

        if submitted:
            ok = DatabaseConnection.execute_query(
                sql_queries.QUERY_RESTOCK,
                (int(pid), int(qty), float(cost), notes or None, user["user_id"])
            )
            if ok:
                st.success(
                    f"✅ Restocked **{int(qty)} units**. "
                    f"New stock: **{int(safe(cur_qty)) + int(qty)}**")
                st.rerun()
            else:
                st.error("Failed to record restock.")


# ── Edit product ──────────────────────────────────────────────────────────────

def _edit_product_form(user: dict):
    st.markdown("### ✏️ Edit Product")
    df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_ALL_PRODUCTS_INCL_INACTIVE)
    if df is None or df.empty:
        st.info("No products to edit.")
        return

    cats_df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_ALL_CATEGORIES)
    cat_map = {}
    if cats_df is not None and not cats_df.empty:
        cat_map = dict(zip(cats_df["name"], cats_df["category_id"]))
    cat_id_to_name = {v:k for k,v in cat_map.items()}

    prod_map = {
        f"{r['name']} ({r.get('brand','') or '—'})": r["product_id"]
        for _,r in df.iterrows()
    }
    selected = st.selectbox("Select product to edit", list(prod_map.keys()),
                            key="edit_prod_select")
    pid = prod_map[selected]

    prow = DatabaseConnection.fetch_dataframe(
        sql_queries.QUERY_PRODUCT_BY_ID, params=(pid,))
    if prow is None or prow.empty:
        st.error("Could not load product.")
        return
    p = prow.iloc[0]

    with st.form("edit_product_form"):
        col1,col2 = st.columns(2)
        with col1:
            name    = st.text_input("Product Name", value=str(p.get("name","")))
            brand   = st.text_input("Brand", value=str(p.get("brand","") or ""))
            sku     = st.text_input("SKU", value=str(p.get("sku","") or ""))
            cur_cat = cat_id_to_name.get(p.get("category_id"))
            cat_opts= ["-- None --"] + list(cat_map.keys())
            cat_idx = cat_opts.index(cur_cat) if cur_cat and cur_cat in cat_opts else 0
            cat_sel = st.selectbox("Category", cat_opts, index=cat_idx)
            unit_idx= UNITS.index(str(p.get("unit","piece"))) if str(p.get("unit","piece")) in UNITS else 0
            unit    = st.selectbox("Unit", UNITS, index=unit_idx)

        with col2:
            buying_price  = st.number_input("Buying Price",
                                            value=float(safe(p.get("buying_price",0))),
                                            min_value=0.0, step=10.0)
            selling_price = st.number_input("Selling Price",
                                            value=float(safe(p.get("selling_price",0))),
                                            min_value=0.0, step=10.0)
            reorder_level = st.number_input("Reorder Level",
                                            value=int(safe(p.get("reorder_level",5))),
                                            min_value=0)
            reorder_qty   = st.number_input("Restock Qty",
                                            value=int(safe(p.get("reorder_qty",10))),
                                            min_value=1)
            is_active     = st.checkbox("Active", value=bool(p.get("is_active",True)))

        desc = st.text_area("Description",
                            value=str(p.get("description","") or ""), height=60)

        submitted = st.form_submit_button(
            "💾 Save Changes", use_container_width=True, type="primary")

        if submitted:
            cat_id = cat_map.get(cat_sel) if cat_sel != "-- None --" else None
            ok = DatabaseConnection.execute_query(
                sql_queries.QUERY_UPDATE_PRODUCT,
                (cat_id, name, brand or None, sku or None,
                 buying_price, selling_price,
                 reorder_level, reorder_qty, unit,
                 desc or None, pid)
            )
            if is_active != bool(p.get("is_active",True)):
                DatabaseConnection.execute_query(
                    "UPDATE products SET is_active=%s WHERE product_id=%s",
                    (is_active, pid))
            if ok:
                st.success(f"✅ **{name}** updated!")
                st.rerun()
            else:
                st.error("Update failed.")


# ── Stock movements ───────────────────────────────────────────────────────────

def _stock_movements():
    st.markdown("### 📋 Stock Movement History")
    df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_STOCK_MOVEMENTS)
    if df is None or df.empty:
        st.info("No stock movements recorded yet.")
        return

    col1,col2 = st.columns(2)
    with col1:
        type_f = st.selectbox(
            "Type", ["All","Restock","Sale","Adjustment","Return","Damage"],
            key="mv_type")
    with col2:
        search = st.text_input("🔍 Product name", key="mv_search")

    fdf = df.copy()
    if type_f != "All":
        fdf = fdf[fdf["movement_type"] == type_f]
    if search:
        fdf = fdf[fdf["product_name"].str.contains(search,case=False,na=False)]

    if fdf.empty:
        st.info("No movements match your filter.")
        return

    type_color = {
        "Restock":    "#16a34a",
        "Sale":       "#3b82f6",
        "Adjustment": "#f59e0b",
        "Return":     "#8b5cf6",
        "Damage":     "#dc2626",
    }

    for _,r in fdf.head(100).iterrows():
        tc    = type_color.get(str(r["movement_type"]),"#64748b")
        chg   = int(safe(r["qty_change"]))
        arrow = "▲" if chg > 0 else "▼"
        color = "#16a34a" if chg > 0 else "#dc2626"
        cost_html = (f"· Cost/unit: {kes_full(r['cost_per_unit'])}"
                     if r.get("cost_per_unit") else "")

        st.markdown(f"""
        <div style="background:white;border-radius:8px;padding:10px 14px;
                    border:1px solid #e2e8f0;margin-bottom:5px;
                    display:flex;justify-content:space-between;align-items:center">
          <div>
            <span class="badge" style="background:{tc}20;color:{tc};margin-right:8px">
              {r['movement_type']}</span>
            <strong style="color:#1e293b">{r['product_name']}</strong>
            <span style="color:#64748b;font-size:12px">
              · {r.get('brand','') or ''}</span><br>
            <span style="color:#64748b;font-size:11px">
              {fmt_dt(r.get('created_at'))} · By {r.get('recorded_by','')}
              {cost_html}
              {f"· {r['notes']}" if r.get('notes') else ''}
            </span>
          </div>
          <div style="text-align:right;min-width:100px">
            <p style="color:{color};font-weight:700;font-size:15px;margin:0">
              {arrow} {abs(chg)}</p>
            <p style="color:#64748b;font-size:11px;margin:0">
              {int(safe(r['qty_before']))} → {int(safe(r['qty_after']))}</p>
          </div>
        </div>""", unsafe_allow_html=True)

    if len(fdf) > 100:
        st.caption("Showing latest 100 movements.")


# ── Category analytics ────────────────────────────────────────────────────────

def _category_analytics():
    st.markdown("### 📊 Stock by Category")
    df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_CATEGORY_STOCK)
    if df is None or df.empty:
        st.info("No category data.")
        return

    col1,col2 = st.columns(2)
    with col1:
        fig = px.pie(
            df, values="stock_value", names="category",
            title="Stock Value by Category",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            hole=0.45,
        )
        fig.update_layout(height=280,paper_bgcolor="white",
                          margin=dict(l=0,r=0,t=30,b=0),font=dict(size=11))
        st.plotly_chart(fig, use_container_width=True,
                        config={"displayModeBar":False})
    with col2:
        fig2 = px.bar(
            df, x="category", y="total_units",
            color="total_units", color_continuous_scale="Greens",
            title="Units in Stock by Category",
            labels={"category":"Category","total_units":"Units"},
        )
        fig2.update_layout(height=280, plot_bgcolor="white",
                           paper_bgcolor="white",
                           margin=dict(l=0,r=0,t=30,b=0),font=dict(size=11),
                           coloraxis_showscale=False,showlegend=False,
                           xaxis=dict(showgrid=False),
                           yaxis=dict(showgrid=True,gridcolor="#f1f5f9"))
        st.plotly_chart(fig2, use_container_width=True,
                        config={"displayModeBar":False})

    tbl = df.copy()
    tbl["stock_value"] = tbl["stock_value"].apply(kes)
    tbl.columns = ["Category","Products","Total Units","Stock Value"]
    st.dataframe(tbl, use_container_width=True, hide_index=True)


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    AuthenticationManager.require_login()
    _css()

    user = AuthenticationManager.get_current_user()
    if not user:
        st.error("Session expired."); st.stop()

    st.markdown("""
    <div style="padding:16px 0 20px 0;border-bottom:1px solid #e2e8f0;margin-bottom:24px;">
        <h1 style="color:#1e293b;margin:0;font-size:26px;font-weight:700;">
            📦 Inventory Management
        </h1>
        <p style="color:#64748b;margin:4px 0 0 0;font-size:14px;">
            Track stock levels, get restock alerts, and manage your product catalogue.
        </p>
    </div>
    """, unsafe_allow_html=True)

    _inventory_kpis()
    st.markdown("<br>", unsafe_allow_html=True)

    tab1,tab2,tab3,tab4,tab5,tab6 = st.tabs([
        "📦 Stock Overview",
        "🚨 Restock Alerts",
        "📥 Record Restock",
        "➕ Add Product",
        "✏️ Edit Product",
        "📋 Movement History",
    ])

    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        _stock_overview()
        st.markdown("---")
        _category_analytics()

    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        _restock_alerts()

    with tab3:
        st.markdown("<br>", unsafe_allow_html=True)
        _restock_form(user)

    with tab4:
        st.markdown("<br>", unsafe_allow_html=True)
        _add_product_form(user)

    with tab5:
        st.markdown("<br>", unsafe_allow_html=True)
        _edit_product_form(user)

    with tab6:
        st.markdown("<br>", unsafe_allow_html=True)
        _stock_movements()


if __name__ == "__main__":
    main()
