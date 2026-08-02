-- ============================================================================
-- Business Performance 360 Dashboard - Database Schema
-- GlobalMart Retail Inc.
-- Syntax: MySQL 8.0+ (compatible with MariaDB; minor tweaks needed for PostgreSQL)
-- ============================================================================

DROP DATABASE IF EXISTS globalmart_ceo_dashboard;
CREATE DATABASE globalmart_ceo_dashboard
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE globalmart_ceo_dashboard;

-- ----------------------------------------------------------------------------
-- 1. CATEGORIES  (top-level dimension, no dependencies)
-- ----------------------------------------------------------------------------
CREATE TABLE categories (
    category_id     INT PRIMARY KEY,
    category_name   VARCHAR(50)  NOT NULL,
    department      VARCHAR(50)  NOT NULL
);

-- ----------------------------------------------------------------------------
-- 2. PRODUCTS  (depends on categories)
-- ----------------------------------------------------------------------------
CREATE TABLE products (
    product_id      INT PRIMARY KEY,
    category_id     INT NOT NULL,
    product_name    VARCHAR(100) NOT NULL,
    brand           VARCHAR(50),
    unit_price      DECIMAL(10,2) NOT NULL CHECK (unit_price >= 0),
    unit_cost       DECIMAL(10,2) NOT NULL CHECK (unit_cost >= 0),
    launch_date     DATE,
    CONSTRAINT fk_products_category
        FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

-- ----------------------------------------------------------------------------
-- 3. REGIONS  (top-level dimension)
-- ----------------------------------------------------------------------------
CREATE TABLE regions (
    region_id       INT PRIMARY KEY,
    country         VARCHAR(50) NOT NULL,
    state           VARCHAR(50) NOT NULL,
    region_name     VARCHAR(100) NOT NULL
);

-- ----------------------------------------------------------------------------
-- 4. SALES_REPS  (depends on regions)
-- ----------------------------------------------------------------------------
CREATE TABLE sales_reps (
    rep_id          INT PRIMARY KEY,
    rep_name        VARCHAR(100) NOT NULL,
    region_id       INT NOT NULL,
    hire_date       DATE,
    CONSTRAINT fk_reps_region
        FOREIGN KEY (region_id) REFERENCES regions(region_id)
);

-- ----------------------------------------------------------------------------
-- 5. CUSTOMERS  (independent dimension; country/state stored as text —
--    cleaned & standardized during the ALTER/UPDATE phase)
-- ----------------------------------------------------------------------------
CREATE TABLE customers (
    customer_id     INT PRIMARY KEY,
    customer_name   VARCHAR(100) NOT NULL,
    email           VARCHAR(100),
    segment         VARCHAR(20)  NOT NULL,
    country         VARCHAR(50)  NOT NULL,
    state           VARCHAR(50)  NOT NULL,
    signup_date     DATE
);

-- ----------------------------------------------------------------------------
-- 6. ORDERS  (fact table)
-- ----------------------------------------------------------------------------
CREATE TABLE orders (
    order_id        INT PRIMARY KEY,
    customer_id     INT NOT NULL,
    product_id      INT NOT NULL,
    rep_id          INT NOT NULL,
    region_id       INT NOT NULL,
    order_date      DATE NOT NULL,
    ship_date       DATE,
    sales_channel   VARCHAR(20) NOT NULL,
    quantity        INT NOT NULL,
    unit_price      DECIMAL(10,2) NOT NULL,
    discount        DECIMAL(5,2) DEFAULT 0,
    revenue         DECIMAL(12,2) NOT NULL,
    profit          DECIMAL(12,2) NOT NULL,
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    CONSTRAINT fk_orders_product  FOREIGN KEY (product_id)  REFERENCES products(product_id),
    CONSTRAINT fk_orders_rep      FOREIGN KEY (rep_id)      REFERENCES sales_reps(rep_id),
    CONSTRAINT fk_orders_region   FOREIGN KEY (region_id)   REFERENCES regions(region_id)
);

-- ----------------------------------------------------------------------------
-- 7. RETURNS  (fact table, depends on orders)
-- ----------------------------------------------------------------------------
CREATE TABLE returns (
    return_id       INT PRIMARY KEY,
    order_id        INT NOT NULL,
    return_date     DATE NOT NULL,
    return_reason   VARCHAR(100),
    refund_amount   DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_returns_order FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

-- ----------------------------------------------------------------------------
-- 8. MONTHLY_TARGETS  (fact table, depends on regions)
-- ----------------------------------------------------------------------------
CREATE TABLE monthly_targets (
    target_id       INT PRIMARY KEY,
    region_id       INT NOT NULL,
    target_month    DATE NOT NULL,
    target_revenue  DECIMAL(12,2) NOT NULL,
    CONSTRAINT fk_targets_region FOREIGN KEY (region_id) REFERENCES regions(region_id)
);

-- ----------------------------------------------------------------------------
-- INDEXES for query performance (executive dashboard runs heavy aggregations)
-- ----------------------------------------------------------------------------
CREATE INDEX idx_orders_date        ON orders(order_date);
CREATE INDEX idx_orders_customer    ON orders(customer_id);
CREATE INDEX idx_orders_product     ON orders(product_id);
CREATE INDEX idx_orders_region      ON orders(region_id);
CREATE INDEX idx_orders_rep         ON orders(rep_id);
CREATE INDEX idx_orders_channel     ON orders(sales_channel);
CREATE INDEX idx_returns_order      ON returns(order_id);
CREATE INDEX idx_targets_region_mo  ON monthly_targets(region_id, target_month);
CREATE INDEX idx_customers_segment  ON customers(segment);
CREATE INDEX idx_customers_country  ON customers(country);

-- ----------------------------------------------------------------------------
-- SAMPLE INSERT STATEMENTS
-- (Full data load for 100K+ rows uses LOAD DATA INFILE / bulk import —
--  see 02_data_load_and_cleaning.sql. These are illustrative single-row inserts.)
-- ----------------------------------------------------------------------------
INSERT INTO categories (category_id, category_name, department) VALUES
    (1, 'Electronics', 'Hardgoods'),
    (2, 'Furniture', 'Hardgoods'),
    (3, 'Apparel', 'Softlines');

INSERT INTO regions (region_id, country, state, region_name) VALUES
    (1, 'USA', 'California', 'USA - California'),
    (2, 'UK', 'England', 'UK - England');

INSERT INTO sales_reps (rep_id, rep_name, region_id, hire_date) VALUES
    (1, 'James Smith', 1, '2019-03-15'),
    (2, 'Priya Sharma', 2, '2020-07-01');

INSERT INTO customers (customer_id, customer_name, email, segment, country, state, signup_date) VALUES
    (1, 'John Miller', 'john.miller1@mail.com', 'Consumer', 'USA', 'California', '2021-05-10'),
    (2, 'Emma Evans', 'emma.evans2@mail.com', 'Corporate', 'UK', 'England', '2020-11-22');

INSERT INTO products (product_id, category_id, product_name, brand, unit_price, unit_cost, launch_date) VALUES
    (1, 1, 'Wireless Headphones', 'Zenova', 89.99, 34.50, '2021-01-15'),
    (2, 2, 'Office Chair', 'Urbanix', 249.00, 95.00, '2020-06-01');

INSERT INTO orders (order_id, customer_id, product_id, rep_id, region_id, order_date, ship_date,
                     sales_channel, quantity, unit_price, discount, revenue, profit) VALUES
    (1, 1, 1, 1, 1, '2024-03-10', '2024-03-13', 'Online', 2, 89.99, 0.10, 161.98, 92.98),
    (2, 2, 2, 2, 2, '2024-03-11', '2024-03-14', 'In-Store', 1, 249.00, 0.00, 249.00, 154.00);

INSERT INTO returns (return_id, order_id, return_date, return_reason, refund_amount) VALUES
    (1, 1, '2024-03-20', 'Changed Mind', 145.78);

INSERT INTO monthly_targets (target_id, region_id, target_month, target_revenue) VALUES
    (1, 1, '2024-03-01', 45000.00),
    (2, 2, '2024-03-01', 38000.00);
