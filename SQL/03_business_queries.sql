-- ============================================================================
-- Business Performance 360 Dashboard - Business Queries
-- 40 real-world analytical queries for executive decision-making
-- Syntax: MySQL 8.0+ | All queries validated against the cleaned dataset
-- ============================================================================

USE globalmart_ceo_dashboard;

-- ============================================================================
-- SECTION 1: REVENUE & PROFIT ANALYSIS
-- ============================================================================

-- Q1. Overall company revenue, profit, and profit margin
SELECT
    ROUND(SUM(revenue), 2) AS total_revenue,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(SUM(profit) * 100.0 / SUM(revenue), 2) AS profit_margin_pct
FROM orders;

-- Q2. Revenue by year
SELECT YEAR(order_date) AS yr, ROUND(SUM(revenue), 2) AS revenue
FROM orders
GROUP BY yr
ORDER BY yr;

-- Q3. Year-over-year revenue growth
SELECT yr,
       revenue,
       ROUND((revenue - LAG(revenue) OVER (ORDER BY yr)) * 100.0 / LAG(revenue) OVER (ORDER BY yr), 2) AS yoy_growth_pct
FROM (
    SELECT YEAR(order_date) AS yr, SUM(revenue) AS revenue
    FROM orders GROUP BY yr
) yearly;

-- Q4. Monthly sales trend
SELECT DATE_FORMAT(order_date, '%Y-%m') AS ym, ROUND(SUM(revenue), 2) AS revenue
FROM orders
GROUP BY ym
ORDER BY ym;

-- Q5. Monthly profit margin trend
SELECT DATE_FORMAT(order_date, '%Y-%m') AS ym, ROUND(SUM(profit) * 100.0 / SUM(revenue), 2) AS margin_pct
FROM orders
GROUP BY ym
ORDER BY ym;

-- Q6. Quarterly revenue trend
SELECT YEAR(order_date) AS yr, QUARTER(order_date) AS qtr, ROUND(SUM(revenue), 2) AS revenue
FROM orders
GROUP BY yr, qtr
ORDER BY yr, qtr;

-- Q7. Running total (cumulative) revenue by month
SELECT ym, monthly_rev,
       ROUND(SUM(monthly_rev) OVER (ORDER BY ym), 2) AS running_total
FROM (
    SELECT DATE_FORMAT(order_date, '%Y-%m') AS ym, SUM(revenue) AS monthly_rev
    FROM orders GROUP BY ym
) m;

-- Q8. Profit margin by category
SELECT cat.category_name, ROUND(SUM(o.profit) * 100.0 / SUM(o.revenue), 2) AS profit_margin_pct
FROM orders o
JOIN products p ON o.product_id = p.product_id
JOIN categories cat ON p.category_id = cat.category_id
GROUP BY cat.category_name
ORDER BY profit_margin_pct DESC;

-- ============================================================================
-- SECTION 2: PRODUCT ANALYSIS
-- ============================================================================

-- Q9. Top 10 products by revenue
SELECT p.product_name, ROUND(SUM(o.revenue), 2) AS revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.product_name
ORDER BY revenue DESC
LIMIT 10;

-- Q10. Bottom 10 products by revenue (underperformers)
SELECT p.product_name, ROUND(SUM(o.revenue), 2) AS revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.product_name
ORDER BY revenue ASC
LIMIT 10;

-- Q11. Category-wise revenue and profit
SELECT cat.category_name, ROUND(SUM(o.revenue), 2) AS revenue, ROUND(SUM(o.profit), 2) AS profit
FROM orders o
JOIN products p ON o.product_id = p.product_id
JOIN categories cat ON p.category_id = cat.category_id
GROUP BY cat.category_name
ORDER BY revenue DESC;

-- Q12. Top-selling brand by revenue
SELECT p.brand, ROUND(SUM(o.revenue), 2) AS revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.brand
ORDER BY revenue DESC
LIMIT 5;

-- Q13. Best-selling product within each category (window function)
SELECT category_name, product_name, revenue FROM (
    SELECT cat.category_name, p.product_name, SUM(o.revenue) AS revenue,
           RANK() OVER (PARTITION BY cat.category_name ORDER BY SUM(o.revenue) DESC) AS rnk
    FROM orders o
    JOIN products p ON o.product_id = p.product_id
    JOIN categories cat ON p.category_id = cat.category_id
    GROUP BY cat.category_name, p.product_name
) ranked
WHERE rnk = 1;

-- Q14. Product price vs. its category average price (identify premium-priced items)
SELECT p.product_name, p.unit_price, cat.category_name,
       ROUND((SELECT AVG(unit_price) FROM products p2 WHERE p2.category_id = p.category_id), 2) AS category_avg_price
FROM products p
JOIN categories cat ON p.category_id = cat.category_id
ORDER BY p.unit_price DESC
LIMIT 10;

-- Q15. Products that have never been returned (quality leaders)
SELECT COUNT(*) AS never_returned_products
FROM products p
WHERE p.product_id NOT IN (
    SELECT o.product_id FROM orders o JOIN returns rt ON o.order_id = rt.order_id
);

-- ============================================================================
-- SECTION 3: REGIONAL / GEOGRAPHIC ANALYSIS
-- ============================================================================

-- Q16. Region performance (revenue + profit)
SELECT r.region_name, ROUND(SUM(o.revenue), 2) AS revenue, ROUND(SUM(o.profit), 2) AS profit
FROM orders o
JOIN regions r ON o.region_id = r.region_id
GROUP BY r.region_name
ORDER BY revenue DESC;

-- Q17. Revenue by country
SELECT r.country, ROUND(SUM(o.revenue), 2) AS revenue
FROM orders o
JOIN regions r ON o.region_id = r.region_id
GROUP BY r.country
ORDER BY revenue DESC;

-- Q18. Top 10 states by profit
SELECT r.state, r.country, ROUND(SUM(o.profit), 2) AS profit
FROM orders o
JOIN regions r ON o.region_id = r.region_id
GROUP BY r.state, r.country
ORDER BY profit DESC
LIMIT 10;

-- Q19. Monthly target achievement % by region
-- (Pre-aggregate orders by region/month FIRST to avoid fan-out inflation
--  from joining raw order rows directly to the targets table.)
SELECT r.region_name,
       ROUND(SUM(m.actual_revenue), 2) AS actual_revenue,
       ROUND(SUM(mt.target_revenue), 2) AS target_revenue,
       ROUND(SUM(m.actual_revenue) * 100.0 / SUM(mt.target_revenue), 2) AS achievement_pct
FROM (
    SELECT region_id, DATE_FORMAT(order_date, '%Y-%m') AS ym, SUM(revenue) AS actual_revenue
    FROM orders GROUP BY region_id, ym
) m
JOIN monthly_targets mt
    ON mt.region_id = m.region_id
   AND DATE_FORMAT(mt.target_month, '%Y-%m') = m.ym
JOIN regions r ON r.region_id = m.region_id
GROUP BY r.region_name
ORDER BY achievement_pct DESC;

-- Q20. Regions currently missing their target (underperformers needing attention)
SELECT r.region_name,
       ROUND(SUM(m.actual_revenue), 2) AS actual_revenue,
       ROUND(SUM(mt.target_revenue), 2) AS target_revenue,
       ROUND(SUM(m.actual_revenue) * 100.0 / SUM(mt.target_revenue), 2) AS achievement_pct
FROM (
    SELECT region_id, DATE_FORMAT(order_date, '%Y-%m') AS ym, SUM(revenue) AS actual_revenue
    FROM orders GROUP BY region_id, ym
) m
JOIN monthly_targets mt ON mt.region_id = m.region_id AND DATE_FORMAT(mt.target_month, '%Y-%m') = m.ym
JOIN regions r ON r.region_id = m.region_id
GROUP BY r.region_name
HAVING achievement_pct < 100
ORDER BY achievement_pct ASC;

-- ============================================================================
-- SECTION 4: CUSTOMER ANALYSIS & SEGMENTATION
-- ============================================================================

-- Q21. Revenue and customer count by segment
SELECT c.segment, COUNT(DISTINCT c.customer_id) AS customers, ROUND(SUM(o.revenue), 2) AS revenue
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.segment
ORDER BY revenue DESC;

-- Q22. Top 10 customers by lifetime value
SELECT c.customer_name, c.segment, COUNT(o.order_id) AS num_orders, ROUND(SUM(o.revenue), 2) AS lifetime_value
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id
ORDER BY lifetime_value DESC
LIMIT 10;

-- Q23. Repeat customer rate
SELECT ROUND(SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS repeat_customer_rate_pct
FROM (
    SELECT customer_id, COUNT(*) AS order_count FROM orders GROUP BY customer_id
) t;

-- Q24. New/one-time vs. returning customer revenue split
SELECT CASE WHEN order_count = 1 THEN 'New / One-time' ELSE 'Returning' END AS customer_type,
       COUNT(*) AS customers, ROUND(SUM(total_revenue), 2) AS revenue
FROM (
    SELECT customer_id, COUNT(*) AS order_count, SUM(revenue) AS total_revenue
    FROM orders GROUP BY customer_id
) t
GROUP BY customer_type;

-- Q25. Customers with zero orders (never converted / inactive)
SELECT COUNT(*) AS customers_with_no_orders
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL;

-- Q26. Average discount given, by customer segment
SELECT c.segment, ROUND(AVG(o.discount) * 100, 2) AS avg_discount_pct
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.segment;

-- Q27. Customer count by country and segment (cross-tab style)
SELECT country, segment, COUNT(*) AS customers
FROM customers
GROUP BY country, segment
ORDER BY country, segment;

-- ============================================================================
-- SECTION 5: SALES CHANNEL & ORDER ANALYSIS
-- ============================================================================

-- Q28. Average order value by sales channel
SELECT sales_channel, ROUND(AVG(revenue), 2) AS avg_order_value, COUNT(*) AS total_orders
FROM orders
GROUP BY sales_channel
ORDER BY avg_order_value DESC;

-- Q29. Profit comparison across sales channels
SELECT sales_channel, ROUND(SUM(profit), 2) AS total_profit, ROUND(AVG(profit), 2) AS avg_profit_per_order
FROM orders
GROUP BY sales_channel
ORDER BY total_profit DESC;

-- Q30. Discounted vs. non-discounted order profitability
SELECT CASE WHEN discount = 0 THEN 'No Discount' ELSE 'Discounted' END AS discount_flag,
       ROUND(AVG(profit), 2) AS avg_profit, COUNT(*) AS orders
FROM orders
GROUP BY discount_flag;

-- Q31. Orders placed per month (volume trend)
SELECT DATE_FORMAT(order_date, '%Y-%m') AS ym, COUNT(*) AS order_count
FROM orders
GROUP BY ym
ORDER BY ym;

-- Q32. Average delivery time (days between order and shipment)
SELECT ROUND(AVG(DATEDIFF(ship_date, order_date)), 2) AS avg_delivery_days
FROM orders;

-- ============================================================================
-- SECTION 6: SALES REP PERFORMANCE
-- ============================================================================

-- Q33. Sales rep performance ranking
SELECT sr.rep_name, ROUND(SUM(o.revenue), 2) AS revenue, COUNT(o.order_id) AS orders,
       RANK() OVER (ORDER BY SUM(o.revenue) DESC) AS rnk
FROM orders o
JOIN sales_reps sr ON o.rep_id = sr.rep_id
GROUP BY sr.rep_name
ORDER BY revenue DESC
LIMIT 10;

-- Q34. Sales reps performing above the company average
SELECT sr.rep_name, ROUND(SUM(o.revenue), 2) AS rep_revenue
FROM orders o
JOIN sales_reps sr ON o.rep_id = sr.rep_id
GROUP BY sr.rep_name
HAVING rep_revenue > (
    SELECT AVG(rev) FROM (SELECT SUM(revenue) AS rev FROM orders GROUP BY rep_id) t
)
ORDER BY rep_revenue DESC;

-- ============================================================================
-- SECTION 7: RETURNS ANALYSIS
-- ============================================================================

-- Q35. Overall return rate (% of orders returned)
SELECT ROUND(COUNT(DISTINCT rt.order_id) * 100.0 / COUNT(DISTINCT o.order_id), 2) AS return_rate_pct
FROM orders o
LEFT JOIN returns rt ON o.order_id = rt.order_id;

-- Q36. Return reason breakdown
SELECT return_reason, COUNT(*) AS return_count, ROUND(SUM(refund_amount), 2) AS total_refunded
FROM returns
GROUP BY return_reason
ORDER BY return_count DESC;

-- Q37. Top 10 most-returned products
SELECT p.product_name, COUNT(*) AS return_count
FROM returns rt
JOIN orders o ON rt.order_id = o.order_id
JOIN products p ON o.product_id = p.product_id
GROUP BY p.product_name
ORDER BY return_count DESC
LIMIT 10;

-- Q38. Return rate by product category
SELECT cat.category_name,
       COUNT(DISTINCT rt.order_id) AS returns_count,
       COUNT(DISTINCT o.order_id) AS orders_count,
       ROUND(COUNT(DISTINCT rt.order_id) * 100.0 / COUNT(DISTINCT o.order_id), 2) AS return_rate_pct
FROM orders o
JOIN products p ON o.product_id = p.product_id
JOIN categories cat ON p.category_id = cat.category_id
LEFT JOIN returns rt ON rt.order_id = o.order_id
GROUP BY cat.category_name
ORDER BY return_rate_pct DESC;

-- Q39. Refunds as a percentage of total revenue (profit leakage)
SELECT ROUND(SUM(rt.refund_amount) * 100.0 / (SELECT SUM(revenue) FROM orders), 2) AS refund_pct_of_revenue
FROM returns rt;

-- Q40. Monthly return trend (rising or falling?)
SELECT DATE_FORMAT(rt.return_date, '%Y-%m') AS ym, COUNT(*) AS return_count,
       ROUND(SUM(rt.refund_amount), 2) AS total_refunded
FROM returns rt
GROUP BY ym
ORDER BY ym;
