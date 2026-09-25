"""
Sales / Point of Sale - Glamour Hub Beauty Business
Record sales, build a cart, apply discounts, handle M-Pesa/Cash/Card.
Also shows full sales history with receipt view.
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
from db_connection import DatabaseConnection
from auth import AuthenticationManager
import sql_queries
from mpesa_service import MpesaService


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

def fmt_date(v) -> str:
    if v is None: return "—"
    try:
        if hasattr(v,"strftime"): return v.strftime("%d %b %Y")
        return pd.to_datetime(v).strftime("%d %b %Y")
    except: return str(v)

def fmt_time(v) -> str:
    if v is None: return ""
    try:
        if hasattr(v,"strftime"): return v.strftime("%H:%M")
        return str(v)[:5]
    except: return str(v)


def _css():
    st.markdown("""
    <style>
    .cart-item{background:white;border-radius:8px;padding:12px 14px;
               border:1px solid #e2e8f0;margin-bottom:6px;}
    .receipt{background:#fafafa;border:1px dashed #94a3b8;border-radius:8px;
             padding:20px 24px;font-family:monospace;}
    .kpi-mini{background:white;border-radius:10px;padding:14px;
              border-left:4px solid #16a34a;
              box-shadow:0 1px 4px rgba(0,0,0,.05);
              text-align:center;margin-bottom:8px;}
    .section{color:#1e293b;font-size:16px;font-weight:600;margin:0 0 12px 0;}
    .status-badge{display:inline-block;padding:3px 10px;border-radius:20px;
                  font-size:11px;font-weight:600;}
    </style>
    """, unsafe_allow_html=True)


# ── Cart state helpers ────────────────────────────────────────────────────────

def _init_cart():
    if "cart" not in st.session_state:
        st.session_state.cart = []   # list of {product_id, name, brand, price, qty}

def _add_to_cart(product_id, name, brand, price, qty):
    for item in st.session_state.cart:
        if item["product_id"] == product_id:
            item["qty"] += qty
            return
    st.session_state.cart.append({
        "product_id": product_id,
        "name":       name,
        "brand":      brand,
        "price":      price,
        "qty":        qty,
    })

def _clear_cart():
    st.session_state.cart = []
    for k in ["stk_checkout_id", "stk_phone", "stk_status", "stk_msg", "pos_mpesa_ref"]:
        if k in st.session_state:
            del st.session_state[k]

def _cart_subtotal():
    return sum(i["price"] * i["qty"] for i in st.session_state.cart)


# ── Today KPIs — role-aware ───────────────────────────────────────────────────

def _today_kpis(user: dict):
    role = user.get("role", "Staff")

    if role == "Staff":
        # Staff see only their own transaction count today — no money
        uid     = user["user_id"]
        my_df   = DatabaseConnection.fetch_dataframe(
            sql_queries.QUERY_MY_SALES_TODAY, params=(uid,))
        my_count = len(my_df) if my_df is not None else 0
        items    = 0
        if my_df is not None and not my_df.empty and "items_sold" in my_df.columns:
            items = int(my_df["items_sold"].apply(safe).sum())

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div class="kpi-mini" style="border-left-color:#a7dadc">
                <p style="color:#64748b;font-size:11px;text-transform:uppercase;
                          letter-spacing:.5px;margin:0">My Sales Today</p>
                <p style="color:#1e293b;font-size:20px;font-weight:700;
                          margin:5px 0 0 0">{my_count} transaction(s)</p>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="kpi-mini" style="border-left-color:#ffb6b9">
                <p style="color:#64748b;font-size:11px;text-transform:uppercase;
                          letter-spacing:.5px;margin:0">Items Sold Today</p>
                <p style="color:#1e293b;font-size:20px;font-weight:700;
                          margin:5px 0 0 0">{items} unit(s)</p>
            </div>""", unsafe_allow_html=True)
        return

    # Owner / Manager — full figures
    row  = DatabaseConnection.fetch_one(sql_queries.QUERY_TODAY_SUMMARY)
    txns    = int(safe(row[0] if row else 0))
    revenue = safe(row[1] if row else 0)
    disc    = safe(row[2] if row else 0)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="kpi-mini" style="border-left-color:#a7dadc">
            <p style="color:#64748b;font-size:11px;text-transform:uppercase;
                      letter-spacing:.5px;margin:0">Transactions Today</p>
            <p style="color:#1e293b;font-size:20px;font-weight:700;
                      margin:5px 0 0 0">{txns}</p>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-mini" style="border-left-color:#457b9d">
            <p style="color:#64748b;font-size:11px;text-transform:uppercase;
                      letter-spacing:.5px;margin:0">Revenue Today</p>
            <p style="color:#1e293b;font-size:20px;font-weight:700;
                      margin:5px 0 0 0">{kes(revenue)}</p>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="kpi-mini" style="border-left-color:#ffb6b9">
            <p style="color:#64748b;font-size:11px;text-transform:uppercase;
                      letter-spacing:.5px;margin:0">Discounts Given</p>
            <p style="color:#1e293b;font-size:20px;font-weight:700;
                      margin:5px 0 0 0">{kes(disc)}</p>
        </div>""", unsafe_allow_html=True)


# ── Point of Sale ─────────────────────────────────────────────────────────────

def _pos(user: dict):
    _init_cart()

    st.markdown('<p class="section">🛍 Point of Sale</p>', unsafe_allow_html=True)

    # Load products
    products_df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_ALL_PRODUCTS)
    if products_df is None or products_df.empty:
        st.warning("⚠️ No products in inventory. Add products first.")
        return

    # Only in-stock products
    avail = products_df[products_df["qty_in_stock"] > 0].copy()

    col_products, col_cart = st.columns([3, 2])

    # ── Left: product selector ──
    with col_products:
        st.markdown("**Select Products**")

        c1,c2 = st.columns(2)
        with c1:
            search = st.text_input("🔍 Search product", key="pos_search")
        with c2:
            cats = ["All"] + sorted(avail["category"].dropna().unique().tolist())
            cat_f = st.selectbox("Category", cats, key="pos_cat")

        fdf = avail.copy()
        if search:
            fdf = fdf[fdf["name"].str.contains(search,case=False,na=False) |
                      fdf["brand"].str.contains(search,case=False,na=False)]
        if cat_f != "All":
            fdf = fdf[fdf["category"] == cat_f]

        if fdf.empty:
            st.info("No products match.")
        else:
            for i in range(0, min(len(fdf), 30), 2):
                row_cols = st.columns(2)
                for j, rcol in enumerate(row_cols):
                    if i+j >= len(fdf): break
                    r = fdf.iloc[i+j]
                    qty_in_stock = int(safe(r["qty_in_stock"]))
                    with rcol:
                        with st.container():
                            st.markdown(f"""
                            <div style="background:white;border-radius:8px;
                                        padding:10px 12px;border:1px solid #e2e8f0;
                                        margin-bottom:8px;">
                                <p style="font-weight:600;color:#1e293b;
                                          margin:0;font-size:13px">{r['name']}</p>
                                <p style="color:#64748b;font-size:11px;margin:2px 0">
                                    {r.get('brand','') or ''}
                                    · {r.get('category','')}</p>
                                <p style="color:#16a34a;font-weight:700;
                                          margin:4px 0;font-size:14px">
                                    {kes_full(r['selling_price'])}</p>
                                <p style="color:#64748b;font-size:11px;margin:0">
                                    Stock: {qty_in_stock} {r.get('unit','pcs')}</p>
                            </div>""", unsafe_allow_html=True)

                            add_qty = st.number_input(
                                "Qty", min_value=1,
                                max_value=qty_in_stock,
                                value=1, key=f"qty_{r['product_id']}",
                                label_visibility="collapsed")
                            if st.button(
                                "➕ Add",
                                key=f"add_{r['product_id']}",
                                use_container_width=True,
                            ):
                                _add_to_cart(
                                    int(r["product_id"]),
                                    str(r["name"]),
                                    str(r.get("brand","") or ""),
                                    float(safe(r["selling_price"])),
                                    int(add_qty),
                                )
                                st.rerun()

    # ── Right: cart + checkout ──
    with col_cart:
        st.markdown("**🛒 Cart**")

        cart = st.session_state.cart
        if not cart:
            st.info("Cart is empty. Add products from the left.")
        else:
            # Cart items
            for idx, item in enumerate(cart):
                col_a, col_b = st.columns([3,1])
                with col_a:
                    st.markdown(f"""
                    <div class="cart-item">
                        <p style="font-weight:600;color:#1e293b;margin:0;font-size:13px">
                            {item['name']}</p>
                        <p style="color:#64748b;font-size:11px;margin:2px 0">
                            {item.get('brand','')}</p>
                        <p style="color:#16a34a;font-weight:600;font-size:13px;margin:0">
                            {item['qty']} × {kes_full(item['price'])} =
                            {kes_full(item['price']*item['qty'])}</p>
                    </div>""", unsafe_allow_html=True)
                with col_b:
                    if st.button("✕", key=f"rm_{idx}_{item['product_id']}"):
                        st.session_state.cart.pop(idx)
                        st.rerun()

            subtotal = _cart_subtotal()
            st.markdown("---")

            # Discount
            disc_pct = st.slider("Discount %", 0, 50, 0, key="pos_disc")
            disc_amt = round(subtotal * disc_pct / 100, 2)
            total    = round(subtotal - disc_amt, 2)

            st.markdown(f"""
            <div style="background:#f8fafc;border-radius:8px;padding:14px 16px;
                        border:1px solid #e2e8f0;margin:8px 0">
                <div style="display:flex;justify-content:space-between">
                    <span style="color:#64748b">Subtotal</span>
                    <span>{kes_full(subtotal)}</span>
                </div>
                <div style="display:flex;justify-content:space-between;margin-top:4px">
                    <span style="color:#f59e0b">Discount ({disc_pct}%)</span>
                    <span style="color:#f59e0b">− {kes_full(disc_amt)}</span>
                </div>
                <hr style="border:none;border-top:1px solid #e2e8f0;margin:8px 0">
                <div style="display:flex;justify-content:space-between">
                    <strong style="color:#1e293b;font-size:16px">TOTAL</strong>
                    <strong style="color:#16a34a;font-size:18px">
                        {kes_full(total)}</strong>
                </div>
            </div>""", unsafe_allow_html=True)

            # Payment
            st.markdown("**Payment**")
            method = st.selectbox(
                "Method", ["M-Pesa","Cash","Card","Split"], key="pos_method")

            mpesa_ref = ""
            if method in ("M-Pesa", "Split"):
                st.markdown("##### 📲 M-Pesa Direct STK Connection")
                mpesa_mode = st.radio(
                    "Mode",
                    ["📱 STK Push Prompt", "✏️ Manual Code Entry"],
                    horizontal=True,
                    key="pos_mpesa_mode_radio"
                )

                if mpesa_mode == "📱 STK Push Prompt":
                    phone_input = st.text_input(
                        "Customer M-Pesa Phone Number",
                        value=os.getenv("MPESA_TEST_PHONE", ""),
                        placeholder="e.g. 0712345678 or 0112345678",
                        key="pos_stk_phone_input"
                    )

                    stk_c1, stk_c2 = st.columns([1, 1])
                    with stk_c1:
                        if st.button("🚀 Send STK Push Prompt", key="btn_trigger_stk", use_container_width=True, type="primary"):
                            if not phone_input:
                                st.error("Please enter customer phone number.")
                            else:
                                with st.spinner("Initiating M-Pesa STK Push..."):
                                    DatabaseConnection.execute_query(sql_queries.QUERY_CREATE_MPESA_TABLE)
                                    res = MpesaService.initiate_stk_push(
                                        phone_number=phone_input,
                                        amount=total,
                                        account_reference="GlamourHub",
                                        transaction_desc="Sales Hub"
                                    )
                                if res.get("success"):
                                    chk_id = res["checkout_request_id"]
                                    st.session_state["stk_checkout_id"] = chk_id
                                    st.session_state["stk_phone"] = res["phone_number"]
                                    st.session_state["stk_status"] = "PENDING"
                                    st.session_state["stk_msg"] = res["customer_message"]

                                    DatabaseConnection.execute_query(
                                        sql_queries.QUERY_ADD_MPESA_TRANSACTION,
                                        (chk_id, res.get("merchant_request_id"), res["phone_number"], total, "PENDING", res["customer_message"])
                                    )
                                    st.success(f"📲 STK prompt sent to {res['phone_number']}! Customer enter PIN.")
                                    st.rerun()
                                else:
                                    st.error(f"❌ {res.get('message')}")

                    if st.session_state.get("stk_checkout_id"):
                        chk_id = st.session_state["stk_checkout_id"]
                        status = st.session_state.get("stk_status", "PENDING")
                        phone = st.session_state.get("stk_phone", "")

                        st.markdown(f"""
                        <div style="background:#eff6ff;border-left:4px solid #a7dadc;border-radius:8px;padding:10px 12px;margin:8px 0;font-size:12px">
                            <strong style="color:#1e40af">STK Prompt Sent</strong> to <code>{phone}</code><br>
                            <span style="color:#64748b">ID: {chk_id[:16]}...</span>
                        </div>
                        """, unsafe_allow_html=True)

                        with stk_c2:
                            if st.button("🔄 Verify M-Pesa Status", key="btn_check_stk", use_container_width=True):
                                with st.spinner("Verifying with Safaricom M-Pesa..."):
                                    q_res = MpesaService.query_stk_status(chk_id)
                                    st.session_state["stk_status"] = q_res["status"]
                                    st.session_state["stk_msg"] = q_res["message"]

                                    receipt = q_res.get("receipt_number")
                                    if receipt:
                                        st.session_state["pos_mpesa_ref"] = receipt
                                    elif q_res["status"] == "COMPLETED" and not st.session_state.get("pos_mpesa_ref"):
                                        st.session_state["pos_mpesa_ref"] = f"MP_{chk_id[:8].upper()}"

                                    DatabaseConnection.execute_query(
                                        sql_queries.QUERY_UPDATE_MPESA_TRANSACTION,
                                        (q_res["status"], receipt or st.session_state.get("pos_mpesa_ref"), q_res.get("result_desc"), chk_id)
                                    )
                                    st.rerun()

                        if status == "COMPLETED":
                            ref_val = st.session_state.get("pos_mpesa_ref", "")
                            st.success(f"✅ M-Pesa Payment Confirmed! Code: **{ref_val}**")
                            mpesa_ref = ref_val
                        elif status == "CANCELLED":
                            st.error(f"❌ {st.session_state.get('stk_msg', 'Transaction cancelled.')}")
                        elif status == "FAILED":
                            st.error(f"⚠️ {st.session_state.get('stk_msg', 'Transaction failed.')}")
                        else:
                            st.info("⏳ Waiting for customer PIN... Click 'Verify M-Pesa Status' after PIN input.")

                else:
                    mpesa_ref = st.text_input(
                        "M-Pesa Confirmation Code",
                        value=st.session_state.get("pos_mpesa_ref", ""),
                        placeholder="e.g. QHX3K4ABCD",
                        key="pos_mpesa_ref_input")

                if not mpesa_ref and st.session_state.get("pos_mpesa_ref"):
                    mpesa_ref = st.session_state["pos_mpesa_ref"]

            amount_paid = st.number_input(
                "Amount Tendered (KES)",
                min_value=float(total), value=float(total),
                step=10.0, key="pos_paid")
            change = round(amount_paid - total, 2)
            if change > 0:
                st.markdown(
                    f"<p style='color:#16a34a;font-weight:600'>"
                    f"Change: {kes_full(change)}</p>",
                    unsafe_allow_html=True)

            notes = st.text_area("Notes", height=60, key="pos_notes")

            col_buy, col_clr = st.columns(2)
            with col_buy:
                checkout = st.button(
                    "✅ Complete Sale",
                    use_container_width=True, type="primary",
                    key="pos_checkout")
            with col_clr:
                if st.button("🗑 Clear Cart", use_container_width=True,
                             key="pos_clear"):
                    _clear_cart(); st.rerun()

            if checkout:
                if method == "M-Pesa" and not mpesa_ref:
                    # If phone entered, trigger STK push automatically
                    phone_val = st.session_state.get("pos_stk_phone_input", "").strip()
                    if phone_val and not st.session_state.get("stk_checkout_id"):
                        with st.spinner("Connecting to M-Pesa & sending STK Push prompt..."):
                            DatabaseConnection.execute_query(sql_queries.QUERY_CREATE_MPESA_TABLE)
                            res = MpesaService.initiate_stk_push(
                                phone_number=phone_val,
                                amount=total,
                                account_reference="GlamourHub",
                                transaction_desc="Sales Hub"
                            )
                        if res.get("success"):
                            chk_id = res["checkout_request_id"]
                            st.session_state["stk_checkout_id"] = chk_id
                            st.session_state["stk_phone"] = res["phone_number"]
                            st.session_state["stk_status"] = "PENDING"
                            st.session_state["stk_msg"] = res["customer_message"]
                            DatabaseConnection.execute_query(
                                sql_queries.QUERY_ADD_MPESA_TRANSACTION,
                                (chk_id, res.get("merchant_request_id"), res["phone_number"], total, "PENDING", res["customer_message"])
                            )
                            st.success(f"📲 STK push prompt sent to {res['phone_number']}! Ask customer to enter PIN, then click Complete Sale again.")
                            st.rerun()
                        else:
                            st.error(f"❌ M-Pesa Error: {res.get('message')}")
                    else:
                        st.error("Please enter customer phone number and verify M-Pesa payment or confirmation code.")
                elif not cart:
                    st.error("Cart is empty.")

                else:
                    now = datetime.now()
                    ok = DatabaseConnection.execute_query(
                        sql_queries.QUERY_ADD_SALE,
                        (user["user_id"],
                         subtotal, disc_amt, total,
                         amount_paid, change,
                         method, mpesa_ref or None,
                         now.date(), now.time(),
                         notes or None, "Completed")
                    )
                    if ok:
                        sale_id_row = DatabaseConnection.fetch_one(
                            sql_queries.QUERY_LAST_SALE_ID)
                        sale_id = sale_id_row[0] if sale_id_row else None
                        if sale_id:
                            for item in cart:
                                DatabaseConnection.execute_query(
                                    sql_queries.QUERY_ADD_SALE_ITEM,
                                    (sale_id,
                                     item["product_id"],
                                     item["qty"],
                                     item["price"],
                                     item["price"] * item["qty"])
                                )
                        # Store receipt in session for display
                        st.session_state["last_receipt"] = {
                            "sale_id":   sale_id,
                            "items":     list(cart),
                            "subtotal":  subtotal,
                            "discount":  disc_amt,
                            "total":     total,
                            "paid":      amount_paid,
                            "change":    change,
                            "method":    method,
                            "mpesa_ref": mpesa_ref,
                            "time":      now.strftime("%d %b %Y %H:%M"),
                        }
                        _clear_cart()
                        st.success(f"✅ Sale #{sale_id} completed!")
                        st.rerun()
                    else:
                        st.error("Failed to save sale.")


    # ── Receipt ──
    if "last_receipt" in st.session_state:
        r = st.session_state["last_receipt"]
        st.markdown("---")
        st.markdown('<p class="section">🧾 Last Receipt</p>',
                    unsafe_allow_html=True)
        lines = "\n".join(
            f"  {i['name'][:28]:<30} {i['qty']} × {kes_full(i['price']):<12} "
            f"{kes_full(i['price']*i['qty'])}"
            for i in r["items"]
        )
        st.markdown(f"""
        <div class="receipt">
            <div style="text-align:center;margin-bottom:12px">
                <strong>💄 GLAMOUR HUB</strong><br>
                <span style="font-size:11px">Receipt #{r['sale_id']} · {r['time']}</span>
            </div>
            <hr style="border:1px dashed #94a3b8">
            <pre style="font-size:12px;margin:8px 0">{lines}</pre>
            <hr style="border:1px dashed #94a3b8">
            <div style="display:flex;justify-content:space-between">
                <span>Subtotal</span><span>{kes_full(r['subtotal'])}</span>
            </div>
            {"<div style='display:flex;justify-content:space-between;color:#f59e0b'><span>Discount</span><span>- "+kes_full(r['discount'])+"</span></div>" if r['discount'] > 0 else ""}
            <div style="display:flex;justify-content:space-between;
                        font-weight:700;font-size:15px;margin-top:4px">
                <span>TOTAL</span><span style="color:#16a34a">{kes_full(r['total'])}</span>
            </div>
            <div style="color:#64748b;font-size:12px;margin-top:8px">
                Paid: {kes_full(r['paid'])} · {r['method']}
                {" · Ref: "+r['mpesa_ref'] if r.get('mpesa_ref') else ""}
                {"<br>Change: "+kes_full(r['change']) if r['change']>0 else ""}
            </div>
            <div style="text-align:center;margin-top:14px;font-size:11px;color:#94a3b8">
                Thank you for shopping with us! 💕
            </div>
        </div>""", unsafe_allow_html=True)
        if st.button("✕ Dismiss Receipt", key="dismiss_receipt"):
            del st.session_state["last_receipt"]
            st.rerun()


# ── Sales history — role-aware ────────────────────────────────────────────────

def _sales_history(user: dict):
    role = user.get("role", "Staff")
    st.markdown('<p class="section">📋 Sales History</p>', unsafe_allow_html=True)

    # Staff only see their own sales, no amounts
    if role == "Staff":
        df = DatabaseConnection.fetch_dataframe(
            sql_queries.QUERY_MY_SALES_HISTORY, params=(user["user_id"],))
        if df is None or df.empty:
            st.info("You haven't recorded any sales yet.")
            return

        col1, col2 = st.columns(2)
        with col1:
            method_f = st.selectbox("Payment Method",
                                    ["All","Cash","M-Pesa","Card","Split"],
                                    key="sh_method_staff")
        with col2:
            period = st.selectbox("Period",
                                  ["All Time","Today","This Week","This Month"],
                                  key="sh_period_staff")

        df["sale_date"] = pd.to_datetime(df["sale_date"], errors="coerce")
        today = pd.Timestamp.today().normalize()
        if period == "Today":
            df = df[df["sale_date"] == today]
        elif period == "This Week":
            df = df[df["sale_date"] >= today - pd.Timedelta(days=today.weekday())]
        elif period == "This Month":
            df = df[df["sale_date"].dt.to_period("M") == today.to_period("M")]
        if method_f != "All":
            df = df[df["payment_method"] == method_f]

        st.caption(f"{len(df)} transaction(s)")
        for _, row in df.iterrows():
            icons = {"M-Pesa":"📱","Cash":"💵","Card":"💳","Split":"🔀"}
            icon  = icons.get(str(row.get("payment_method","")),"💰")
            mpesa = f" · {row['mpesa_ref']}" if row.get("mpesa_ref") else ""
            date_str = row["sale_date"].strftime("%d %b %Y") if hasattr(row["sale_date"],"strftime") else str(row["sale_date"])
            time_str = str(row.get("sale_time",""))[:5]
            items    = int(safe(row.get("items_sold",0)))
            amount   = safe(row.get("total_amount", 0))
            st.markdown(f"""
            <div style="background:white;border-radius:8px;padding:12px 16px;
                        border:1px solid #e2e8f0;margin-bottom:6px;
                        display:flex;justify-content:space-between;align-items:center">
                <div>
                    <strong style="color:#1e293b">Sale #{row['sale_id']}</strong>
                    <span style="color:#64748b;font-size:12px">
                        &nbsp;·&nbsp; {date_str} {time_str}
                        &nbsp;·&nbsp; {items} item(s)
                    </span><br>
                    <span style="color:#64748b;font-size:12px">
                        {icon} {row.get('payment_method','')}{mpesa}
                    </span>
                </div>
                <span style="color:#16a34a;font-weight:700;font-size:15px">
                    {kes(amount)}
                </span>
            </div>""", unsafe_allow_html=True)
        return

    # ── Owner / Manager: full history with amounts ──
    df = DatabaseConnection.fetch_dataframe(sql_queries.QUERY_ALL_SALES)
    if df is None or df.empty:
        st.info("No sales recorded yet.")
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        search = st.text_input("🔍 Staff / payment method", key="sh_search")
    with col2:
        method_f = st.selectbox("Payment Method",
                                ["All","Cash","M-Pesa","Card","Split"],
                                key="sh_method")
    with col3:
        period = st.selectbox("Period",
                              ["All Time","Today","This Week",
                               "This Month","Last 30 Days"],
                              key="sh_period")

    df["sale_date"] = pd.to_datetime(df["sale_date"], errors="coerce")
    today = pd.Timestamp.today().normalize()

    if period == "Today":
        df = df[df["sale_date"] == today]
    elif period == "This Week":
        df = df[df["sale_date"] >= today - pd.Timedelta(days=today.weekday())]
    elif period == "This Month":
        df = df[df["sale_date"].dt.to_period("M") == today.to_period("M")]
    elif period == "Last 30 Days":
        df = df[df["sale_date"] >= today - pd.Timedelta(days=30)]

    if method_f != "All":
        df = df[df["payment_method"] == method_f]
    if search:
        df = df[df["served_by"].str.contains(search,case=False,na=False) |
                df["payment_method"].str.contains(search,case=False,na=False)]

    if df.empty:
        st.info("No sales match your filters.")
        return

    total = df["total_amount"].apply(safe).sum()
    disc  = df["discount_amount"].apply(safe).sum()
    m1, m2, m3 = st.columns(3)
    m1.metric("Transactions", len(df))
    m2.metric("Total Revenue", kes(total))
    m3.metric("Discounts Given", kes(disc))
    st.markdown("<br>", unsafe_allow_html=True)

    status_color = {"Completed":"#16a34a","Refunded":"#f59e0b","Void":"#dc2626"}

    for _, row in df.iterrows():
        sc   = status_color.get(str(row.get("status","")),"#64748b")
        icons= {"M-Pesa":"📱","Cash":"💵","Card":"💳","Split":"🔀"}
        icon = icons.get(str(row.get("payment_method","")),"💰")

        with st.expander(
            f"#{row['sale_id']}  {fmt_date(row.get('sale_date'))} "
            f"{fmt_time(row.get('sale_time'))}  —  "
            f"Staff: {row.get('served_by','—')}  —  "
            f"{kes_full(row.get('total_amount',0))}  "
            f"{icon} {row.get('payment_method','')}"
        ):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""
                **Served by:** {row.get('served_by','—')}<br>
                **Date/Time:** {fmt_date(row.get('sale_date'))} {fmt_time(row.get('sale_time'))}<br>
                **Status:** <span style='color:{sc}'>{row.get('status','')}</span>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                **Total:** {kes_full(row.get('total_amount',0))}<br>
                **Payment:** {icon} {row.get('payment_method','')}<br>
                {f"**M-Pesa Ref:** {row.get('mpesa_ref','')}" if row.get('mpesa_ref') else ""}
                """)

            items_df = DatabaseConnection.fetch_dataframe(
                sql_queries.QUERY_SALE_ITEMS, params=(int(row["sale_id"]),))
            if items_df is not None and not items_df.empty:
                items_df["unit_price"] = items_df["unit_price"].apply(kes_full)
                items_df["line_total"] = items_df["line_total"].apply(kes_full)
                items_df.columns = ["ID","Product","Brand","Qty","Unit Price","Total"]
                st.dataframe(items_df.drop(columns=["ID"]),
                             use_container_width=True, hide_index=True)


# ── Staff check-in/out ────────────────────────────────────────────────────────

def _staff_checkin(user: dict):
    st.markdown('<p class="section">🕐 Staff Check-In / Out</p>',
                unsafe_allow_html=True)

    att = DatabaseConnection.fetch_one(
        sql_queries.QUERY_MY_ATTENDANCE_TODAY, (user["user_id"],))

    check_in  = att[0] if att else None
    check_out = att[1] if att else None

    if check_in:
        st.markdown(
            f'<div style="background:#f0fdf4;border-left:4px solid #16a34a;'
            f'border-radius:8px;padding:12px 16px;margin-bottom:12px">'
            f'✅ Checked in at <strong>{fmt_time(check_in)}</strong>'
            f'{" · Checked out at <strong>"+fmt_time(check_out)+"</strong>" if check_out else ""}'
            f'</div>', unsafe_allow_html=True)

    col1,col2 = st.columns(2)
    with col1:
        if not check_in or (check_in and check_out):
            if st.button("🟢 Check In", use_container_width=True, type="primary"):
                DatabaseConnection.execute_query(
                    sql_queries.QUERY_CHECK_IN, (user["user_id"],))
                st.success("Checked in!"); st.rerun()
    with col2:
        if check_in and not check_out:
            if st.button("🔴 Check Out", use_container_width=True):
                DatabaseConnection.execute_query(
                    sql_queries.QUERY_CHECK_OUT, (user["user_id"],))
                st.success("Checked out!"); st.rerun()


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    AuthenticationManager.require_login()
    _css()

    user = AuthenticationManager.get_current_user()
    if not user:
        st.error("Session expired."); st.stop()

    st.markdown("""
    <div style="padding:16px 0 20px 0;border-bottom:1px solid #e2e8f0;
                margin-bottom:24px;">
        <h1 style="color:#1e293b;margin:0;font-size:26px;font-weight:700;">
            🛍 Sales & Point of Sale
        </h1>
        <p style="color:#64748b;margin:4px 0 0 0;font-size:14px;">
            Record sales, issue receipts, and view transaction history.
        </p>
    </div>
    """, unsafe_allow_html=True)

    _today_kpis(user)
    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs([
        "🛍 New Sale",
        "📋 Sales History",
        "🕐 Staff Check-In",
    ])

    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        _pos(user)

    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        _sales_history(user)

    with tab3:
        st.markdown("<br>", unsafe_allow_html=True)
        _staff_checkin(user)


if __name__ == "__main__":
    main()
