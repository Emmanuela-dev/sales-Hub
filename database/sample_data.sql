-- Sales Intelligence Hub Sample Data
-- Realistic demo data for testing
-- ============================================

USE sales_intelligence_hub;

-- ============================================
-- INSERT: Branches
-- ============================================
INSERT INTO branches (branch_name, branch_code, location, branch_manager, contact_phone, email) VALUES
('New York HQ', 'NY-001', 'Manhattan, New York', 'John Smith', '212-555-0101', 'ny@salesintel.com'),
('Los Angeles Branch', 'LA-002', 'Downtown, Los Angeles', 'Sarah Johnson', '213-555-0102', 'la@salesintel.com'),
('Chicago Office', 'CH-003', 'Loop District, Chicago', 'Michael Brown', '312-555-0103', 'chicago@salesintel.com'),
('Boston Sales', 'BOS-004', 'Financial District, Boston', 'Emma Wilson', '617-555-0104', 'boston@salesintel.com'),
('San Francisco Hub', 'SF-005', 'SOMA, San Francisco', 'David Lee', '415-555-0105', 'sf@salesintel.com'),
('Miami Operations', 'MIA-006', 'Brickell, Miami', 'Jessica Martinez', '305-555-0106', 'miami@salesintel.com');

-- ============================================
-- INSERT: Users (with bcrypt hashed passwords)
-- Password: admin123 (example - use proper hashing in production)
-- ============================================
INSERT INTO users (username, email, password_hash, role, branch_id, is_active) VALUES
('superadmin', 'admin@salesintel.com', '$2b$12$abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', 'Super Admin', NULL, TRUE),
('ny_admin', 'ny.admin@salesintel.com', '$2b$12$abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', 'Admin', 1, TRUE),
('la_admin', 'la.admin@salesintel.com', '$2b$12$abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', 'Admin', 2, TRUE),
('ch_admin', 'ch.admin@salesintel.com', '$2b$12$abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', 'Admin', 3, TRUE),
('user1', 'user1@salesintel.com', '$2b$12$abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', 'User', 1, TRUE);

-- ============================================
-- INSERT: Sales Data (January - May 2026)
-- ============================================
INSERT INTO customer_sales (branch_id, customer_name, customer_phone, customer_email, product_category, product_description, sale_amount, sale_date, payment_status, notes) VALUES
-- New York (Branch 1)
(1, 'Acme Corporation', '212-555-1001', 'contact@acmecorp.com', 'Enterprise', 'Software License - Annual', 45000.00, '2026-01-15', 'Open', 'Large enterprise deal'),
(1, 'Tech Solutions Inc', '212-555-1002', 'info@techsol.com', 'Professional Services', 'Consulting Services - Q1', 15000.00, '2026-01-20', 'Open', ''),
(1, 'Global Industries', '212-555-1003', 'sales@global.com', 'Enterprise', 'Software License - Annual', 32000.00, '2026-02-10', 'Partial', ''),
(1, 'Financial Group NY', '212-555-1004', 'procurement@fgny.com', 'Professional Services', 'Implementation Services', 28000.00, '2026-02-15', 'Open', ''),
(1, 'Metro Services LLC', '212-555-1005', 'admin@metro.com', 'Standard', 'Monthly Subscription', 5000.00, '2026-03-01', 'Closed', 'Regular customer'),
(1, 'Capital Partners', '212-555-1006', 'contact@capital.com', 'Enterprise', 'Premium Support Package', 18000.00, '2026-03-20', 'Partial', ''),

-- Los Angeles (Branch 2)
(2, 'West Coast Trading', '213-555-2001', 'sales@westcoast.com', 'Enterprise', 'Software License - Annual', 38000.00, '2026-01-12', 'Partial', ''),
(2, 'Pacific Innovations', '213-555-2002', 'info@pacific.com', 'Professional Services', 'Strategy Consultation', 12000.00, '2026-01-25', 'Closed', ''),
(2, 'Entertainment Plus', '213-555-2003', 'contact@entplus.com', 'Standard', 'Monthly Subscription', 4500.00, '2026-02-08', 'Closed', ''),
(2, 'California Enterprises', '213-555-2004', 'procurement@caent.com', 'Enterprise', 'Enterprise Solution', 55000.00, '2026-02-20', 'Open', 'Large deal - pending approval'),
(2, 'Creative Studios', '213-555-2005', 'admin@creative.com', 'Professional Services', 'Design Services Package', 9000.00, '2026-03-10', 'Partial', ''),
(2, 'LA Media Group', '213-555-2006', 'sales@lamedia.com', 'Standard', 'Monthly Subscription', 6000.00, '2026-03-25', 'Closed', ''),

-- Chicago (Branch 3)
(3, 'Midwest Manufacturing', '312-555-3001', 'contact@midwest.com', 'Enterprise', 'ERP Implementation', 62000.00, '2026-01-18', 'Open', 'Complex implementation'),
(3, 'Chicago Financial', '312-555-3002', 'procurement@chicfin.com', 'Professional Services', 'Audit Services', 16000.00, '2026-02-05', 'Partial', ''),
(3, 'Industrial Solutions', '312-555-3003', 'sales@industrial.com', 'Enterprise', 'Software License - Annual', 41000.00, '2026-02-22', 'Closed', ''),
(3, 'North Star Logistics', '312-555-3004', 'info@northstar.com', 'Professional Services', 'Supply Chain Optimization', 22000.00, '2026-03-15', 'Open', ''),
(3, 'Midwest Retailers', '312-555-3005', 'admin@midwest-retail.com', 'Standard', 'Monthly Subscription', 5500.00, '2026-04-01', 'Closed', 'Renewed subscription'),

-- Boston (Branch 4)
(4, 'Boston Biotech', '617-555-4001', 'procurement@bostonbio.com', 'Enterprise', 'Research Platform License', 48000.00, '2026-01-22', 'Partial', ''),
(4, 'Northeast Trading', '617-555-4002', 'sales@northeast.com', 'Professional Services', 'Market Analysis', 13000.00, '2026-02-12', 'Closed', ''),
(4, 'Elite Consultants', '617-555-4003', 'info@elite.com', 'Enterprise', 'Premium Consulting Package', 35000.00, '2026-03-05', 'Open', ''),
(4, 'Boston Analytics', '617-555-4004', 'contact@bosanalytics.com', 'Standard', 'Monthly Subscription', 4800.00, '2026-03-28', 'Partial', ''),

-- San Francisco (Branch 5)
(5, 'Silicon Valley Tech', '415-555-5001', 'contact@svtech.com', 'Enterprise', 'AI/ML Platform License', 72000.00, '2026-01-20', 'Open', 'Cutting-edge technology'),
(5, 'Innovation Labs', '415-555-5002', 'procurement@innovlabs.com', 'Professional Services', 'AI Consultation', 25000.00, '2026-02-18', 'Partial', ''),
(5, 'Tech Startup Hub', '415-555-5003', 'admin@techub.com', 'Standard', 'Startup Package', 8000.00, '2026-03-12', 'Open', ''),
(5, 'Bay Area Ventures', '415-555-5004', 'sales@bayarea.com', 'Enterprise', 'Digital Transformation', 58000.00, '2026-04-01', 'Open', ''),

-- Miami (Branch 6)
(6, 'Miami Development', '305-555-6001', 'info@miamdev.com', 'Enterprise', 'Real Estate Platform', 44000.00, '2026-01-25', 'Partial', ''),
(6, 'Caribbean Imports', '305-555-6002', 'sales@carimports.com', 'Professional Services', 'Trade Facilitation Services', 11000.00, '2026-02-20', 'Closed', ''),
(6, 'Miami Hotels Group', '305-555-6003', 'procurement@miahotel.com', 'Standard', 'Monthly Subscription', 5200.00, '2026-03-08', 'Closed', ''),
(6, 'Biscayne Financial', '305-555-6004', 'admin@biscaynefin.com', 'Enterprise', 'Financial Services Suite', 51000.00, '2026-04-10', 'Open', '');

-- ============================================
-- INSERT: Payment Data
-- ============================================
INSERT INTO payment_splits (sale_id, branch_id, amount, payment_method, payment_date, transaction_reference, notes) VALUES
-- Sales 1-3 (New York) Payments
(1, 1, 15000.00, 'Card', '2026-01-20', 'TXN001', 'First installment'),
(1, 1, 15000.00, 'Card', '2026-02-20', 'TXN002', 'Second installment'),
(2, 1, 15000.00, 'UPI', '2026-01-25', 'UPI001', 'Full payment'),
(3, 1, 16000.00, 'Card', '2026-02-15', 'TXN003', 'Partial payment'),
(4, 1, 10000.00, 'Cash', '2026-02-25', 'CASH001', 'Initial payment'),
(5, 1, 5000.00, 'Card', '2026-03-05', 'TXN004', 'Full payment'),
(6, 1, 9000.00, 'UPI', '2026-04-01', 'UPI002', 'Partial payment'),

-- Sales 7-12 (Los Angeles) Payments
(7, 2, 20000.00, 'Card', '2026-01-18', 'TXN005', 'First installment'),
(7, 2, 18000.00, 'Card', '2026-02-18', 'TXN006', 'Second installment'),
(8, 2, 12000.00, 'UPI', '2026-02-01', 'UPI003', 'Full payment'),
(9, 2, 4500.00, 'Cash', '2026-02-15', 'CASH002', 'Full payment'),
(10, 2, 25000.00, 'Card', '2026-03-20', 'TXN007', 'Partial payment'),
(11, 2, 5000.00, 'UPI', '2026-03-15', 'UPI004', 'Partial payment'),
(12, 2, 6000.00, 'Card', '2026-03-28', 'TXN008', 'Full payment'),

-- Sales 13-17 (Chicago) Payments
(13, 3, 30000.00, 'Card', '2026-02-01', 'TXN009', 'First installment'),
(14, 3, 8000.00, 'UPI', '2026-02-10', 'UPI005', 'Partial payment'),
(15, 3, 41000.00, 'Card', '2026-03-01', 'TXN010', 'Full payment'),
(16, 3, 11000.00, 'Cash', '2026-03-20', 'CASH003', 'Partial payment'),
(17, 3, 5500.00, 'Card', '2026-04-05', 'TXN011', 'Full payment'),

-- Sales 18-21 (Boston) Payments
(18, 4, 24000.00, 'Card', '2026-02-01', 'TXN012', 'Partial payment'),
(19, 4, 13000.00, 'UPI', '2026-02-20', 'UPI006', 'Full payment'),
(20, 4, 18000.00, 'Card', '2026-03-15', 'TXN013', 'Partial payment'),
(21, 4, 2400.00, 'Cash', '2026-04-05', 'CASH004', 'Partial payment'),

-- Sales 22-25 (San Francisco) Payments
(22, 5, 36000.00, 'Card', '2026-02-01', 'TXN014', 'Partial payment'),
(23, 5, 15000.00, 'Card', '2026-03-01', 'TXN015', 'Partial payment'),
(24, 5, 4000.00, 'UPI', '2026-03-20', 'UPI007', 'Partial payment'),
(25, 5, 30000.00, 'Card', '2026-04-15', 'TXN016', 'Partial payment'),

-- Sales 26-29 (Miami) Payments
(26, 6, 22000.00, 'Card', '2026-02-10', 'TXN017', 'Partial payment'),
(27, 6, 11000.00, 'UPI', '2026-03-01', 'UPI008', 'Full payment'),
(28, 6, 5200.00, 'Cash', '2026-03-15', 'CASH005', 'Full payment');
