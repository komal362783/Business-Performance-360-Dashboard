# Data Dictionary — Business Performance 360° Dashboard

---

## 1. Categories
| Column | Type | Description | Notes |
|---|---|---|---|
| category_id | INT (PK) | Unique category identifier | 1–8 |
| category_name | VARCHAR(50) | e.g. Electronics, Furniture, Apparel | |
| department | VARCHAR(50) | Parent grouping, e.g. "Hardgoods", "Softlines" | |

## 2. Products
| Column | Type | Description | Notes |
|---|---|---|---|
| product_id | INT (PK) | Unique product identifier | 1–500 |
| category_id | INT (FK) | Links to Categories | |
| product_name | VARCHAR(100) | Product title | |
| brand | VARCHAR(50) | Brand name | |
| unit_price | DECIMAL(10,2) | Selling price per unit | Some missing (raw) |
| unit_cost | DECIMAL(10,2) | Cost to company per unit | Used for profit calc |
| launch_date | DATE | Date product was introduced | |

## 3. Customers
| Column | Type | Description | Notes |
|---|---|---|---|
| customer_id | INT (PK) | Unique customer identifier | 1–8000 |
| customer_name | VARCHAR(100) | Full name | |
| email | VARCHAR(100) | Contact email | ~3% missing |
| segment | VARCHAR(20) | Consumer / Corporate / Small Business | |
| country | VARCHAR(50) | Customer's country | Inconsistent labels (raw) |
| state | VARCHAR(50) | Customer's state/province | |
| signup_date | DATE | Date customer first registered | |

## 4. Regions
| Column | Type | Description | Notes |
|---|---|---|---|
| region_id | INT (PK) | Unique region identifier | |
| country | VARCHAR(50) | Country name | 6 countries |
| state | VARCHAR(50) | State/province | ~40 states total |
| region_name | VARCHAR(50) | e.g. "North America - West" | |

## 5. Sales_Reps
| Column | Type | Description | Notes |
|---|---|---|---|
| rep_id | INT (PK) | Unique sales rep identifier | 1–60 |
| rep_name | VARCHAR(100) | Full name | |
| region_id | INT (FK) | Assigned region | |
| hire_date | DATE | Date hired | |

## 6. Orders (Fact Table)
| Column | Type | Description | Notes |
|---|---|---|---|
| order_id | INT (PK) | Unique order line identifier | ~1.5% duplicated (raw) |
| customer_id | INT (FK) | Links to Customers | Some invalid/orphaned (raw) |
| product_id | INT (FK) | Links to Products | |
| rep_id | INT (FK) | Links to Sales_Reps | |
| region_id | INT (FK) | Links to Regions | |
| order_date | DATE | Date order was placed | Mixed formats (raw) |
| ship_date | DATE | Date order was shipped | Sometimes before order_date (raw, error) |
| sales_channel | VARCHAR(20) | Online / In-Store / Wholesale / Marketplace | |
| quantity | INT | Units ordered | Some negative/outlier values (raw) |
| unit_price | DECIMAL(10,2) | Price per unit at time of sale | |
| discount | DECIMAL(5,2) | Discount % applied | ~5% missing (raw) |
| revenue | DECIMAL(12,2) | quantity × unit_price × (1-discount) | Calculated |
| profit | DECIMAL(12,2) | revenue − (quantity × unit_cost) | Calculated |

## 7. Returns
| Column | Type | Description | Notes |
|---|---|---|---|
| return_id | INT (PK) | Unique return identifier | |
| order_id | INT (FK) | Links to Orders | |
| return_date | DATE | Date of return | |
| return_reason | VARCHAR(100) | Damaged / Wrong Item / Not as Described / Other | ~8% missing (raw) |
| refund_amount | DECIMAL(10,2) | Amount refunded | |

## 8. Monthly_Targets
| Column | Type | Description | Notes |
|---|---|---|---|
| target_id | INT (PK) | Unique identifier | |
| region_id | INT (FK) | Links to Regions | |
| target_month | DATE | First day of target month | |
| target_revenue | DECIMAL(12,2) | Revenue goal for that region/month | |

---

## Derived / Feature-Engineered Fields (created in Python phase)
| Field | Description |
|---|---|
| order_year, order_month, order_quarter | Extracted date parts |
| profit_margin_pct | profit / revenue |
| is_returned | Flag if order_id appears in Returns |
| customer_lifetime_orders | Count of orders per customer |
| is_repeat_customer | Flag if customer has >1 order |
| delivery_days | ship_date − order_date |
| target_achievement_pct | actual revenue / target revenue per region/month |
