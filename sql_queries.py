"""
SQL Queries - Glamour Hub Beauty Business v1.0
Single-branch beauty shop management system.
All amounts in KES.
"""

# ============================================================
# AUTH
# ============================================================

QUERY_USER_BY_USERNAME = """
SELECT user_id, username, full_name, email, phone,
       password_hash, role, is_active
FROM users
WHERE username = %s AND is_active = TRUE
"""

QUERY_UPDATE_LAST_LOGIN = """
UPDATE users SET last_login = NOW() WHERE user_id = %s
"""

QUERY_ALL_STAFF = """
SELECT user_id, full_name, username, email, phone, role, is_active,
       created_at, last_login
FROM users
ORDER BY role ASC, full_name ASC
"""

QUERY_ACTIVE_STAFF = """
SELECT user_id, full_name, role
FROM users
WHERE is_active = TRUE
ORDER BY full_name ASC
"""

QUERY_CREATE_USER = """
INSERT INTO users
(username, full_name, email, phone, password_hash, role)
VALUES (%s,%s,%s,%s,%s,%s)
"""

QUERY_UPDATE_USER_STATUS = """
UPDATE users SET is_active = %s WHERE user_id = %s
"""

# ============================================================
# DASHBOARD — OWNER REMOTE MONITORING
# ============================================================

# Today's headline numbers
QUERY_TODAY_SUMMARY = """
SELECT
    COUNT(*)                           AS txn_count,
    COALESCE(SUM(total_amount), 0)     AS total_revenue,
    COALESCE(SUM(discount_amount), 0)  AS total_discounts,
    COALESCE(SUM(total_amount - discount_amount
                 - (SELECT COALESCE(SUM(si.qty * p.buying_price),0)
                    FROM sale_items si
                    JOIN products p ON si.product_id = p.product_id
                    WHERE si.sale_id = s.sale_id)), 0) AS gross_profit,
    COUNT(DISTINCT served_by)          AS staff_members
FROM sales s
WHERE sale_date = CURDATE()
  AND status    = 'Completed'
"""

# Simpler profit query (revenue - cost of goods sold today)
QUERY_TODAY_PROFIT = """
SELECT
    COALESCE(SUM(s.total_amount), 0)                       AS revenue,
    COALESCE(SUM(si.qty * p.buying_price), 0)              AS cogs,
    COALESCE(SUM(s.total_amount), 0)
        - COALESCE(SUM(si.qty * p.buying_price), 0)        AS gross_profit
FROM sales s
JOIN sale_items si ON s.sale_id = si.sale_id
JOIN products p    ON si.product_id = p.product_id
WHERE s.sale_date = CURDATE()
  AND s.status    = 'Completed'
"""

QUERY_YESTERDAY_REVENUE = """
SELECT COALESCE(SUM(total_amount), 0) AS revenue
FROM sales
WHERE sale_date = DATE_SUB(CURDATE(), INTERVAL 1 DAY)
  AND status = 'Completed'
"""

QUERY_THIS_MONTH_SUMMARY = """
SELECT
    COUNT(*)                          AS txn_count,
    COALESCE(SUM(total_amount), 0)    AS revenue,
    COALESCE(SUM(discount_amount), 0) AS discounts,
    COUNT(DISTINCT served_by)         AS staff_members
FROM sales
WHERE MONTH(sale_date) = MONTH(CURDATE())
  AND YEAR(sale_date)  = YEAR(CURDATE())
  AND status = 'Completed'
"""

QUERY_THIS_MONTH_PROFIT = """
SELECT
    COALESCE(SUM(s.total_amount), 0)              AS revenue,
    COALESCE(SUM(si.qty * p.buying_price), 0)     AS cogs,
    COALESCE(SUM(s.total_amount), 0)
        - COALESCE(SUM(si.qty * p.buying_price),0) AS gross_profit
FROM sales s
JOIN sale_items si ON s.sale_id = si.sale_id
JOIN products p    ON si.product_id = p.product_id
WHERE MONTH(s.sale_date) = MONTH(CURDATE())
  AND YEAR(s.sale_date)  = YEAR(CURDATE())
  AND s.status = 'Completed'
"""

QUERY_THIS_MONTH_EXPENSES = """
SELECT COALESCE(SUM(amount), 0) AS total_expenses
FROM expenses
WHERE MONTH(expense_date) = MONTH(CURDATE())
  AND YEAR(expense_date)  = YEAR(CURDATE())
"""

# Hourly sales today (for owner to see when shop is busy)
QUERY_HOURLY_SALES_TODAY = """
SELECT
    HOUR(sale_time)                    AS hour_of_day,
    COUNT(*)                           AS txn_count,
    COALESCE(SUM(total_amount), 0)     AS revenue
FROM sales
WHERE sale_date = CURDATE()
  AND status    = 'Completed'
GROUP BY HOUR(sale_time)
ORDER BY hour_of_day ASC
"""

# Payment method split today
QUERY_TODAY_PAYMENT_METHODS = """
SELECT
    payment_method,
    COUNT(*)                       AS txn_count,
    COALESCE(SUM(total_amount), 0) AS total_amount
FROM sales
WHERE sale_date = CURDATE()
  AND status    = 'Completed'
GROUP BY payment_method
"""

# Last 7 days daily revenue
QUERY_LAST_7_DAYS = """
SELECT
    sale_date,
    COUNT(*)                       AS txn_count,
    COALESCE(SUM(total_amount), 0) AS revenue
FROM sales
WHERE sale_date >= DATE_SUB(CURDATE(), INTERVAL 6 DAY)
  AND status    = 'Completed'
GROUP BY sale_date
ORDER BY sale_date ASC
"""

# Last 30 days daily revenue
QUERY_LAST_30_DAYS = """
SELECT
    sale_date,
    COUNT(*)                       AS txn_count,
    COALESCE(SUM(total_amount), 0) AS revenue
FROM sales
WHERE sale_date >= DATE_SUB(CURDATE(), INTERVAL 29 DAY)
  AND status    = 'Completed'
GROUP BY sale_date
ORDER BY sale_date ASC
"""

# Monthly revenue trend (12 months)
QUERY_MONTHLY_TREND = """
SELECT
    DATE_FORMAT(sale_date, '%Y-%m-01')  AS month,
    YEAR(sale_date)                      AS yr,
    MONTH(sale_date)                     AS mo,
    COUNT(*)                             AS txn_count,
    COALESCE(SUM(total_amount), 0)       AS revenue
FROM sales
WHERE sale_date >= DATE_SUB(CURDATE(), INTERVAL 11 MONTH)
  AND status = 'Completed'
GROUP BY yr, mo, month
ORDER BY yr ASC, mo ASC
"""

# Low stock alert (stock <= reorder_level)
QUERY_LOW_STOCK = """
SELECT
    p.product_id,
    p.name,
    p.brand,
    p.sku,
    p.qty_in_stock,
    p.reorder_level,
    p.reorder_qty,
    p.selling_price,
    pc.name AS category
FROM products p
LEFT JOIN product_categories pc ON p.category_id = pc.category_id
WHERE p.qty_in_stock <= p.reorder_level
  AND p.is_active = TRUE
ORDER BY p.qty_in_stock ASC
"""

# Out of stock
QUERY_OUT_OF_STOCK = """
SELECT COUNT(*) AS count
FROM products
WHERE qty_in_stock = 0 AND is_active = TRUE
"""

# Staff on duty today
QUERY_STAFF_TODAY = """
SELECT
    u.full_name,
    u.role,
    sa.check_in,
    sa.check_out,
    COALESCE(sa.check_out IS NULL AND sa.check_in IS NOT NULL, FALSE) AS is_in,
    COUNT(DISTINCT s.sale_id)          AS sales_made,
    COALESCE(SUM(s.total_amount), 0)   AS revenue_generated
FROM users u
LEFT JOIN staff_attendance sa ON u.user_id = sa.user_id
    AND sa.work_date = CURDATE()
LEFT JOIN sales s ON s.served_by = u.user_id
    AND s.sale_date = CURDATE()
    AND s.status    = 'Completed'
WHERE u.is_active = TRUE
  AND u.role IN ('Staff','Manager')
GROUP BY u.user_id, u.full_name, u.role, sa.check_in, sa.check_out
ORDER BY sa.check_in ASC
"""

# Recent transactions (last 10)
QUERY_RECENT_SALES = """
SELECT
    s.sale_id,
    s.sale_time,
    u.full_name                       AS served_by,
    s.total_amount,
    s.payment_method,
    s.mpesa_ref,
    s.status
FROM sales s
LEFT JOIN users u     ON s.served_by   = u.user_id
WHERE s.sale_date = CURDATE()
ORDER BY s.sale_time DESC
LIMIT 15
"""

# Staff: only their own sales today (with amounts — they need to know what they collected)
QUERY_MY_SALES_TODAY = """
SELECT
    s.sale_id,
    s.sale_time,
    s.payment_method,
    s.mpesa_ref,
    s.status,
    s.total_amount,
    COALESCE(SUM(si.qty), 0) AS items_sold
FROM sales s
LEFT JOIN sale_items si ON s.sale_id = si.sale_id
WHERE s.served_by = %s
  AND s.sale_date = CURDATE()
  AND s.status    = 'Completed'
GROUP BY s.sale_id, s.sale_time, s.payment_method,
         s.mpesa_ref, s.status, s.total_amount
ORDER BY s.sale_time DESC
"""

# Staff: their own sales history (with amounts)
QUERY_MY_SALES_HISTORY = """
SELECT
    s.sale_id,
    s.sale_date,
    s.sale_time,
    s.payment_method,
    s.mpesa_ref,
    s.status,
    s.total_amount,
    COALESCE(SUM(si.qty), 0) AS items_sold
FROM sales s
LEFT JOIN sale_items si ON s.sale_id = si.sale_id
WHERE s.served_by = %s
  AND s.status    = 'Completed'
GROUP BY s.sale_id, s.sale_date, s.sale_time,
         s.payment_method, s.mpesa_ref, s.status, s.total_amount
ORDER BY s.sale_date DESC, s.sale_time DESC
"""

# ============================================================
# INVENTORY
# ============================================================

QUERY_ALL_PRODUCTS = """
SELECT
    p.product_id,
    pc.name                                           AS category,
    p.name,
    p.brand,
    p.sku,
    p.buying_price,
    p.selling_price,
    ROUND(p.selling_price - p.buying_price, 2)        AS margin,
    ROUND((p.selling_price - p.buying_price)
          / NULLIF(p.selling_price, 0) * 100, 1)      AS margin_pct,
    p.qty_in_stock,
    p.reorder_level,
    p.reorder_qty,
    p.unit,
    p.is_active,
    p.updated_at,
    CASE
        WHEN p.qty_in_stock = 0             THEN 'Out of Stock'
        WHEN p.qty_in_stock <= p.reorder_level THEN 'Low Stock'
        ELSE 'In Stock'
    END AS stock_status
FROM products p
LEFT JOIN product_categories pc ON p.category_id = pc.category_id
WHERE p.is_active = TRUE
ORDER BY stock_status ASC, p.name ASC
"""

QUERY_ALL_PRODUCTS_INCL_INACTIVE = """
SELECT
    p.product_id,
    pc.name                 AS category,
    p.name,
    p.brand,
    p.sku,
    p.buying_price,
    p.selling_price,
    p.qty_in_stock,
    p.reorder_level,
    p.unit,
    p.is_active
FROM products p
LEFT JOIN product_categories pc ON p.category_id = pc.category_id
ORDER BY p.name ASC
"""

QUERY_PRODUCT_BY_ID = """
SELECT p.*, pc.name AS category_name
FROM products p
LEFT JOIN product_categories pc ON p.category_id = pc.category_id
WHERE p.product_id = %s
"""

QUERY_ALL_CATEGORIES = """
SELECT category_id, name, description
FROM product_categories
ORDER BY name ASC
"""

QUERY_STOCK_VALUE = """
SELECT
    COALESCE(SUM(qty_in_stock * buying_price), 0)   AS cost_value,
    COALESCE(SUM(qty_in_stock * selling_price), 0)  AS retail_value,
    COUNT(*)                                          AS product_count,
    SUM(CASE WHEN qty_in_stock = 0 THEN 1 ELSE 0 END)             AS out_of_stock,
    SUM(CASE WHEN qty_in_stock > 0
              AND qty_in_stock <= reorder_level THEN 1 ELSE 0 END) AS low_stock
FROM products
WHERE is_active = TRUE
"""

QUERY_STOCK_MOVEMENTS = """
SELECT
    sm.movement_id,
    p.name         AS product_name,
    p.brand,
    sm.movement_type,
    sm.qty_change,
    sm.qty_before,
    sm.qty_after,
    sm.cost_per_unit,
    sm.notes,
    COALESCE(u.full_name, 'System') AS recorded_by,
    sm.created_at
FROM stock_movements sm
JOIN products p  ON sm.product_id  = p.product_id
LEFT JOIN users u ON sm.recorded_by = u.user_id
ORDER BY sm.created_at DESC
LIMIT 200
"""

QUERY_STOCK_MOVEMENTS_BY_PRODUCT = """
SELECT
    sm.movement_id,
    sm.movement_type,
    sm.qty_change,
    sm.qty_before,
    sm.qty_after,
    sm.cost_per_unit,
    sm.notes,
    COALESCE(u.full_name,'System') AS recorded_by,
    sm.created_at
FROM stock_movements sm
LEFT JOIN users u ON sm.recorded_by = u.user_id
WHERE sm.product_id = %s
ORDER BY sm.created_at DESC
"""

QUERY_ADD_PRODUCT = """
INSERT INTO products
(category_id, name, brand, sku, description, buying_price,
 selling_price, qty_in_stock, reorder_level, reorder_qty, unit)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
"""

QUERY_UPDATE_PRODUCT = """
UPDATE products
SET category_id=%s, name=%s, brand=%s, sku=%s, buying_price=%s,
    selling_price=%s, reorder_level=%s, reorder_qty=%s, unit=%s,
    description=%s, updated_at=NOW()
WHERE product_id=%s
"""

QUERY_RESTOCK = """
CALL restock_product(%s, %s, %s, %s, %s)
"""

QUERY_ADJUST_STOCK = """
UPDATE products
SET qty_in_stock = qty_in_stock + %s,
    updated_at   = NOW()
WHERE product_id = %s
"""

QUERY_LOG_MOVEMENT = """
INSERT INTO stock_movements
(product_id, movement_type, qty_change, qty_before, qty_after, notes, recorded_by)
VALUES (%s,%s,%s,%s,%s,%s,%s)
"""

QUERY_CATEGORY_STOCK = """
SELECT
    pc.name                                          AS category,
    COUNT(p.product_id)                              AS product_count,
    COALESCE(SUM(p.qty_in_stock), 0)                 AS total_units,
    COALESCE(SUM(p.qty_in_stock * p.buying_price),0) AS stock_value
FROM product_categories pc
LEFT JOIN products p ON p.category_id = pc.category_id AND p.is_active = TRUE
GROUP BY pc.category_id, pc.name
ORDER BY stock_value DESC
"""

# ============================================================
# SALES / POS
# ============================================================

QUERY_ADD_SALE = """
INSERT INTO sales
(served_by, subtotal, discount_amount, total_amount,
 amount_paid, change_given, payment_method, mpesa_ref,
 sale_date, sale_time, notes, status)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
"""

QUERY_ADD_SALE_ITEM = """
INSERT INTO sale_items (sale_id, product_id, qty, unit_price, line_total)
VALUES (%s,%s,%s,%s,%s)
"""

QUERY_LAST_SALE_ID = """
SELECT MAX(sale_id) FROM sales
"""

QUERY_ALL_SALES = """
SELECT
    s.sale_id,
    s.sale_date,
    s.sale_time,
    COALESCE(u.full_name,'—')        AS served_by,
    s.subtotal,
    s.discount_amount,
    s.total_amount,
    s.payment_method,
    s.mpesa_ref,
    s.status
FROM sales s
LEFT JOIN users u     ON s.served_by   = u.user_id
ORDER BY s.sale_date DESC, s.sale_time DESC
"""

QUERY_SALE_ITEMS = """
SELECT
    si.item_id,
    p.name         AS product_name,
    p.brand,
    si.qty,
    si.unit_price,
    si.line_total
FROM sale_items si
JOIN products p ON si.product_id = p.product_id
WHERE si.sale_id = %s
"""

QUERY_SALES_BY_DATE_RANGE = """
SELECT
    s.sale_id,
    s.sale_date,
    s.sale_time,
    COALESCE(u.full_name,'—')        AS served_by,
    s.total_amount,
    s.payment_method,
    s.status
FROM sales s
LEFT JOIN users u     ON s.served_by   = u.user_id
WHERE s.sale_date BETWEEN %s AND %s
ORDER BY s.sale_date DESC, s.sale_time DESC
"""

# ============================================================
# EXPENSES
# ============================================================

QUERY_ALL_EXPENSES = """
SELECT
    e.expense_id,
    e.category,
    e.description,
    e.amount,
    e.expense_date,
    e.payment_method,
    e.reference,
    COALESCE(u.full_name,'—') AS recorded_by,
    e.notes
FROM expenses e
LEFT JOIN users u ON e.recorded_by = u.user_id
ORDER BY e.expense_date DESC
"""

QUERY_EXPENSES_THIS_MONTH = """
SELECT
    category,
    COALESCE(SUM(amount),0) AS total,
    COUNT(*)                 AS count
FROM expenses
WHERE MONTH(expense_date) = MONTH(CURDATE())
  AND YEAR(expense_date)  = YEAR(CURDATE())
GROUP BY category
ORDER BY total DESC
"""

QUERY_ADD_EXPENSE = """
INSERT INTO expenses
(category, description, amount, expense_date, payment_method, reference, recorded_by, notes)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
"""

QUERY_EXPENSE_TREND = """
SELECT
    DATE_FORMAT(expense_date,'%Y-%m-01') AS month,
    COALESCE(SUM(amount),0)              AS total_expenses
FROM expenses
WHERE expense_date >= DATE_SUB(CURDATE(), INTERVAL 5 MONTH)
GROUP BY month
ORDER BY month ASC
"""

# ============================================================
# REPORTS
# ============================================================

QUERY_BEST_SELLERS = """
SELECT
    p.name,
    p.brand,
    pc.name                          AS category,
    SUM(si.qty)                      AS units_sold,
    SUM(si.line_total)               AS revenue,
    SUM(si.qty * p.buying_price)     AS cogs,
    SUM(si.line_total)
        - SUM(si.qty * p.buying_price) AS profit
FROM sale_items si
JOIN products p  ON si.product_id  = p.product_id
JOIN sales s     ON si.sale_id     = s.sale_id
LEFT JOIN product_categories pc ON p.category_id = pc.category_id
WHERE s.status    = 'Completed'
  AND s.sale_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
GROUP BY p.product_id, p.name, p.brand, pc.name
ORDER BY units_sold DESC
LIMIT 20
"""

QUERY_BEST_SELLERS_ALL_TIME = """
SELECT
    p.name,
    p.brand,
    SUM(si.qty)                      AS units_sold,
    SUM(si.line_total)               AS revenue,
    SUM(si.line_total)
        - SUM(si.qty * p.buying_price) AS profit
FROM sale_items si
JOIN products p ON si.product_id = p.product_id
JOIN sales s    ON si.sale_id    = s.sale_id
WHERE s.status = 'Completed'
GROUP BY p.product_id, p.name, p.brand
ORDER BY units_sold DESC
LIMIT 20
"""

QUERY_CATEGORY_SALES = """
SELECT
    pc.name                               AS category,
    COUNT(DISTINCT s.sale_id)             AS transactions,
    SUM(si.qty)                           AS units_sold,
    COALESCE(SUM(si.line_total),0)        AS revenue,
    COALESCE(SUM(si.qty * p.buying_price),0) AS cogs,
    COALESCE(SUM(si.line_total),0)
        - COALESCE(SUM(si.qty*p.buying_price),0) AS profit
FROM product_categories pc
LEFT JOIN products p     ON p.category_id  = pc.category_id
LEFT JOIN sale_items si  ON si.product_id  = p.product_id
LEFT JOIN sales s        ON si.sale_id     = s.sale_id
    AND s.status = 'Completed'
    AND s.sale_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
GROUP BY pc.category_id, pc.name
ORDER BY revenue DESC
"""

QUERY_STAFF_PERFORMANCE = """
SELECT
    u.full_name,
    u.role,
    COUNT(DISTINCT s.sale_id)              AS sales_count,
    COALESCE(SUM(s.total_amount),0)        AS revenue,
    COALESCE(AVG(s.total_amount),0)        AS avg_sale,
    COALESCE(SUM(s.discount_amount),0)     AS discounts_given,
    COUNT(DISTINCT s.sale_date)            AS days_worked
FROM users u
LEFT JOIN sales s ON s.served_by = u.user_id
    AND s.status    = 'Completed'
    AND s.sale_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
WHERE u.is_active = TRUE
  AND u.role IN ('Staff','Manager')
GROUP BY u.user_id, u.full_name, u.role
ORDER BY revenue DESC
"""

QUERY_PROFIT_LOSS = """
SELECT
    DATE_FORMAT(s.sale_date,'%Y-%m-01')   AS month,
    COALESCE(SUM(s.total_amount),0)        AS revenue,
    COALESCE(SUM(si.qty*p.buying_price),0) AS cogs,
    COALESCE(SUM(s.total_amount),0)
        - COALESCE(SUM(si.qty*p.buying_price),0) AS gross_profit,
    COALESCE((
        SELECT SUM(e.amount)
        FROM expenses e
        WHERE DATE_FORMAT(e.expense_date,'%Y-%m-01')
              = DATE_FORMAT(s.sale_date,'%Y-%m-01')
    ),0) AS operating_expenses,
    COALESCE(SUM(s.total_amount),0)
        - COALESCE(SUM(si.qty*p.buying_price),0)
        - COALESCE((
            SELECT SUM(e.amount) FROM expenses e
            WHERE DATE_FORMAT(e.expense_date,'%Y-%m-01')
                  = DATE_FORMAT(s.sale_date,'%Y-%m-01')
          ),0) AS net_profit
FROM sales s
JOIN sale_items si ON s.sale_id     = si.sale_id
JOIN products p    ON si.product_id = p.product_id
WHERE s.status = 'Completed'
  AND s.sale_date >= DATE_SUB(CURDATE(), INTERVAL 5 MONTH)
GROUP BY month
ORDER BY month ASC
"""

QUERY_PAYMENT_METHOD_REPORT = """
SELECT
    payment_method,
    COUNT(*)                       AS txn_count,
    COALESCE(SUM(total_amount),0)  AS total_amount,
    ROUND(COALESCE(SUM(total_amount),0)
        / NULLIF((SELECT SUM(total_amount) FROM sales
                  WHERE status='Completed'
                    AND MONTH(sale_date)=MONTH(CURDATE())
                    AND YEAR(sale_date)=YEAR(CURDATE())),0)*100,1) AS pct
FROM sales
WHERE status = 'Completed'
  AND MONTH(sale_date) = MONTH(CURDATE())
  AND YEAR(sale_date)  = YEAR(CURDATE())
GROUP BY payment_method
ORDER BY total_amount DESC
"""

QUERY_HOURLY_HEATMAP = """
SELECT
    DAYOFWEEK(sale_date) AS dow,          -- 1=Sun … 7=Sat
    HOUR(sale_time)       AS hour_of_day,
    COUNT(*)              AS txn_count,
    COALESCE(SUM(total_amount),0) AS revenue
FROM sales
WHERE status    = 'Completed'
  AND sale_date >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
GROUP BY dow, hour_of_day
ORDER BY dow ASC, hour_of_day ASC
"""

# ============================================================
# STAFF ATTENDANCE
# ============================================================

QUERY_CHECK_IN = """
INSERT INTO staff_attendance (user_id, work_date, check_in)
VALUES (%s, CURDATE(), CURTIME())
ON DUPLICATE KEY UPDATE check_in = CURTIME()
"""

QUERY_CHECK_OUT = """
UPDATE staff_attendance
SET check_out = CURTIME()
WHERE user_id = %s AND work_date = CURDATE()
"""

QUERY_MY_ATTENDANCE_TODAY = """
SELECT check_in, check_out
FROM staff_attendance
WHERE user_id = %s AND work_date = CURDATE()
"""

QUERY_ATTENDANCE_HISTORY = """
SELECT
    u.full_name,
    sa.work_date,
    sa.check_in,
    sa.check_out,
    TIMEDIFF(sa.check_out, sa.check_in) AS hours_worked
FROM staff_attendance sa
JOIN users u ON sa.user_id = u.user_id
WHERE sa.work_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
ORDER BY sa.work_date DESC, sa.check_in ASC
"""
