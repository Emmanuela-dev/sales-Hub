"""
SQL Queries Module
Professional analytics and reporting queries for Sales Intelligence Hub
"""

# ============================================
# DASHBOARD QUERIES
# ============================================

QUERY_TOTAL_SALES = """
SELECT COALESCE(SUM(sale_amount), 0) as total_sales
FROM customer_sales
WHERE DATE(sale_date) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
"""

QUERY_TOTAL_RECEIVED = """
SELECT COALESCE(SUM(amount), 0) as total_received
FROM payment_splits
WHERE DATE(payment_date) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
"""

QUERY_TOTAL_PENDING = """
SELECT COALESCE(SUM(pending_amount), 0) as total_pending
FROM customer_sales
WHERE payment_status IN ('Open', 'Partial')
"""

QUERY_COLLECTION_PERCENTAGE = """
SELECT 
    ROUND(
        (COALESCE(SUM(received_amount), 0) / NULLIF(SUM(sale_amount), 0)) * 100, 
        2
    ) as collection_percentage
FROM customer_sales
WHERE DATE(sale_date) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
"""

# ============================================
# BRANCH ANALYTICS
# ============================================

QUERY_BRANCH_WISE_SALES = """
SELECT 
    b.branch_id,
    b.branch_name,
    b.branch_code,
    COUNT(cs.sale_id) as total_sales_count,
    COALESCE(SUM(cs.sale_amount), 0) as total_sales_amount,
    COALESCE(SUM(cs.received_amount), 0) as total_received,
    COALESCE(SUM(cs.pending_amount), 0) as total_pending,
    ROUND(
        (COALESCE(SUM(cs.received_amount), 0) / NULLIF(SUM(cs.sale_amount), 0)) * 100,
        2
    ) as collection_percentage
FROM branches b
LEFT JOIN customer_sales cs ON b.branch_id = cs.branch_id
WHERE DATE(cs.sale_date) >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
GROUP BY b.branch_id, b.branch_name, b.branch_code
ORDER BY total_sales_amount DESC
"""

QUERY_TOP_BRANCHES = """
SELECT 
    b.branch_id,
    b.branch_name,
    COALESCE(SUM(cs.sale_amount), 0) as total_sales,
    COUNT(DISTINCT cs.sale_id) as sales_count
FROM branches b
LEFT JOIN customer_sales cs ON b.branch_id = cs.branch_id
WHERE DATE(cs.sale_date) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
GROUP BY b.branch_id, b.branch_name
ORDER BY total_sales DESC
LIMIT 10
"""

# ============================================
# PAYMENT METHOD ANALYSIS
# ============================================

QUERY_PAYMENT_METHOD_BREAKDOWN = """
SELECT 
    payment_method,
    COUNT(*) as transaction_count,
    COALESCE(SUM(amount), 0) as total_amount,
    ROUND(
        (COALESCE(SUM(amount), 0) / (SELECT SUM(amount) FROM payment_splits)) * 100,
        2
    ) as percentage
FROM payment_splits
WHERE DATE(payment_date) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
GROUP BY payment_method
ORDER BY total_amount DESC
"""

# ============================================
# SALES STATUS DISTRIBUTION
# ============================================

QUERY_PAYMENT_STATUS_DISTRIBUTION = """
SELECT 
    payment_status,
    COUNT(*) as count,
    COALESCE(SUM(sale_amount), 0) as total_amount,
    ROUND(
        (COUNT(*) / (SELECT COUNT(*) FROM customer_sales WHERE DATE(sale_date) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY))) * 100,
        2
    ) as percentage
FROM customer_sales
WHERE DATE(sale_date) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
GROUP BY payment_status
"""

# ============================================
# MONTHLY TRENDS
# ============================================

QUERY_MONTHLY_SALES_TREND = """
SELECT 
    DATE_FORMAT(sale_date, '%Y-%m-01') as month,
    YEAR(sale_date) as year,
    MONTH(sale_date) as month_num,
    COUNT(*) as sales_count,
    COALESCE(SUM(sale_amount), 0) as total_sales,
    COALESCE(SUM(received_amount), 0) as total_received,
    COALESCE(SUM(pending_amount), 0) as total_pending
FROM customer_sales
WHERE DATE(sale_date) >= DATE_SUB(CURDATE(), INTERVAL 365 DAY)
GROUP BY year, month_num, month
ORDER BY year DESC, month_num DESC
"""

QUERY_MONTHLY_REVENUE_TREND = """
SELECT 
    DATE_FORMAT(DATE(payment_date), '%Y-%m') as month,
    COUNT(*) as payment_count,
    COALESCE(SUM(amount), 0) as revenue
FROM payment_splits
WHERE DATE(payment_date) >= DATE_SUB(CURDATE(), INTERVAL 365 DAY)
GROUP BY month
ORDER BY month DESC
"""

# ============================================
# PENDING COLLECTIONS ANALYSIS
# ============================================

QUERY_PENDING_COLLECTIONS = """
SELECT 
    cs.sale_id,
    cs.customer_name,
    b.branch_name,
    cs.sale_amount,
    cs.received_amount,
    cs.pending_amount,
    cs.payment_status,
    cs.sale_date,
    DATEDIFF(CURDATE(), cs.sale_date) as days_pending
FROM customer_sales cs
JOIN branches b ON cs.branch_id = b.branch_id
WHERE cs.payment_status IN ('Open', 'Partial')
ORDER BY cs.pending_amount DESC
"""

QUERY_OVERDUE_COLLECTIONS = """
SELECT 
    cs.sale_id,
    cs.customer_name,
    b.branch_name,
    cs.sale_amount,
    cs.received_amount,
    cs.pending_amount,
    DATEDIFF(CURDATE(), cs.sale_date) as days_overdue
FROM customer_sales cs
JOIN branches b ON cs.branch_id = b.branch_id
WHERE cs.payment_status IN ('Open', 'Partial')
AND DATEDIFF(CURDATE(), cs.sale_date) > 30
ORDER BY days_overdue DESC
"""

# ============================================
# REVENUE ANALYSIS
# ============================================

QUERY_TOTAL_REVENUE_ANALYSIS = """
SELECT 
    COALESCE(SUM(sale_amount), 0) as total_sales,
    COALESCE(SUM(received_amount), 0) as total_received,
    COALESCE(SUM(pending_amount), 0) as total_pending,
    ROUND(
        (COALESCE(SUM(received_amount), 0) / NULLIF(SUM(sale_amount), 0)) * 100,
        2
    ) as collection_rate,
    COUNT(*) as total_transactions
FROM customer_sales
"""

QUERY_HIGHEST_SALES = """
SELECT 
    cs.sale_id,
    cs.customer_name,
    b.branch_name,
    cs.product_category,
    cs.sale_amount,
    cs.received_amount,
    cs.payment_status,
    cs.sale_date
FROM customer_sales cs
JOIN branches b ON cs.branch_id = b.branch_id
ORDER BY cs.sale_amount DESC
LIMIT 20
"""

# ============================================
# CUSTOMER INSIGHTS
# ============================================

QUERY_TOP_CUSTOMERS = """
SELECT 
    cs.customer_name,
    b.branch_name,
    COUNT(cs.sale_id) as purchase_count,
    COALESCE(SUM(cs.sale_amount), 0) as total_purchase_amount,
    COALESCE(SUM(cs.received_amount), 0) as total_paid
FROM customer_sales cs
JOIN branches b ON cs.branch_id = b.branch_id
GROUP BY cs.customer_name, b.branch_name
ORDER BY total_purchase_amount DESC
LIMIT 15
"""

QUERY_CUSTOMERS_HIGH_PENDING = """
SELECT 
    cs.customer_name,
    b.branch_name,
    cs.sale_amount,
    cs.received_amount,
    cs.pending_amount,
    cs.payment_status,
    cs.sale_date
FROM customer_sales cs
JOIN branches b ON cs.branch_id = b.branch_id
WHERE cs.payment_status IN ('Open', 'Partial')
ORDER BY cs.pending_amount DESC
LIMIT 20
"""

# ============================================
# OPEN VS CLOSED SALES
# ============================================

QUERY_OPEN_CLOSED_RATIO = """
SELECT 
    SUM(CASE WHEN payment_status = 'Closed' THEN 1 ELSE 0 END) as closed_count,
    SUM(CASE WHEN payment_status IN ('Open', 'Partial') THEN 1 ELSE 0 END) as open_count,
    COUNT(*) as total_sales,
    ROUND(
        (SUM(CASE WHEN payment_status = 'Closed' THEN 1 ELSE 0 END) / COUNT(*)) * 100,
        2
    ) as closed_percentage
FROM customer_sales
WHERE DATE(sale_date) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
"""

# ============================================
# BRANCH PERFORMANCE METRICS
# ============================================

QUERY_BRANCH_EFFICIENCY = """
SELECT 
    b.branch_id,
    b.branch_name,
    COUNT(DISTINCT cs.sale_id) as total_sales,
    COUNT(DISTINCT CASE WHEN cs.payment_status = 'Closed' THEN cs.sale_id END) as closed_sales,
    ROUND(
        (COUNT(DISTINCT CASE WHEN cs.payment_status = 'Closed' THEN cs.sale_id END) / 
         COUNT(DISTINCT cs.sale_id)) * 100,
        2
    ) as closing_percentage,
    ROUND(AVG(DATEDIFF(CURDATE(), cs.sale_date)), 0) as avg_days_open
FROM branches b
LEFT JOIN customer_sales cs ON b.branch_id = cs.branch_id
WHERE DATE(cs.sale_date) >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
GROUP BY b.branch_id, b.branch_name
ORDER BY closing_percentage DESC
"""

# ============================================
# REVENUE GROWTH ANALYSIS
# ============================================

QUERY_REVENUE_GROWTH = """
SELECT 
    DATE_FORMAT(DATE(sale_date), '%Y-%m') as month,
    COUNT(*) as sales_count,
    COALESCE(SUM(sale_amount), 0) as monthly_sales,
    LAG(SUM(sale_amount)) OVER (ORDER BY DATE_FORMAT(DATE(sale_date), '%Y-%m')) as previous_month_sales,
    ROUND(
        ((SUM(sale_amount) - LAG(SUM(sale_amount)) OVER (ORDER BY DATE_FORMAT(DATE(sale_date), '%Y-%m'))) / 
         LAG(SUM(sale_amount)) OVER (ORDER BY DATE_FORMAT(DATE(sale_date), '%Y-%m'))) * 100,
        2
    ) as growth_percentage
FROM customer_sales
WHERE DATE(sale_date) >= DATE_SUB(CURDATE(), INTERVAL 365 DAY)
GROUP BY month
ORDER BY month DESC
"""

# ============================================
# CATEGORY ANALYSIS
# ============================================

QUERY_PRODUCT_CATEGORY_BREAKDOWN = """
SELECT 
    product_category,
    COUNT(*) as count,
    COALESCE(SUM(sale_amount), 0) as total_amount,
    COALESCE(SUM(received_amount), 0) as total_received,
    ROUND(
        (COALESCE(SUM(received_amount), 0) / NULLIF(SUM(sale_amount), 0)) * 100,
        2
    ) as collection_rate
FROM customer_sales
WHERE DATE(sale_date) >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
GROUP BY product_category
ORDER BY total_amount DESC
"""

# ============================================
# COLLECTION EFFICIENCY
# ============================================

QUERY_COLLECTION_EFFICIENCY = """
SELECT 
    b.branch_name,
    COUNT(DISTINCT cs.sale_id) as total_sales,
    COUNT(DISTINCT CASE WHEN cs.payment_status = 'Closed' THEN cs.sale_id END) as collected_sales,
    COALESCE(SUM(cs.sale_amount), 0) as total_amount,
    COALESCE(SUM(cs.received_amount), 0) as collected_amount,
    ROUND(
        (COALESCE(SUM(cs.received_amount), 0) / NULLIF(SUM(cs.sale_amount), 0)) * 100,
        2
    ) as collection_percentage,
    ROUND(
        AVG(DATEDIFF(MAX(ps.payment_date), cs.sale_date)),
        1
    ) as avg_payment_days
FROM branches b
LEFT JOIN customer_sales cs ON b.branch_id = cs.branch_id
LEFT JOIN payment_splits ps ON cs.sale_id = ps.sale_id
WHERE DATE(cs.sale_date) >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
GROUP BY b.branch_name
ORDER BY collection_percentage DESC
"""

# ============================================
# SALES BY DATE RANGE QUERIES
# ============================================

QUERY_SALES_BY_DATE_RANGE = """
SELECT 
    cs.sale_id,
    cs.customer_name,
    b.branch_name,
    cs.sale_amount,
    cs.received_amount,
    cs.pending_amount,
    cs.payment_status,
    cs.sale_date
FROM customer_sales cs
JOIN branches b ON cs.branch_id = b.branch_id
WHERE DATE(cs.sale_date) BETWEEN %s AND %s
ORDER BY cs.sale_date DESC
"""

QUERY_PAYMENTS_BY_DATE_RANGE = """
SELECT 
    ps.payment_id,
    cs.customer_name,
    b.branch_name,
    ps.amount,
    ps.payment_method,
    ps.payment_date,
    ps.transaction_reference
FROM payment_splits ps
JOIN customer_sales cs ON ps.sale_id = cs.sale_id
JOIN branches b ON ps.branch_id = b.branch_id
WHERE DATE(ps.payment_date) BETWEEN %s AND %s
ORDER BY ps.payment_date DESC
"""

# ============================================
# BRANCH SPECIFIC QUERIES
# ============================================

QUERY_BRANCH_SALES = """
SELECT 
    cs.sale_id,
    cs.customer_name,
    cs.sale_amount,
    cs.received_amount,
    cs.pending_amount,
    cs.payment_status,
    cs.sale_date
FROM customer_sales cs
WHERE cs.branch_id = %s
ORDER BY cs.sale_date DESC
"""

QUERY_BRANCH_METRICS = """
SELECT 
    COALESCE(SUM(cs.sale_amount), 0) as total_sales,
    COALESCE(SUM(cs.received_amount), 0) as total_received,
    COALESCE(SUM(cs.pending_amount), 0) as total_pending,
    COUNT(*) as total_transactions,
    COUNT(DISTINCT CASE WHEN cs.payment_status = 'Closed' THEN cs.sale_id END) as closed_transactions
FROM customer_sales cs
WHERE cs.branch_id = %s
"""

# ============================================
# USER ROLE AND PERMISSION QUERIES
# ============================================

QUERY_USER_BY_USERNAME = """
SELECT user_id, username, email, role, branch_id, is_active, password_hash
FROM users
WHERE username = %s AND is_active = TRUE
"""

QUERY_VERIFY_USER = """
SELECT user_id, username, role, branch_id
FROM users
WHERE username = %s AND is_active = TRUE
"""

# ============================================
# INSERT QUERIES (Parameterized)
# ============================================

QUERY_ADD_SALE = """
INSERT INTO customer_sales 
(branch_id, customer_name, customer_phone, customer_email, product_category, product_description, sale_amount, sale_date, payment_status, notes)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

QUERY_ADD_PAYMENT = """
INSERT INTO payment_splits 
(sale_id, branch_id, amount, payment_method, payment_date, transaction_reference, notes)
VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

# ============================================
# UPDATE QUERIES
# ============================================

QUERY_UPDATE_SALE = """
UPDATE customer_sales
SET customer_name = %s, customer_phone = %s, customer_email = %s, 
    product_category = %s, product_description = %s, notes = %s
WHERE sale_id = %s
"""

# ============================================
# ALL SALES WITH DETAILS
# ============================================

QUERY_ALL_SALES_WITH_DETAILS = """
SELECT 
    cs.sale_id,
    cs.customer_name,
    cs.customer_phone,
    cs.customer_email,
    b.branch_name,
    cs.product_category,
    cs.product_description,
    cs.sale_amount,
    cs.received_amount,
    cs.pending_amount,
    cs.payment_status,
    cs.sale_date,
    cs.created_at
FROM customer_sales cs
JOIN branches b ON cs.branch_id = b.branch_id
ORDER BY cs.created_at DESC
"""

QUERY_ALL_PAYMENTS_WITH_DETAILS = """
SELECT 
    ps.payment_id,
    cs.sale_id,
    cs.customer_name,
    b.branch_name,
    ps.amount,
    ps.payment_method,
    ps.payment_date,
    ps.transaction_reference,
    ps.notes,
    ps.created_at
FROM payment_splits ps
JOIN customer_sales cs ON ps.sale_id = cs.sale_id
JOIN branches b ON ps.branch_id = b.branch_id
ORDER BY ps.created_at DESC
"""

# ============================================
# GET BRANCHES
# ============================================

QUERY_ALL_BRANCHES = """
SELECT branch_id, branch_name, branch_code, location
FROM branches
ORDER BY branch_name ASC
"""

QUERY_GET_BRANCH_BY_ID = """
SELECT branch_id, branch_name, branch_code, location, branch_manager, contact_phone, email
FROM branches
WHERE branch_id = %s
"""
