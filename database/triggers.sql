-- Sales Intelligence Hub Database Triggers
-- Automation for Financial Consistency
-- ============================================

USE sales_intelligence_hub;

-- ============================================
-- TRIGGER: payment_splits_after_insert
-- Purpose: Update payment status and amounts when a payment is recorded
-- ============================================
DELIMITER $$

CREATE TRIGGER payment_splits_after_insert
AFTER INSERT ON payment_splits
FOR EACH ROW
BEGIN
    DECLARE total_received DECIMAL(12, 2);
    DECLARE sale_amount_total DECIMAL(12, 2);
    DECLARE new_status VARCHAR(20);
    
    -- Get the sale amount
    SELECT sale_amount INTO sale_amount_total FROM customer_sales WHERE sale_id = NEW.sale_id;
    
    -- Calculate total received
    SELECT COALESCE(SUM(amount), 0) INTO total_received FROM payment_splits WHERE sale_id = NEW.sale_id;
    
    -- Determine payment status
    IF total_received >= sale_amount_total THEN
        SET new_status = 'Closed';
    ELSEIF total_received > 0 THEN
        SET new_status = 'Partial';
    ELSE
        SET new_status = 'Open';
    END IF;
    
    -- Update the sale record
    UPDATE customer_sales 
    SET payment_status = new_status,
        updated_at = CURRENT_TIMESTAMP
    WHERE sale_id = NEW.sale_id;
END $$

DELIMITER ;

-- ============================================
-- TRIGGER: payment_splits_after_update
-- Purpose: Update payment status when a payment is modified
-- ============================================
DELIMITER $$

CREATE TRIGGER payment_splits_after_update
AFTER UPDATE ON payment_splits
FOR EACH ROW
BEGIN
    DECLARE total_received DECIMAL(12, 2);
    DECLARE sale_amount_total DECIMAL(12, 2);
    DECLARE new_status VARCHAR(20);
    
    -- Get the sale amount
    SELECT sale_amount INTO sale_amount_total FROM customer_sales WHERE sale_id = NEW.sale_id;
    
    -- Calculate total received
    SELECT COALESCE(SUM(amount), 0) INTO total_received FROM payment_splits WHERE sale_id = NEW.sale_id;
    
    -- Determine payment status
    IF total_received >= sale_amount_total THEN
        SET new_status = 'Closed';
    ELSEIF total_received > 0 THEN
        SET new_status = 'Partial';
    ELSE
        SET new_status = 'Open';
    END IF;
    
    -- Update the sale record
    UPDATE customer_sales 
    SET payment_status = new_status,
        updated_at = CURRENT_TIMESTAMP
    WHERE sale_id = NEW.sale_id;
END $$

DELIMITER ;

-- ============================================
-- TRIGGER: payment_splits_after_delete
-- Purpose: Update payment status when a payment is deleted
-- ============================================
DELIMITER $$

CREATE TRIGGER payment_splits_after_delete
AFTER DELETE ON payment_splits
FOR EACH ROW
BEGIN
    DECLARE total_received DECIMAL(12, 2);
    DECLARE sale_amount_total DECIMAL(12, 2);
    DECLARE new_status VARCHAR(20);
    
    -- Get the sale amount
    SELECT sale_amount INTO sale_amount_total FROM customer_sales WHERE sale_id = OLD.sale_id;
    
    -- Calculate total received
    SELECT COALESCE(SUM(amount), 0) INTO total_received FROM payment_splits WHERE sale_id = OLD.sale_id;
    
    -- Determine payment status
    IF total_received >= sale_amount_total THEN
        SET new_status = 'Closed';
    ELSEIF total_received > 0 THEN
        SET new_status = 'Partial';
    ELSE
        SET new_status = 'Open';
    END IF;
    
    -- Update the sale record
    UPDATE customer_sales 
    SET payment_status = new_status,
        updated_at = CURRENT_TIMESTAMP
    WHERE sale_id = OLD.sale_id;
END $$

DELIMITER ;
