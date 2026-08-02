# Business Performance 360° Dashboard (CEO Dashboard)
## Phase 1: Project Foundation & Data Model

---

## 1. Business Scenario

**Company:** GlobalMart Retail Inc. (fictional multinational retail company)

GlobalMart sells products across **6 countries**, **4 sales channels** (Online, In-Store, Wholesale, Marketplace), and **8 product categories**. The company operates through a network of **regional sales representatives** and ships orders to customers segmented by tier (Consumer, Corporate, Small Business).

**The Problem:**
Leadership currently receives fragmented reports from different regional teams, in different formats, on different schedules. The CEO and executive team have no single, real-time view of:
- Where revenue and profit are actually being generated
- Which products/categories are winning or losing
- Which regions/reps are over- or under-performing against targets
- Customer retention and return-related revenue loss
- Whether the company is on track to hit monthly/quarterly targets

**The Ask:**
Build a unified data pipeline (raw data → cleaned data → database → analysis → dashboard) that gives the CEO and executives a single source of truth: the **Business Performance 360° Dashboard**.

---

## 2. Objectives

1. Consolidate order, customer, product, returns, and target data into one analytical model.
2. Clean and validate messy real-world-style data (nulls, dupes, bad values, outliers).
3. Answer 30–40 real business questions via SQL.
4. Perform EDA, feature engineering, and KPI computation in Python.
5. Deliver an executive-grade, interactive Power BI dashboard across 8 pages.
6. Translate analysis into insights and actionable recommendations for leadership.

---

## 3. Project Folder Structure

```
Business-Performance-360-Dashboard/
│
├── Dataset/
│   ├── raw/                # Original messy generated data (with dirty records)
│   └── cleaned/             # Cleaned, production-ready data (for SQL/Python/PBI)
│
├── SQL/
│   ├── 01_create_tables.sql
│   ├── 02_alter_update_delete.sql
│   └── 03_business_queries.sql
│
├── Python/
│   ├── 01_data_cleaning.py
│   ├── 02_eda_feature_engineering.py
│   └── 03_kpi_insights_export.py
│
├── Excel/
│   └── CEO_Dashboard_Workbook.xlsx
│
├── PowerBI/
│   ├── DAX/
│   │   └── measures.txt
│   ├── Screenshots/
│   └── CEO_Dashboard_BuildGuide.md
│
├── Images/                  # Charts, ERD, dashboard mockups
│
├── Report/
│   ├── 01_Project_Foundation.md
│   ├── 02_Data_Dictionary.md
│   ├── Business_Insights_and_Recommendations.md
│   └── Project_Report.md
│
├── Resume/
│   └── Resume_Content.md
│
└── README.md
```

---

## 4. Data Model — Tables Overview

Star-schema style model: **Orders** (fact table) at the center, surrounded by dimension tables.

| Table | Type | Approx. Rows | Purpose |
|---|---|---|---|
| Orders | Fact | 100,000+ | One row per order line item |
| Customers | Dimension | 8,000 | Customer master data |
| Products | Dimension | 500 | Product catalog |
| Categories | Dimension | 8 | Product category hierarchy |
| Sales_Reps | Dimension | 60 | Sales rep master data |
| Regions | Dimension | 6 countries / 40 states | Geography hierarchy |
| Returns | Fact | ~6,000 | Returned order line items |
| Monthly_Targets | Fact | 216 | Region-level monthly revenue targets |

---

## 5. Entity Relationship Diagram (ERD) — Text Form

```
                     ┌───────────────┐
                     │   Categories   │
                     │───────────────│
                     │ category_id PK│
                     │ category_name │
                     │ department    │
                     └───────┬───────┘
                             │ 1
                             │
                             │ M
                     ┌───────▼───────┐
        ┌────────────│    Products    │
        │            │───────────────│
        │            │ product_id  PK│
        │            │ category_id FK│
        │            │ product_name  │
        │            │ unit_price    │
        │            │ unit_cost     │
        │            │ brand         │
        │            └───────┬───────┘
        │                    │ 1
        │                    │
        │                    │ M
┌───────▼───────┐    ┌───────▼────────┐    ┌────────────────┐
│    Returns     │M  1│     Orders      │M  1│    Customers    │
│───────────────│◄───│─────────────────│───►│─────────────────│
│ return_id   PK│    │ order_id     PK │    │ customer_id  PK │
│ order_id    FK│    │ customer_id  FK │    │ customer_name   │
│ return_reason │    │ product_id   FK │    │ segment         │
│ return_date   │    │ rep_id       FK │    │ country         │
│ refund_amount │    │ region_id    FK │    │ signup_date     │
└───────────────┘    │ order_date      │    └─────────────────┘
                      │ ship_date       │
                      │ quantity        │
                      │ unit_price      │
                      │ discount        │
                      │ sales_channel   │
                      │ revenue         │
                      │ profit          │
                      └────────┬────────┘
                          M    │    1
                               │
                    ┌──────────▼─────────┐        ┌────────────────────┐
                    │    Sales_Reps       │        │      Regions        │
                    │────────────────────│        │─────────────────────│
                    │ rep_id          PK │        │ region_id        PK │
                    │ rep_name           │        │ country              │
                    │ region_id       FK │◄───────│ state                │
                    │ hire_date          │   M  1 │ region_name          │
                    └────────────────────┘        └──────────┬──────────┘
                                                               │ 1
                                                               │
                                                               │ M
                                                    ┌──────────▼──────────┐
                                                    │  Monthly_Targets     │
                                                    │─────────────────────│
                                                    │ target_id        PK │
                                                    │ region_id        FK │
                                                    │ month/year           │
                                                    │ target_revenue       │
                                                    └─────────────────────┘
```

**Relationships:**
- Categories 1→M Products
- Products 1→M Orders
- Customers 1→M Orders
- Sales_Reps 1→M Orders
- Regions 1→M Orders (via Sales_Reps and directly)
- Orders 1→M Returns (an order line can be returned)
- Regions 1→M Monthly_Targets

---

## 6. Deliberate Data Quality Issues (to be cleaned in later phases)

To simulate a real-world messy dataset, the raw data will include:

| Issue Type | Where Injected | Example |
|---|---|---|
| Missing values | Customers.email, Orders.discount, Products.unit_cost, Returns.return_reason | NULL / blank cells |
| Duplicate records | Orders (~1.5% dup rows), Customers (~1% dup rows) | Same order_id repeated |
| Incorrect values | Orders.quantity (negative), Customers.country (typos: "USA" vs "U.S.A" vs "United States") | Inconsistent categorical labels |
| Outliers | Orders.unit_price (extreme values), Orders.quantity (unrealistically high) | quantity = 5000 |
| Inconsistent formatting | Orders.order_date (mixed formats), Customers.phone | "2023/05/01" vs "01-05-2023" |
| Invalid foreign keys | Orders.customer_id referencing non-existent customers | Orphaned records |

This ensures the cleaning process (Excel + SQL + Python) is **necessary and demonstrable**, not cosmetic — which is exactly what makes this portfolio-credible.

---

## 7. Next Step

➡️ **Phase 2** will generate the actual dataset (Python script producing 100,000+ Orders rows plus all dimension tables, raw + cleaned versions, exported as CSV).

**Please confirm to proceed to Phase 2**, or let me know if you want any changes to the schema, table names, or business scenario first.
