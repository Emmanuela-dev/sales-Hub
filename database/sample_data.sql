-- ============================================================
-- Glamour Hub - Beauty Business Sample Data
-- Run AFTER schema.sql
-- ============================================================

USE glamour_hub;

-- ============================================================
-- USERS
-- Demo password for all seeded users: admin123
-- ============================================================
INSERT INTO users (username, full_name, email, phone, password_hash, role) VALUES
('owner',   'Amina Wanjiku',  'amina@glamourhub.co.ke',  '0722 001 001', '$2b$12$SZhaR7ik0iiy.zlK6.aA3.oBUFT5hQhf5p1JuLS9IbaEPA8KyTG4e', 'Owner'),
('manager', 'Grace Njeri',    'grace@glamourhub.co.ke',  '0711 001 002', '$2b$12$SZhaR7ik0iiy.zlK6.aA3.oBUFT5hQhf5p1JuLS9IbaEPA8KyTG4e', 'Manager'),
('staff1',  'Beatrice Auma',  'bea@glamourhub.co.ke',    '0700 001 003', '$2b$12$SZhaR7ik0iiy.zlK6.aA3.oBUFT5hQhf5p1JuLS9IbaEPA8KyTG4e', 'Staff'),
('staff2',  'Sharon Chebet',  'sharon@glamourhub.co.ke', '0733 001 004', '$2b$12$SZhaR7ik0iiy.zlK6.aA3.oBUFT5hQhf5p1JuLS9IbaEPA8KyTG4e', 'Staff');

-- ============================================================
-- PRODUCT CATEGORIES
-- ============================================================
INSERT INTO product_categories (name, description) VALUES
('Skincare',        'Moisturisers, serums, sunscreen, cleansers'),
('Hair Care',       'Shampoos, conditioners, hair oils, treatments'),
('Body Care',       'Body lotions, oils, scrubs, deodorants'),
('Makeup',          'Foundation, lipstick, mascara, eyeshadow'),
('Nail Care',       'Nail polish, nail care tools, gel kits'),
('Fragrances',      'Perfumes and body sprays'),
('Men''s Grooming', 'Shaving creams, beard oils, face wash'),
('Tools & Accessories', 'Brushes, sponges, hair tools');

-- ============================================================
-- PRODUCTS (Kenyan market brands + KES prices)
-- ============================================================
INSERT INTO products (category_id, name, brand, sku, buying_price, selling_price,
                      qty_in_stock, reorder_level, reorder_qty, unit, description) VALUES
-- Skincare (cat 1)
(1,'Nivea Soft Moisturising Cream 200ml',    'Nivea',   'NIV-SM-200', 350, 550,  28, 5, 12, 'piece', 'Light moisturiser for face and body'),
(1,'Fair & Lovely Advanced Multi Vitamin',  'Unilever','FAL-AMV-50',  120, 220,  40, 8, 20, 'piece', '50g fairness cream'),
(1,'Neutrogena Hydro Boost Water Gel',      'Neutrogena','NEU-HB-50',  950,1500,   8, 3,  6, 'piece', '50ml hydrating gel'),
(1,'Garnier Micellar Cleansing Water 400ml','Garnier', 'GAR-MCW-400', 750,1200,  12, 3,  6, 'bottle','Removes makeup and cleanses'),
(1,'Cetaphil Gentle Skin Cleanser 250ml',   'Cetaphil','CET-GSC-250', 850,1400,   5, 3,  6, 'bottle','Sensitive skin cleanser'),
-- Hair Care (cat 2)
(2,'Pantene Pro-V Shampoo 400ml',           'Pantene', 'PAN-SH-400',  380, 620,  22, 5, 12, 'bottle','Anti-dandruff formula'),
(2,'Organics Hair Food Olive Oil 250ml',    'Organics','ORG-HF-250',  280, 450,  30, 6, 15, 'bottle','Moisturising hair food'),
(2,'Vitale Olive Oil Hair Lotion 500ml',    'Vitale',  'VIT-OL-500',  320, 520,   3, 5, 10, 'bottle','Daily hair lotion'),
(2,'Doo Gro Hair Vitalizer 284g',           'Doo Gro', 'DOO-HV-284',  480, 780,  15, 4, 10, 'jar',   'Growth stimulating formula'),
(2,'Dark & Lovely Relaxer Kit Regular',     'Dark & Lovely','DAL-RK-REG',380,650, 2, 4,  8, 'kit',   'Home relaxer kit'),
-- Body Care (cat 3)
(3,'Vaseline Intensive Care Cocoa Glow',    'Vaseline','VAS-CC-400',  380, 600,  35, 8, 20, 'bottle','400ml cocoa butter lotion'),
(3,'Dove Body Wash Deeply Nourishing 500ml','Dove',    'DOV-BW-500',  520, 850,  18, 5, 10, 'bottle','Moisturising body wash'),
(3,'Shea Moisture Raw Shea Body Lotion',    'Shea Moisture','SHM-RSB-384',900,1500,7, 3,  6, 'bottle','384ml shea butter lotion'),
(3,'Jergens Natural Glow Daily Moisturiser','Jergens', 'JER-NG-400',  480, 780,   0, 4,  8, 'bottle','Self-tanning moisturiser - OUT'),
-- Makeup (cat 4)
(4,'Black Opal True Color Foundation SPF15','Black Opal','BOP-TC-30', 950,1600,  10, 3,  6, 'piece', '30ml liquid foundation'),
(4,'NYX Butter Gloss Lipstick',             'NYX',     'NYX-BG-LIP',  650,1100,  20, 5, 10, 'piece', 'Non-sticky lip gloss'),
(4,'L.A. Girl Pro Concealer HD',            'L.A. Girl','LAG-PC-HD',  450, 780,  14, 4,  8, 'piece', 'High-definition concealer'),
(4,'Rimmel Stay Matte Pressed Powder',      'Rimmel',  'RIM-SMP-14',  520, 900,   8, 3,  6, 'piece', '14g pressed powder'),
(4,'Maybelline Fit Me Matte Foundation',    'Maybelline','MAY-FMM-30', 780,1300,  6, 3,  6, 'piece', '30ml lightweight foundation'),
-- Nail Care (cat 5)
(5,'OPI Nail Lacquer 15ml',                 'OPI',     'OPI-NL-15',   380, 650,  25, 5, 12, 'bottle','Long-lasting nail colour'),
(5,'Sally Hansen Complete Salon Manicure',  'Sally Hansen','SAL-CSM-15',280,500, 18, 5, 10, 'bottle','7-in-1 nail colour'),
-- Fragrances (cat 6)
(6,'Revlon Charlie Red EDP 33ml',           'Revlon',  'REV-CR-33',   680,1100,  12, 3,  6, 'bottle','Fresh floral fragrance'),
(6,'Axe Apollo Body Spray 150ml',           'Axe',     'AXE-AP-150',  280, 450,  20, 5, 10, 'bottle','Long-lasting body spray'),
-- Men Grooming (cat 7)
(7,'Gillette Fusion5 Shave Gel 200ml',      'Gillette','GIL-F5-200',  420, 700,  10, 3,  6, 'bottle','Sensitive skin shave gel'),
(7,'Nivea Men Face Wash 100ml',             'Nivea',   'NIV-MFW-100', 280, 480,   8, 3,  6, 'bottle','Deep cleaning face wash'),
-- Tools (cat 8)
(8,'Real Techniques Starter Set 5pc',       'Real Techniques','RT-SS-5',1200,2000,5, 2,  4, 'set',   '5-piece brush starter set'),
(8,'Denman D3 Classic Styling Brush',       'Denman',  'DEN-D3-CL',   780,1300,   7, 2,  4, 'piece', 'Classic 7-row styling brush');

-- ============================================================
-- NOTE: After loading, generate real bcrypt hashes and update:
-- Login: username=owner  password=admin123
-- ============================================================
