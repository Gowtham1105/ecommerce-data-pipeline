-- 1. Create the "Compute" Engine (Warehouse)
CREATE WAREHOUSE IF NOT EXISTS compute_wh;
USE WAREHOUSE compute_wh;

-- 2. Create the Database (The "Folder")
CREATE DATABASE IF NOT EXISTS ecommerce_db;
USE DATABASE ecommerce_db;  -- <--- This fixes your error

-- 3. Create the Schema (The "Sub-folder")
CREATE SCHEMA IF NOT EXISTS raw_data;
USE SCHEMA raw_data;

-- 4. Create the Table (The "File")
CREATE OR REPLACE TABLE orders (
    order_id INTEGER,
    user_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    total_price FLOAT,
    status STRING,
    created_at TIMESTAMP
);

-- 5. Verification
SELECT * FROM orders;

SELECT * FROM orders ORDER BY created_at DESC;

SELECT COUNT(order_id) FROM orders;

SELECT * FROM orders ORDER BY order_id DESC;

select count(*) from orders;

-- 1. Create a backup of unique rows
CREATE OR REPLACE TABLE orders_clean AS
SELECT DISTINCT * FROM orders;

-- 2. Empty the original table
TRUNCATE TABLE orders;

-- 3. Put the clean data back
INSERT INTO orders SELECT * FROM orders_clean;

-- 4. Verify (Should be around 1500 now)
SELECT COUNT(*) FROM orders;

select * from orders order by order_id desc;

