-- ============================================================
-- Glamour Hub - Beauty Business Management System
-- Schema v1.0 | Single Branch | Currency: KES | MariaDB
-- ============================================================

CREATE DATABASE IF NOT EXISTS glamour_hub;
USE glamour_hub;

-- ============================================================
-- TABLE: users (owner + staff accounts)
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    user_id       INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    full_name     VARCHAR(100) NOT NULL,
    email         VARCHAR(100),
    phone         VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    role          ENUM('Owner', 'Manager', 'Staff') NOT NULL DEFAULT 'Staff',
    is_active     BOOLEAN DEFAULT TRUE,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login    TIMESTAMP NULL,
    INDEX idx_username (username),
    INDEX idx_role     (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: product_categories
-- ============================================================
CREATE TABLE IF NOT EXISTS product_categories (
    category_id   INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(100) NOT NULL UNIQUE,
    description   TEXT,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: products (beauty inventory items)
-- ============================================================
CREATE TABLE IF NOT EXISTS products (
    product_id       INT AUTO_INCREMENT PRIMARY KEY,
    category_id      INT NULL,
    name             VARCHAR(150) NOT NULL,
    brand            VARCHAR(100),
    sku              VARCHAR(50) UNIQUE,
    description      TEXT,
    buying_price     DECIMAL(10,2) NOT NULL DEFAULT 0.00,  -- cost price KES
    selling_price    DECIMAL(10,2) NOT NULL,               -- retail price KES
    qty_in_stock     INT NOT NULL DEFAULT 0,
    reorder_level    INT NOT NULL DEFAULT 5,               -- alert when stock <= this
    reorder_qty      INT NOT NULL DEFAULT 10,              -- suggested restock qty
    unit             VARCHAR(30) DEFAULT 'piece',          -- piece, bottle, set, ml, etc.
    image_url        VARCHAR(255),
    is_active        BOOLEAN DEFAULT TRUE,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_product_category
        FOREIGN KEY (category_id) REFERENCES product_categories(category_id)
        ON DELETE SET NULL,
    INDEX idx_product_name     (name),
    INDEX idx_product_category (category_id),
    INDEX idx_product_sku      (sku),
    INDEX idx_product_stock    (qty_in_stock)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: sales (each transaction / receipt)
-- ============================================================
CREATE TABLE IF NOT EXISTS sales (
    sale_id          INT AUTO_INCREMENT PRIMARY KEY,
    served_by        INT NULL,                        -- staff user_id
    subtotal         DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    discount_amount  DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    total_amount     DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    amount_paid      DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    change_given     DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    payment_method   ENUM('M-Pesa','Cash','Card','Split') DEFAULT 'Cash',
    mpesa_ref        VARCHAR(20),
    sale_date        DATE NOT NULL,
    sale_time        TIME NOT NULL,
    notes            TEXT,
    status           ENUM('Completed','Refunded','Void') DEFAULT 'Completed',
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sale_staff    FOREIGN KEY (served_by)   REFERENCES users(user_id)         ON DELETE SET NULL,
    INDEX idx_sale_date    (sale_date),
    INDEX idx_sale_staff   (served_by),
    INDEX idx_sale_method  (payment_method)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: sale_items (line items per sale)
-- ============================================================
CREATE TABLE IF NOT EXISTS sale_items (
    item_id       INT AUTO_INCREMENT PRIMARY KEY,
    sale_id       INT NOT NULL,
    product_id    INT NOT NULL,
    qty           INT NOT NULL DEFAULT 1,
    unit_price    DECIMAL(10,2) NOT NULL,   -- price at time of sale
    line_total    DECIMAL(12,2) NOT NULL,   -- qty * unit_price
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_item_sale    FOREIGN KEY (sale_id)    REFERENCES sales(sale_id)    ON DELETE CASCADE,
    CONSTRAINT fk_item_product FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT,
    INDEX idx_item_sale    (sale_id),
    INDEX idx_item_product (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: stock_movements (full audit trail of inventory changes)
-- ============================================================
CREATE TABLE IF NOT EXISTS stock_movements (
    movement_id    INT AUTO_INCREMENT PRIMARY KEY,
    product_id     INT NOT NULL,
    movement_type  ENUM('Restock','Sale','Adjustment','Return','Damage') NOT NULL,
    qty_change     INT NOT NULL,           -- positive = in, negative = out
    qty_before     INT NOT NULL,
    qty_after      INT NOT NULL,
    reference_id   INT NULL,              -- sale_id or purchase_id
    cost_per_unit  DECIMAL(10,2) NULL,    -- for restocks
    notes          TEXT,
    recorded_by    INT NULL,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_movement_product  FOREIGN KEY (product_id)  REFERENCES products(product_id) ON DELETE CASCADE,
    CONSTRAINT fk_movement_recorder FOREIGN KEY (recorded_by) REFERENCES users(user_id)       ON DELETE SET NULL,
    INDEX idx_movement_product (product_id),
    INDEX idx_movement_type    (movement_type),
    INDEX idx_movement_date    (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: expenses (business costs: rent, supplies, salaries, etc.)
-- ============================================================
CREATE TABLE IF NOT EXISTS expenses (
    expense_id     INT AUTO_INCREMENT PRIMARY KEY,
    category       ENUM('Rent','Salaries','Utilities','Stock Purchase',
                        'Marketing','Equipment','Transport','Other') NOT NULL,
    description    VARCHAR(255) NOT NULL,
    amount         DECIMAL(12,2) NOT NULL,   -- KES
    expense_date   DATE NOT NULL,
    payment_method ENUM('M-Pesa','Cash','Bank Transfer') DEFAULT 'Cash',
    reference      VARCHAR(100),
    recorded_by    INT NULL,
    notes          TEXT,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_expense_user FOREIGN KEY (recorded_by) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_expense_date     (expense_date),
    INDEX idx_expense_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: staff_attendance (track who opened/closed the shop)
-- ============================================================
CREATE TABLE IF NOT EXISTS staff_attendance (
    attendance_id  INT AUTO_INCREMENT PRIMARY KEY,
    user_id        INT NOT NULL,
    work_date      DATE NOT NULL,
    check_in       TIME NULL,
    check_out      TIME NULL,
    notes          TEXT,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_attendance_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE KEY uq_user_date (user_id, work_date),
    INDEX idx_attendance_date (work_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: mpesa_transactions (track STK push requests & statuses)
-- ============================================================
CREATE TABLE IF NOT EXISTS mpesa_transactions (
    id                   INT AUTO_INCREMENT PRIMARY KEY,
    checkout_request_id  VARCHAR(100) NOT NULL UNIQUE,
    merchant_request_id  VARCHAR(100) NULL,
    phone_number         VARCHAR(20)  NOT NULL,
    amount               DECIMAL(12,2) NOT NULL,
    status               ENUM('PENDING', 'COMPLETED', 'FAILED', 'CANCELLED') DEFAULT 'PENDING',
    mpesa_receipt_number VARCHAR(50)  NULL,
    result_desc          TEXT NULL,
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_mpesa_checkout (checkout_request_id),
    INDEX idx_mpesa_status   (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TRIGGERS
-- ============================================================

-- 1. After a sale_item is inserted: deduct stock, log movement
DROP TRIGGER IF EXISTS after_sale_item_insert;
DELIMITER $$
CREATE TRIGGER after_sale_item_insert
AFTER INSERT ON sale_items
FOR EACH ROW
BEGIN
    DECLARE v_before INT;
    SELECT qty_in_stock INTO v_before FROM products WHERE product_id = NEW.product_id;
    UPDATE products
    SET qty_in_stock = qty_in_stock - NEW.qty,
        updated_at   = NOW()
    WHERE product_id = NEW.product_id;
    INSERT INTO stock_movements
        (product_id, movement_type, qty_change, qty_before, qty_after, reference_id)
    VALUES
        (NEW.product_id, 'Sale', -NEW.qty, v_before, v_before - NEW.qty, NEW.sale_id);
END $$
DELIMITER ;

-- 2. Stock restock movement logger (called manually via execute_query)
-- Used when recording a restock purchase
DROP PROCEDURE IF EXISTS restock_product;
DELIMITER $$
CREATE PROCEDURE restock_product(
    IN p_product_id  INT,
    IN p_qty         INT,
    IN p_cost        DECIMAL(10,2),
    IN p_notes       TEXT,
    IN p_user_id     INT
)
BEGIN
    DECLARE v_before INT;
    SELECT qty_in_stock INTO v_before FROM products WHERE product_id = p_product_id;
    UPDATE products
    SET qty_in_stock  = qty_in_stock + p_qty,
        buying_price  = IF(p_cost > 0, p_cost, buying_price),
        updated_at    = NOW()
    WHERE product_id = p_product_id;
    INSERT INTO stock_movements
        (product_id, movement_type, qty_change, qty_before, qty_after,
         cost_per_unit, notes, recorded_by)
    VALUES
        (p_product_id, 'Restock', p_qty, v_before, v_before + p_qty,
         p_cost, p_notes, p_user_id);
END $$
DELIMITER ;
