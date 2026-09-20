-- Sales Intelligence Hub Database Triggers
-- Automation for Financial Consistency
-- ============================================

USE sales_intelligence_hub;

-- ============================================
-- TRIGGER: payment_splits_after_insert
-- Purpose: Update received_amount, pending_amount and payment_status
--          on customer_sales whenever a payment row is inserted
-- ============================================
DELIMITER $$

CREATE TRIGGER payment_splits_after_insert
AFTER INSERT ON payment_splits
FOR EACH ROW
BEGIN
    DECLARE v_sale_amount    DECIMAL(12, 2);
    DECLARE v_total_received DECIMAL(12, 2);
    DECLARE v_new_status     VARCHAR(20);

    SELECT sale_amount INTO v_sale_amount
    FROM customer_sales WHERE sale_id = NEW.sale_id;

    SELECT COALESCE(SUM(amount), 0) INTO v_total_received
    FROM payment_splits WHERE sale_id = NEW.sale_id;

    IF v_total_received >= v_sale_amount THEN
        SET v_new_status = 'Closed';
    ELSEIF v_total_received > 0 THEN
        SET v_new_status = 'Partial';
    ELSE
        SET v_new_status = 'Open';
    END IF;

    UPDATE customer_sales
    SET received_amount = v_total_received,
        pending_amount  = v_sale_amount - v_total_received,
        payment_status  = v_new_status,
        updated_at      = CURRENT_TIMESTAMP
    WHERE sale_id = NEW.sale_id;
END $$

DELIMITER ;

-- ============================================
-- TRIGGER: payment_splits_after_update
-- Purpose: Update received_amount, pending_amount and payment_status
--          on customer_sales whenever a payment row is updated
-- ============================================
DELIMITER $$

CREATE TRIGGER payment_splits_after_update
AFTER UPDATE ON payment_splits
FOR EACH ROW
BEGIN
    DECLARE v_sale_amount    DECIMAL(12, 2);
    DECLARE v_total_received DECIMAL(12, 2);
    DECLARE v_new_status     VARCHAR(20);

    SELECT sale_amount INTO v_sale_amount
    FROM customer_sales WHERE sale_id = NEW.sale_id;

    SELECT COALESCE(SUM(amount), 0) INTO v_total_received
    FROM payment_splits WHERE sale_id = NEW.sale_id;

    IF v_total_received >= v_sale_amount THEN
        SET v_new_status = 'Closed';
    ELSEIF v_total_received > 0 THEN
        SET v_new_status = 'Partial';
    ELSE
        SET v_new_status = 'Open';
    END IF;

    UPDATE customer_sales
    SET received_amount = v_total_received,
        pending_amount  = v_sale_amount - v_total_received,
        payment_status  = v_new_status,
        updated_at      = CURRENT_TIMESTAMP
    WHERE sale_id = NEW.sale_id;
END $$

DELIMITER ;

-- ============================================
-- TRIGGER: payment_splits_after_delete
-- Purpose: Update received_amount, pending_amount and payment_status
--          on customer_sales whenever a payment row is deleted
-- ============================================
DELIMITER $$

CREATE TRIGGER payment_splits_after_delete
AFTER DELETE ON payment_splits
FOR EACH ROW
BEGIN
    DECLARE v_sale_amount    DECIMAL(12, 2);
    DECLARE v_total_received DECIMAL(12, 2);
    DECLARE v_new_status     VARCHAR(20);

    SELECT sale_amount INTO v_sale_amount
    FROM customer_sales WHERE sale_id = OLD.sale_id;

    SELECT COALESCE(SUM(amount), 0) INTO v_total_received
    FROM payment_splits WHERE sale_id = OLD.sale_id;

    IF v_total_received >= v_sale_amount THEN
        SET v_new_status = 'Closed';
    ELSEIF v_total_received > 0 THEN
        SET v_new_status = 'Partial';
    ELSE
        SET v_new_status = 'Open';
    END IF;

    UPDATE customer_sales
    SET received_amount = v_total_received,
        pending_amount  = v_sale_amount - v_total_received,
        payment_status  = v_new_status,
        updated_at      = CURRENT_TIMESTAMP
    WHERE sale_id = OLD.sale_id;
END $$

DELIMITER ;
