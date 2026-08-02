-- ============================================================================
-- Business Performance 360 Dashboard - Data Load & In-Database Cleaning
-- ============================================================================
-- This script assumes the RAW (dirty) CSVs have been bulk-loaded into staging
-- tables (orders_staging, customers_staging, returns_staging) with the same
-- structure as the main tables. It then applies ALTER / UPDATE / DELETE
-- operations to clean the data before promoting it into the production tables.
-- ============================================================================

USE globalmart_ceo_dashboard;

-- ----------------------------------------------------------------------------
-- STEP 0: Bulk load raw data into staging tables
-- ----------------------------------------------------------------------------
CREATE TABLE orders_staging LIKE orders;
CREATE TABLE customers_staging LIKE customers;
CREATE TABLE returns_staging LIKE returns;

LOAD DATA LOCAL INFILE '/path/to/Dataset/raw/orders_raw.csv'
    INTO TABLE orders_staging
    FIELDS TERMINATED BY ',' ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE '/path/to/Dataset/raw/customers_raw.csv'
    INTO TABLE customers_staging
    FIELDS TERMINATED BY ',' ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE '/path/to/Dataset/raw/returns_raw.csv'
    INTO TABLE returns_staging
    FIELDS TERMINATED BY ',' ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 ROWS;

-- ----------------------------------------------------------------------------
-- STEP 1: ALTER TABLE — add tracking / audit columns before cleaning
-- ----------------------------------------------------------------------------
ALTER TABLE orders_staging
    ADD COLUMN is_duplicate TINYINT(1) DEFAULT 0,
    ADD COLUMN cleaned_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE customers_staging
    ADD COLUMN country_original VARCHAR(50);

-- preserve original messy value before standardizing (audit trail)
UPDATE customers_staging
SET country_original = country;

-- ----------------------------------------------------------------------------
-- STEP 2: UPDATE — fix incorrect / inconsistent values
-- ----------------------------------------------------------------------------

-- 2a. Standardize inconsistent country labels
UPDATE customers_staging
SET country = 'USA'
WHERE UPPER(TRIM(country)) IN ('USA', 'U.S.A', 'UNITED STATES');

UPDATE customers_staging
SET country = 'UK'
WHERE UPPER(TRIM(country)) IN ('UK', 'U.K.', 'UNITED KINGDOM');

UPDATE customers_staging
SET country = 'Canada'
WHERE UPPER(TRIM(country)) = 'CANADA';

UPDATE customers_staging
SET country = 'Australia'
WHERE UPPER(TRIM(country)) IN ('AUSTRALIA', 'AUS');

UPDATE customers_staging
SET country = 'Germany'
WHERE UPPER(TRIM(country)) IN ('GERMANY', 'DE');

UPDATE customers_staging
SET country = 'India'
WHERE UPPER(TRIM(country)) IN ('INDIA', 'IND');

-- 2b. Fix negative quantities (data entry sign errors → take absolute value)
UPDATE orders_staging
SET quantity = ABS(quantity)
WHERE quantity < 0;

-- 2c. Fill missing discount values with 0 (business rule: no discount recorded = none applied)
UPDATE orders_staging
SET discount = 0
WHERE discount IS NULL;

-- 2d. Recompute revenue and profit for rows where quantity/discount was corrected,
--     to keep derived columns consistent with cleaned inputs
UPDATE orders_staging o
JOIN products p ON o.product_id = p.product_id
SET o.revenue = ROUND(o.quantity * o.unit_price * (1 - o.discount), 2),
    o.profit  = ROUND(o.revenue - (o.quantity * p.unit_cost), 2)
WHERE o.is_duplicate = 0;

-- 2e. Cap extreme quantity outliers at a business-reasonable maximum (e.g. 50 units/order)
--     Flag them first for review rather than silently deleting
ALTER TABLE orders_staging ADD COLUMN quantity_flag VARCHAR(20) DEFAULT NULL;

UPDATE orders_staging
SET quantity_flag = 'OUTLIER_REVIEW'
WHERE quantity > 500;

UPDATE orders_staging
SET quantity = 50
WHERE quantity > 500;

-- 2f. Fix unit_price outliers (>3 std dev from category mean → likely decimal/typo error)
UPDATE orders_staging o
JOIN products p ON o.product_id = p.product_id
SET o.unit_price = p.unit_price
WHERE o.unit_price > p.unit_price * 10;

-- 2g. Fill missing return_reason with 'Not Specified'
UPDATE returns_staging
SET return_reason = 'Not Specified'
WHERE return_reason IS NULL;

-- ----------------------------------------------------------------------------
-- STEP 3: DELETE — remove duplicates and invalid records
-- ----------------------------------------------------------------------------

-- 3a. Mark duplicate order_ids (keep the first occurrence only)
UPDATE orders_staging o
JOIN (
    SELECT order_id, MIN(cleaned_at) AS first_seen
    FROM orders_staging
    GROUP BY order_id
    HAVING COUNT(*) > 1
) dupes ON o.order_id = dupes.order_id AND o.cleaned_at > dupes.first_seen
SET o.is_duplicate = 1;

-- 3b. Delete flagged duplicate rows
DELETE FROM orders_staging
WHERE is_duplicate = 1;

-- 3c. Delete orders with invalid/orphaned customer_id (no matching customer)
DELETE os FROM orders_staging os
LEFT JOIN customers_staging cs ON os.customer_id = cs.customer_id
WHERE cs.customer_id IS NULL;

-- 3d. Delete exact duplicate customer records (same name + email)
DELETE c1 FROM customers_staging c1
INNER JOIN customers_staging c2
    ON c1.customer_name = c2.customer_name
    AND c1.email = c2.email
    AND c1.customer_id > c2.customer_id
WHERE c1.email IS NOT NULL;

-- ----------------------------------------------------------------------------
-- STEP 4: Standardize order_date format (mixed formats → proper DATE type)
-- ----------------------------------------------------------------------------
UPDATE orders_staging
SET order_date = STR_TO_DATE(order_date, '%m/%d/%Y')
WHERE order_date LIKE '%/%' AND order_date REGEXP '^[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}$';

UPDATE orders_staging
SET order_date = STR_TO_DATE(order_date, '%d-%m-%Y')
WHERE order_date LIKE '%-%' AND order_date REGEXP '^[0-9]{1,2}-[0-9]{1,2}-[0-9]{4}$';

-- ----------------------------------------------------------------------------
-- STEP 5: Promote cleaned staging data into production tables
-- ----------------------------------------------------------------------------
INSERT INTO customers (customer_id, customer_name, email, segment, country, state, signup_date)
SELECT customer_id, customer_name, email, segment, country, state, signup_date
FROM customers_staging;

INSERT INTO orders (order_id, customer_id, product_id, rep_id, region_id, order_date, ship_date,
                     sales_channel, quantity, unit_price, discount, revenue, profit)
SELECT order_id, customer_id, product_id, rep_id, region_id, order_date, ship_date,
       sales_channel, quantity, unit_price, discount, revenue, profit
FROM orders_staging;

INSERT INTO returns (return_id, order_id, return_date, return_reason, refund_amount)
SELECT return_id, order_id, return_date, return_reason, refund_amount
FROM returns_staging;

-- ----------------------------------------------------------------------------
-- STEP 6: Drop staging tables once validated
-- ----------------------------------------------------------------------------
-- DROP TABLE orders_staging, customers_staging, returns_staging;
-- (Kept commented out intentionally — drop only after QA sign-off)

-- ----------------------------------------------------------------------------
-- STEP 7: Validation queries — confirm cleaning worked
-- ----------------------------------------------------------------------------
SELECT COUNT(*) AS total_orders FROM orders;
SELECT COUNT(*) AS duplicate_check FROM (
    SELECT order_id FROM orders GROUP BY order_id HAVING COUNT(*) > 1
) d;
SELECT COUNT(*) AS negative_quantity_check FROM orders WHERE quantity < 0;
SELECT DISTINCT country FROM customers ORDER BY country;
