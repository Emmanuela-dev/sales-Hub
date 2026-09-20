-- Sales Intelligence Hub Database Schema
-- Compatible with MariaDB / MySQL
-- ============================================

-- Create Database
CREATE DATABASE IF NOT EXISTS sales_intelligence_hub;
USE sales_intelligence_hub;

-- ============================================
-- TABLE: branches
-- Purpose: Store branch information
-- (created before users and customer_sales so FKs resolve)
-- ============================================
CREATE TABLE IF NOT EXISTS branches (
    branch_id   INT AUTO_INCREMENT PRIMARY KEY,
    branch_name VARCHAR(100) NOT NULL UNIQUE,
    branch_code VARCHAR(20)  NOT NULL UNIQUE,
    location    VARCHAR(150),
    branch_manager VARCHAR(100),
    contact_phone  VARCHAR(20),
    email          VARCHAR(100),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_branch_code (branch_code),
    INDEX idx_branch_name (branch_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLE: users
-- Purpose: Store user authentication and roles
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    user_id       INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    email         VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role          ENUM('Super Admin', 'Admin', 'User') NOT NULL DEFAULT 'User',
    branch_id     INT NULL,
    is_active     BOOLEAN DEFAULT TRUE,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login    TIMESTAMP NULL,
    CONSTRAINT fk_users_branch
        FOREIGN KEY (branch_id) REFERENCES branches(branch_id) ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX idx_username  (username),
    INDEX idx_role      (role),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLE: customer_sales
-- Purpose: Store sales transactions
-- Note: received_amount and pending_amount are plain columns
--       kept up-to-date by triggers in triggers.sql
-- ============================================
CREATE TABLE IF NOT EXISTS customer_sales (
    sale_id              INT AUTO_INCREMENT PRIMARY KEY,
    branch_id            INT            NOT NULL,
    customer_name        VARCHAR(100)   NOT NULL,
    customer_phone       VARCHAR(20),
    customer_email       VARCHAR(100),
    product_category     VARCHAR(50),
    product_description  VARCHAR(255),
    sale_amount          DECIMAL(12, 2) NOT NULL,
    sale_date            DATE           NOT NULL,
    payment_status       ENUM('Open', 'Partial', 'Closed') DEFAULT 'Open',
    notes                TEXT,
    received_amount      DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    pending_amount       DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_cs_branch
        FOREIGN KEY (branch_id) REFERENCES branches(branch_id) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_branch_id      (branch_id),
    INDEX idx_payment_status (payment_status),
    INDEX idx_sale_date      (sale_date),
    INDEX idx_customer_name  (customer_name),
    INDEX idx_cs_branch_date (branch_id, sale_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLE: payment_splits
-- Purpose: Store split payments for sales
-- ============================================
CREATE TABLE IF NOT EXISTS payment_splits (
    payment_id            INT AUTO_INCREMENT PRIMARY KEY,
    sale_id               INT            NOT NULL,
    branch_id             INT            NOT NULL,
    amount                DECIMAL(12, 2) NOT NULL,
    payment_method        ENUM('Cash', 'UPI', 'Card') DEFAULT 'Cash',
    payment_date          DATE           NOT NULL,
    transaction_reference VARCHAR(100),
    notes                 TEXT,
    created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_ps_sale
        FOREIGN KEY (sale_id)   REFERENCES customer_sales(sale_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_ps_branch
        FOREIGN KEY (branch_id) REFERENCES branches(branch_id)     ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_sale_id        (sale_id),
    INDEX idx_branch_id      (branch_id),
    INDEX idx_payment_date   (payment_date),
    INDEX idx_payment_method (payment_method),
    INDEX idx_ps_branch_date (branch_id, payment_date),
    INDEX idx_ps_sale_method (sale_id, payment_method)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
