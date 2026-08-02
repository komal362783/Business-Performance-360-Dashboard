"""
Business Performance 360 Dashboard - Data Cleaning (Python / Pandas)
=======================================================================
Loads the RAW (dirty) dataset and produces a cleaned, analysis-ready dataset
for EDA, feature engineering, KPI calculation, and Power BI.

This mirrors the cleaning logic already demonstrated in SQL (02_data_load_and_cleaning.sql)
but implemented with pandas — showing the equivalent toolkit a Data Analyst would use
when working outside a database (e.g. ad-hoc analysis, or a pipeline feeding Power BI directly).

Cleaning steps:
  1. Remove exact duplicate order rows (keep first occurrence)
  2. Fix negative quantities (data entry sign errors) -> absolute value
  3. Cap extreme quantity outliers at a business-reasonable maximum
  4. Fill missing discount values with 0 (no discount recorded = none applied)
  5. Fix unit_price outliers (>10x product's catalog price -> likely decimal/typo error)
  6. Standardize inconsistent country labels (USA/U.S.A/United States -> USA, etc.)
  7. Parse mixed order_date formats into a single standard datetime
  8. Remove orders with invalid/orphaned customer_id (no matching customer)
  9. Fill missing customer emails with a flag (kept as missing -- imputing fake emails
     would be misleading; flagged instead)
  10. Fill missing return_reason with 'Not Specified'
  11. Recompute revenue and profit from cleaned inputs (never trust pre-computed values
      once the underlying quantity/discount have been corrected)
"""

import pandas as pd
import numpy as np

BASE = "/home/claude/Business-Performance-360-Dashboard/Dataset"
RAW = f"{BASE}/raw"
OUT = f"{BASE}/powerbi_ready"

pd.set_option("display.max_columns", None)

print("=" * 70)
print("STEP 0: LOAD RAW DATA")
print("=" * 70)

orders = pd.read_csv(f"{RAW}/orders_raw.csv")
customers = pd.read_csv(f"{RAW}/customers_raw.csv")
returns = pd.read_csv(f"{RAW}/returns_raw.csv")
products = pd.read_csv(f"{RAW}/products.csv")
categories = pd.read_csv(f"{RAW}/categories.csv")
regions = pd.read_csv(f"{RAW}/regions.csv")
sales_reps = pd.read_csv(f"{RAW}/sales_reps.csv")
monthly_targets = pd.read_csv(f"{RAW}/monthly_targets.csv")

print(f"Orders (raw):        {len(orders):>8,} rows")
print(f"Customers (raw):     {len(customers):>8,} rows")
print(f"Returns (raw):       {len(returns):>8,} rows")
print(f"Products:            {len(products):>8,} rows")
print(f"Categories:          {len(categories):>8,} rows")
print(f"Regions:             {len(regions):>8,} rows")
print(f"Sales_Reps:          {len(sales_reps):>8,} rows")
print(f"Monthly_Targets:     {len(monthly_targets):>8,} rows")

# ============================================================================
# STEP 1: DEDUPLICATE ORDERS
# ============================================================================
print("\n" + "=" * 70)
print("STEP 1: DEDUPLICATE ORDERS")
print("=" * 70)

before = len(orders)
dup_order_ids = orders["order_id"].duplicated().sum()
orders = orders.drop_duplicates(subset="order_id", keep="first").reset_index(drop=True)
print(f"Removed {before - len(orders):,} duplicate order_id rows (kept first occurrence)")
print(f"Orders: {before:,} -> {len(orders):,}")

# ============================================================================
# STEP 2: FIX NEGATIVE / OUTLIER QUANTITIES
# ============================================================================
print("\n" + "=" * 70)
print("STEP 2: FIX QUANTITY ISSUES")
print("=" * 70)

neg_count = (orders["quantity"] < 0).sum()
orders["quantity"] = orders["quantity"].abs()
print(f"Fixed {neg_count:,} negative quantities (sign errors -> absolute value)")

outlier_count = (orders["quantity"] > 500).sum()
orders.loc[orders["quantity"] > 500, "quantity"] = 50
print(f"Capped {outlier_count:,} outlier quantities (>500 units) at 50 (business-reasonable max)")

# ============================================================================
# STEP 3: FILL MISSING DISCOUNTS
# ============================================================================
print("\n" + "=" * 70)
print("STEP 3: FILL MISSING DISCOUNTS")
print("=" * 70)

missing_disc = orders["discount"].isna().sum()
orders["discount"] = orders["discount"].fillna(0)
print(f"Filled {missing_disc:,} missing discount values with 0")

# ============================================================================
# STEP 4: FIX UNIT_PRICE OUTLIERS (decimal/typo errors vs. product catalog price)
# ============================================================================
print("\n" + "=" * 70)
print("STEP 4: FIX PRICE OUTLIERS")
print("=" * 70)

orders = orders.merge(products[["product_id", "unit_price", "unit_cost"]],
                       on="product_id", suffixes=("", "_catalog"))
price_outlier_mask = orders["unit_price"] > orders["unit_price_catalog"] * 10
price_outlier_count = price_outlier_mask.sum()
orders.loc[price_outlier_mask, "unit_price"] = orders.loc[price_outlier_mask, "unit_price_catalog"]
print(f"Fixed {price_outlier_count:,} unit_price outliers (>10x catalog price -> reset to catalog price)")

# ============================================================================
# STEP 5: STANDARDIZE COUNTRY LABELS
# ============================================================================
print("\n" + "=" * 70)
print("STEP 5: STANDARDIZE COUNTRY LABELS")
print("=" * 70)

country_map = {
    "usa": "USA", "u.s.a": "USA", "united states": "USA", "usa": "USA",
    "uk": "UK", "u.k.": "UK", "united kingdom": "UK",
    "canada": "Canada",
    "australia": "Australia", "aus": "Australia",
    "germany": "Germany", "de": "Germany",
    "india": "India", "ind": "India",
}
before_variants = customers["country"].nunique()
customers["country_original"] = customers["country"]  # audit trail, keep the raw value
customers["country"] = customers["country"].str.strip().str.lower().map(country_map)
after_variants = customers["country"].nunique()
print(f"Standardized country labels: {before_variants} raw variants -> {after_variants} clean values")
print(f"Clean country values: {sorted(customers['country'].unique())}")

# ============================================================================
# STEP 6: PARSE MIXED-FORMAT ORDER DATES
# ============================================================================
print("\n" + "=" * 70)
print("STEP 6: PARSE MIXED-FORMAT DATES")
print("=" * 70)

def parse_mixed_date(val):
    """Try multiple known formats (ISO, DD-MM-YYYY, MM/DD/YYYY, DD/MM/YYYY)."""
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return pd.to_datetime(val, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.NaT

before_parse_fail = orders["order_date"].astype(str).str.len().gt(0).sum()
orders["order_date"] = orders["order_date"].apply(parse_mixed_date)
unparsed = orders["order_date"].isna().sum()
print(f"Parsed order_date across 4 known formats. Unparseable rows: {unparsed:,}")
if unparsed > 0:
    orders = orders.dropna(subset=["order_date"])
    print(f"Dropped {unparsed:,} rows with unparseable dates")

orders["ship_date"] = pd.to_datetime(orders["ship_date"], errors="coerce")
# Fix cases where ship_date < order_date (data entry error) -> set to order_date + 3 days
bad_ship = orders["ship_date"] < orders["order_date"]
orders.loc[bad_ship, "ship_date"] = orders.loc[bad_ship, "order_date"] + pd.Timedelta(days=3)
print(f"Fixed {bad_ship.sum():,} rows where ship_date preceded order_date")

# ============================================================================
# STEP 7: REMOVE ORPHANED CUSTOMER FOREIGN KEYS
# ============================================================================
print("\n" + "=" * 70)
print("STEP 7: REMOVE ORPHANED FOREIGN KEYS")
print("=" * 70)

valid_customer_ids = set(customers["customer_id"])
orphan_mask = ~orders["customer_id"].isin(valid_customer_ids)
orphan_count = orphan_mask.sum()
orders = orders[~orphan_mask].reset_index(drop=True)
print(f"Removed {orphan_count:,} orders with invalid/orphaned customer_id")

# ============================================================================
# STEP 8: HANDLE MISSING EMAILS (flag, don't fabricate)
# ============================================================================
print("\n" + "=" * 70)
print("STEP 8: FLAG MISSING EMAILS")
print("=" * 70)

missing_email = customers["email"].isna().sum()
customers["email_missing_flag"] = customers["email"].isna()
print(f"Flagged {missing_email:,} customers with missing email (not fabricated -- flagged for CRM follow-up)")

# ============================================================================
# STEP 9: FILL MISSING RETURN REASONS
# ============================================================================
print("\n" + "=" * 70)
print("STEP 9: FILL MISSING RETURN REASONS")
print("=" * 70)

missing_reason = returns["return_reason"].isna().sum()
returns["return_reason"] = returns["return_reason"].fillna("Not Specified")
print(f"Filled {missing_reason:,} missing return_reason values with 'Not Specified'")

# ============================================================================
# STEP 10: RECOMPUTE REVENUE AND PROFIT FROM CLEANED INPUTS
# ============================================================================
print("\n" + "=" * 70)
print("STEP 10: RECOMPUTE REVENUE / PROFIT")
print("=" * 70)

orders["revenue"] = (orders["quantity"] * orders["unit_price"] * (1 - orders["discount"])).round(2)
orders["profit"] = (orders["revenue"] - (orders["quantity"] * orders["unit_cost"])).round(2)
orders = orders.drop(columns=["unit_price_catalog"])
print("Recomputed revenue and profit for all rows using cleaned quantity/price/discount/cost")
print(f"Total revenue after cleaning: ${orders['revenue'].sum():,.2f}")
print(f"Total profit after cleaning:  ${orders['profit'].sum():,.2f}")

# ============================================================================
# SAVE CLEANED DATA
# ============================================================================
orders.to_csv(f"{OUT}/orders_clean.csv", index=False)
customers.to_csv(f"{OUT}/customers_clean.csv", index=False)
returns.to_csv(f"{OUT}/returns_clean.csv", index=False)
products.to_csv(f"{OUT}/products.csv", index=False)
categories.to_csv(f"{OUT}/categories.csv", index=False)
regions.to_csv(f"{OUT}/regions.csv", index=False)
sales_reps.to_csv(f"{OUT}/sales_reps.csv", index=False)
monthly_targets.to_csv(f"{OUT}/monthly_targets.csv", index=False)

print("\n" + "=" * 70)
print("CLEANING COMPLETE -- SUMMARY")
print("=" * 70)
print(f"Final Orders:    {len(orders):,} rows (from {before:,} raw rows)")
print(f"Final Customers: {len(customers):,} rows")
print(f"Final Returns:   {len(returns):,} rows")
print(f"Saved to: {OUT}/")
