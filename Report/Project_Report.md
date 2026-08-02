# Project Report
## Business Performance 360° Dashboard (CEO Dashboard)
### GlobalMart Retail Inc. — End-to-End Data Analytics Project

---

## 1. Business Problem

GlobalMart Retail Inc. is a multinational retailer operating across six
countries (USA, UK, Canada, Australia, Germany, India), eight product
categories, and four sales channels (Online, In-Store, Wholesale,
Marketplace). Leadership received fragmented, inconsistently formatted
reports from regional teams on different schedules, with no single view of
where revenue and profit were actually being generated, which products or
regions were winning or losing, or whether the company was on track against
targets.

**The ask**: build a unified pipeline — raw data through cleaning, database
modeling, statistical analysis, and an executive dashboard — culminating in
the **Business Performance 360° Dashboard**, a single source of truth for
the CEO and executive team.

---

## 2. Objectives

1. Consolidate order, customer, product, returns, and target data into one
   analytical model.
2. Clean and validate realistic, messy data (nulls, duplicates, bad values,
   outliers, inconsistent labels).
3. Answer 40 real business questions via SQL.
4. Perform EDA, feature engineering, and KPI computation in Python.
5. Deliver an interactive Excel workbook and an executive-grade Power BI
   dashboard across 8 pages.
6. Translate analysis into insights and actionable recommendations for
   leadership.

---

## 3. Dataset Description

A synthetic but realistic dataset was generated to represent 3 years
(2023–2025) of GlobalMart operations:

| Table | Rows | Role |
|---|---|---|
| Orders | 102,000 (clean) / 103,530 (raw) | Fact table — one row per order line |
| Customers | 8,000 | Dimension |
| Products | 500 | Dimension |
| Categories | 8 | Dimension |
| Regions | 30 (6 countries) | Dimension |
| Sales Reps | 60 | Dimension |
| Returns | 6,120 | Fact table |
| Monthly Targets | 1,080 (region × month) | Fact table, calibrated to actual regional revenue with realistic variance |

Full column-level specifications are in `Report/02_Data_Dictionary.md`, and
the business scenario / ERD are documented in `Report/01_Project_Foundation.md`.

**Deliberately injected data-quality issues** (so cleaning is genuinely
necessary, not cosmetic): duplicate order rows, missing values (discount,
email, return reason), negative quantities, outlier quantities and prices,
inconsistent country labels, mixed date formats, and orphaned foreign keys.

---

## 4. Data Cleaning Process

Cleaning was implemented **independently in three layers** — SQL, Excel, and
Python — so the project demonstrates the same competency across every tool a
Data Analyst is expected to know, rather than cleaning once and re-exporting.

| Layer | Approach |
|---|---|
| **SQL** (`SQL/02_data_load_and_cleaning.sql`) | Staging tables, `ALTER` for audit columns, `UPDATE` to standardize countries/fix negatives/fill missing discounts/cap outliers, `DELETE` for duplicates and orphaned FKs, then promotion to production tables |
| **Excel** (`Excel/CEO_Dashboard_Workbook.xlsx`) | Live formulas (never hardcoded) on a 20,000-row subset: `ABS()`/capping for quantity issues, `IF(ISBLANK())` for missing discounts, `INDEX/MATCH` against a country-mapping lookup table, `MATCH`-based duplicate detection |
| **Python** (`Python/02_data_cleaning.py`) | Pandas-based cleaning on the **full 103,530-row raw dataset**: dedup, quantity/price outlier correction, multi-format date parsing, country standardization, orphaned-FK removal, missing-value handling, and full revenue/profit recomputation from cleaned inputs |

**Real bugs caught during validation** (documented transparently rather than
hidden): a product-generation bug that miscategorized all 500 products into
a single category (fixed and regenerated); an O(n²) Excel formula pattern
that caused a genuine multi-minute computation hang (replaced with O(n)
helper-column patterns); a duplicate-flagging formula that excluded *both*
copies of a duplicate instead of keeping one (fixed with a MATCH-based
first-occurrence check); and a residual date-parsing ambiguity that produced
a small number of unrealistic delivery-time outliers (capped with a
documented rationale).

---

## 5. SQL Layer

`SQL/01_create_tables.sql` defines the full schema — 8 tables, primary/foreign
keys, `CHECK` constraints, and 10 performance indexes — plus sample `INSERT`
statements. `SQL/03_business_queries.sql` contains **40 business queries**
across 7 categories (Revenue/Profit, Product, Regional, Customer, Sales
Channel/Order, Sales Rep, Returns), every one of which was actually executed
against a live SQLite database built from the real dataset and validated for
correctness — not just written and assumed correct. This process caught and
fixed two real bugs: a fan-out join that inflated target-achievement
denominators, and unrealistic monthly targets that made every region look
like it was overachieving (recalibrated to derive targets from actual
regional revenue with realistic variance).

---

## 6. Python Layer

Six scripts form the full pipeline:

1. `00_generate_dataset.py` / `01_generate_orders_returns.py` — synthetic
   dataset generation with intentional data-quality issues
2. `02_data_cleaning.py` — pandas-based cleaning (see Section 4)
3. `03_eda_feature_engineering.py` — feature engineering (date parts, profit
   margin, delivery days, returns flag, repeat-customer flag, target
   achievement) and exploratory summary statistics / correlation analysis
4. `04_matplotlib_charts.py` — 10 static executive charts, all rendered and
   visually verified
5. `05_plotly_interactive_charts.py` — 8 interactive charts (treemap,
   sunburst, heatmap, scatter, etc.); the code is complete and every
   underlying pandas transformation was independently validated, though the
   `plotly` package itself could not be installed in this sandboxed,
   offline environment to render live HTML output
6. `06_kpi_insights_export.py` — 15 KPIs, 27 data-driven business insights,
   and the full Power BI star-schema export

A genuine data-realism issue was caught and handled transparently in this
phase: the underlying date-sampling distribution created an artificial
taper in the final months of the dataset, which would have misrepresented
company performance as declining. Rather than silently regenerate the whole
dataset (which would have invalidated numbers already delivered in the SQL
and Excel phases), the issue was handled the way a real analyst would treat
an incomplete current reporting period — annotated, excluded from
trend-based KPIs, and documented.

---

## 7. Dashboard Layer (Excel + Power BI)

**Excel** (`Excel/CEO_Dashboard_Workbook.xlsx`): 16 sheets, 430,262 live
formulas, zero calculation errors (verified via automated recalculation) —
lookup tables, raw/cleaned Orders and Returns with cleaning + enrichment
formulas, a KPI summary with conditional formatting, and 5 pivot-style
summary sheets each paired with a chart.

**Power BI** (`PowerBI/`): since Power BI Desktop isn't available in this
environment, the deliverable is a complete build package —
`CEO_Dashboard_BuildGuide.md` (data model, DAX measures reference, and
page-by-page specs for all 8 pages: Executive Overview, Sales Analysis,
Customer Analysis, Product Analysis, Regional Analysis, Profit Analysis,
Returns Dashboard, Forecast Dashboard), `DAX/measures.dax` (30+ measures),
an interactive `CEO_Dashboard_Mockup.html` (real data, 18 charts, validated
with zero runtime errors), and `Executive_Walkthrough.md` (a presentation
script for walking leadership through the dashboard).

---

## 8. Business Insights & Recommendations

27 data-driven insight statements (covering 29 individual findings) and 15
prioritized executive recommendations, each tied to the specific insight(s)
that motivate it. See `Report/Business_Insights_and_Recommendations.md` for
the full detail. Headline findings: $112.6M revenue at 47.2% margin, 74.5%
like-for-like YoY growth, $5.81M in return-driven profit leakage (5.16% of
revenue), and 42.5% of region-months missing their revenue target despite a
healthy company-wide average.

---

## 9. Future Scope

- Connect the Power BI model to a live database (Azure SQL / Snowflake) with
  scheduled refresh, replacing the static CSV import used in this project
- Build a genuine customer retention/cohort model (the current repeat-rate
  metric is flagged as a dataset-scale artifact, not production-ready)
- Extend the forecast page from a simple trend projection to a proper
  time-series model (Prophet, ARIMA) once more historical seasons are available
- Add row-level security in Power BI so regional VPs see only their own region
- Automate the SQL cleaning pipeline as a scheduled ETL job (Airflow / dbt)
  rather than a manual script run
- A/B test the discount-strategy recommendation (#5) before a full rollout,
  given the observed margin/discount tradeoff

---

## 10. Project Structure

```
Business-Performance-360-Dashboard/
├── Dataset/            raw/, cleaned/, powerbi_ready/ (star schema)
├── SQL/                schema, cleaning, 40 business queries
├── Python/             generation, cleaning, EDA, charts, KPI/insights export
├── Excel/               CEO_Dashboard_Workbook.xlsx
├── PowerBI/             build guide, DAX measures, HTML mockup, walkthrough
├── Images/              Python-generated charts
├── Report/              this report, data dictionary, insights & recommendations
├── Resume/              resume content
└── README.md
```
