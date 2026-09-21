
USE sales_intelligence_hub;








-- Glamour Hub internal operations database
--
-- The active stock movement trigger and restock procedure are defined in
-- schema.sql so a fresh installation is created in one consistent step.
-- This file is intentionally kept as a setup entry point for existing scripts.

USE glamour_hub;
    SELECT sale_amount INTO v_sale_amount
