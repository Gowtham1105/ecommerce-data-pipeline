-- ==========================================
-- E-COMMERCE PIPELINE: ADVANCED ANALYTICS
-- ==========================================

-- 1. BUSINESS INTELLIGENCE: Best Selling Products
-- Joins the Streaming Fact Table (ORDERS) with the Dimension Table (PRODUCTS)
SELECT 
    p.NAME as "Product Name",
    p.CATEGORY as "Category",
    SUM(o.QUANTITY) as "Items Sold",
    SUM(o.TOTAL_PRICE) as "Total Revenue"
FROM ORDERS o
JOIN PRODUCTS p ON o.PRODUCT_ID = p.PRODUCT_ID
GROUP BY p.NAME, p.CATEGORY
ORDER BY "Total Revenue" DESC
LIMIT 5;

-- 2. FRAUD DETECTION: Z-Score Anomaly Analysis
-- Flags transactions that are > 2 Standard Deviations from the mean
WITH Order_Stats AS (
    SELECT AVG(TOTAL_PRICE) as Avg_Price, STDDEV(TOTAL_PRICE) as Std_Dev_Price
    FROM ORDERS
),
Anomalies AS (
    SELECT 
        o.ORDER_ID, 
        o.USER_ID, 
        o.TOTAL_PRICE,
        (o.TOTAL_PRICE - s.Avg_Price) / NULLIF(s.Std_Dev_Price, 0) as Z_Score
    FROM ORDERS o, Order_Stats s
)
SELECT 
    ORDER_ID, USER_ID, TOTAL_PRICE, ROUND(Z_Score, 2) as "Anomaly Score",
    CASE 
        WHEN ABS(Z_Score) > 2 THEN '🔴 ANOMALY DETECTED'
        ELSE '✅ Normal'
    END as Status
FROM Anomalies 
WHERE ABS(Z_Score) > 2
ORDER BY Z_Score DESC;

-- 3. CUSTOMER SEGMENTATION: RFM Analysis (Monetary)
-- Segments users into VIP tiers based on total spend
WITH User_Spending AS (
    SELECT USER_ID, SUM(TOTAL_PRICE) as Total_Spent
    FROM ORDERS GROUP BY USER_ID
)
SELECT 
    USER_ID, Total_Spent,
    CASE 
        WHEN NTILE(4) OVER (ORDER BY Total_Spent) = 4 THEN '💎 VIP'
        WHEN NTILE(4) OVER (ORDER BY Total_Spent) = 3 THEN '🥇 Gold'
        ELSE '🥈 Silver'
    END as Segment
FROM User_Spending
ORDER BY Total_Spent DESC;