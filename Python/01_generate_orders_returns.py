"""
Business Performance 360 Dashboard - Orders & Returns Generator
==================================================================
Generates the Orders fact table (100,000+ rows) and Returns table,
then produces a deliberately DIRTY raw version for realistic cleaning practice.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

np.random.seed(7)
random.seed(7)

BASE = "/home/claude/Business-Performance-360-Dashboard/Dataset"
OUT_RAW = f"{BASE}/raw"
OUT_CLEAN = f"{BASE}/cleaned"

# Load dimension tables
customers = pd.read_csv(f"{OUT_CLEAN}/customers_clean_reference.csv")
products = pd.read_csv(f"{OUT_CLEAN}/products.csv")
regions = pd.read_csv(f"{OUT_CLEAN}/regions.csv")
sales_reps = pd.read_csv(f"{OUT_CLEAN}/sales_reps.csv")

N_ORDERS = 102000
SALES_CHANNELS = ["Online", "In-Store", "Wholesale", "Marketplace"]
CHANNEL_WEIGHTS = [0.45, 0.30, 0.15, 0.10]

# map customers to their region_id (by country/state match) for consistent geography
region_lookup = regions.set_index(["country", "state"])["region_id"].to_dict()
customers["region_id"] = customers.apply(
    lambda r: region_lookup.get((r["country"], r["state"]), random.choice(regions["region_id"].tolist())), axis=1
)

# reps mapped to region
reps_by_region = sales_reps.groupby("region_id")["rep_id"].apply(list).to_dict()

start_date = datetime(2023, 1, 1)
end_date = datetime(2025, 12, 31)
date_range_days = (end_date - start_date).days

# Seasonal weighting: boost Nov/Dec (holiday season)
def weighted_random_date():
    d = start_date + timedelta(days=int(np.random.triangular(0, date_range_days * 0.85, date_range_days)))
    return d

orders_rows = []
for order_id in range(1, N_ORDERS + 1):
    cust = customers.sample(1).iloc[0]
    prod = products.sample(1).iloc[0]
    region_id = cust["region_id"]
    reps_here = reps_by_region.get(region_id, sales_reps["rep_id"].tolist())
    rep_id = random.choice(reps_here)

    order_date = weighted_random_date()
    ship_lag = np.random.randint(1, 8)
    ship_date = order_date + timedelta(days=int(ship_lag))

    channel = np.random.choice(SALES_CHANNELS, p=CHANNEL_WEIGHTS)
    quantity = np.random.choice([1, 2, 3, 4, 5, 6, 8, 10], p=[0.35, 0.25, 0.15, 0.10, 0.06, 0.04, 0.03, 0.02])
    unit_price = prod["unit_price"]
    discount = round(np.random.choice([0, 0.05, 0.10, 0.15, 0.20, 0.25], p=[0.4, 0.2, 0.15, 0.15, 0.06, 0.04]), 2)

    revenue = round(quantity * unit_price * (1 - discount), 2)
    profit = round(revenue - (quantity * prod["unit_cost"]), 2)

    orders_rows.append([
        order_id, cust["customer_id"], prod["product_id"], rep_id, region_id,
        order_date.date(), ship_date.date(), channel, quantity, unit_price, discount, revenue, profit
    ])

orders = pd.DataFrame(orders_rows, columns=[
    "order_id", "customer_id", "product_id", "rep_id", "region_id",
    "order_date", "ship_date", "sales_channel", "quantity", "unit_price", "discount", "revenue", "profit"
])

# ------------------------------------------------------------------
# RETURNS table (~6% of orders get returned)
# ------------------------------------------------------------------
return_reasons = ["Damaged in Transit", "Wrong Item Shipped", "Not as Described", "Changed Mind", "Defective Product", "Other"]
returned_orders = orders.sample(frac=0.06, random_state=11)

returns_rows = []
for i, (_, o) in enumerate(returned_orders.iterrows(), start=1):
    return_date = pd.to_datetime(o["order_date"]) + timedelta(days=int(np.random.randint(2, 20)))
    reason = random.choice(return_reasons)
    refund_amount = round(o["revenue"] * np.random.uniform(0.8, 1.0), 2)
    returns_rows.append([i, o["order_id"], return_date.date(), reason, refund_amount])

returns = pd.DataFrame(returns_rows, columns=["return_id", "order_id", "return_date", "return_reason", "refund_amount"])

# ------------------------------------------------------------------
# MONTHLY TARGETS — calibrated against ACTUAL regional revenue so
# achievement % has a realistic, believable spread (some regions beat
# target, some miss it) instead of being uniformly random.
# ------------------------------------------------------------------
orders["order_date"] = pd.to_datetime(orders["order_date"])
orders["ym"] = orders["order_date"].dt.to_period("M")

actual_monthly = orders.groupby(["region_id", "ym"])["revenue"].sum().reset_index()

target_rows = []
tid = 1
for _, row in actual_monthly.iterrows():
    # target = actual revenue scaled by a random factor so achievement ranges
    # roughly 75%-125%, clustered around 95-105% (realistic performance spread)
    variance_factor = np.random.normal(loc=1.0, scale=0.13)
    variance_factor = np.clip(variance_factor, 0.72, 1.30)
    target_revenue = round(row["revenue"] / variance_factor, 2) if variance_factor > 0 else round(row["revenue"], 2)
    # convert real revenue back out: target = revenue / achievement_ratio, where achievement_ratio ~ variance_factor
    target_month = row["ym"].to_timestamp().date()
    target_rows.append([tid, row["region_id"], target_month, target_revenue])
    tid += 1

monthly_targets = pd.DataFrame(target_rows, columns=["target_id", "region_id", "target_month", "target_revenue"])
monthly_targets.to_csv(f"{OUT_CLEAN}/monthly_targets.csv", index=False)
orders = orders.drop(columns=["ym"])
orders["order_date"] = orders["order_date"].dt.date

print(f"Monthly Targets (revenue-calibrated): {len(monthly_targets)} rows")

# Save CLEAN versions
orders.to_csv(f"{OUT_CLEAN}/orders.csv", index=False)
returns.to_csv(f"{OUT_CLEAN}/returns.csv", index=False)
customers.drop(columns=["region_id"]).to_csv(f"{OUT_CLEAN}/customers.csv", index=False)  # keep original clean customers (region derived, not stored)

print(f"Clean Orders: {len(orders)} rows")
print(f"Clean Returns: {len(returns)} rows")
print(f"Total Revenue (clean): ${orders['revenue'].sum():,.2f}")
print(f"Total Profit (clean): ${orders['profit'].sum():,.2f}")

# ==================================================================
# NOW BUILD THE DIRTY "RAW" VERSIONS
# ==================================================================
orders_raw = orders.copy()
customers_raw = customers.copy()
returns_raw = returns.copy()

# --- 1. Duplicates (~1.5% of orders duplicated) ---
dupe_sample = orders_raw.sample(frac=0.015, random_state=21)
orders_raw = pd.concat([orders_raw, dupe_sample], ignore_index=True)

# --- 2. Missing values ---
# discount missing ~5%
missing_idx = orders_raw.sample(frac=0.05, random_state=22).index
orders_raw.loc[missing_idx, "discount"] = np.nan

# customer email missing ~3%
missing_email_idx = customers_raw.sample(frac=0.03, random_state=23).index
customers_raw.loc[missing_email_idx, "email"] = np.nan

# --- 3. Incorrect / inconsistent values ---
# negative quantity errors (~0.5%)
neg_idx = orders_raw.sample(frac=0.005, random_state=24).index
orders_raw.loc[neg_idx, "quantity"] = -orders_raw.loc[neg_idx, "quantity"]

# ship_date before order_date (data entry error, ~0.3%)
bad_ship_idx = orders_raw.sample(frac=0.003, random_state=25).index
bad_ship_dates = (pd.to_datetime(orders_raw.loc[bad_ship_idx, "order_date"]) - timedelta(days=3)).dt.date
orders_raw.loc[bad_ship_idx, "ship_date"] = bad_ship_dates

# inconsistent country labels in customers (~ mix casing/abbreviations)
country_variants = {
    "USA": ["USA", "U.S.A", "United States", "usa"],
    "UK": ["UK", "U.K.", "United Kingdom", "uk"],
    "Canada": ["Canada", "CANADA", "canada"],
    "Australia": ["Australia", "AUS", "australia"],
    "Germany": ["Germany", "DE", "germany"],
    "India": ["India", "IND", "india"],
}
def messy_country(c):
    if np.random.rand() < 0.12:  # 12% of rows get a messy variant
        return random.choice(country_variants.get(c, [c]))
    return c

customers_raw["country"] = customers_raw["country"].apply(messy_country)

# --- 4. Outliers ---
# extreme quantity outliers (~0.2%)
outlier_idx = orders_raw.sample(frac=0.002, random_state=26).index
orders_raw.loc[outlier_idx, "quantity"] = np.random.randint(500, 5000, size=len(outlier_idx))

# extreme unit_price outliers (data entry typo, ~0.15%) - e.g. missing decimal point
price_outlier_idx = orders_raw.sample(frac=0.0015, random_state=27).index
orders_raw.loc[price_outlier_idx, "unit_price"] = orders_raw.loc[price_outlier_idx, "unit_price"] * 100

# --- 5. Invalid foreign keys (orphaned customer_id, ~0.2%) ---
orphan_idx = orders_raw.sample(frac=0.002, random_state=28).index
orders_raw.loc[orphan_idx, "customer_id"] = np.random.randint(90000, 99999, size=len(orphan_idx))

# --- 6. Inconsistent date formats (convert order_date to mixed string formats) ---
def messy_date_format(d):
    d = pd.to_datetime(d)
    fmt = random.choice(["%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y"])
    return d.strftime(fmt)

sample_fmt_idx = orders_raw.sample(frac=0.10, random_state=29).index
orders_raw["order_date"] = orders_raw["order_date"].astype(str)
orders_raw.loc[sample_fmt_idx, "order_date"] = orders_raw.loc[sample_fmt_idx, "order_date"].apply(messy_date_format)

# --- 7. Returns missing reason (~8%) ---
missing_reason_idx = returns_raw.sample(frac=0.08, random_state=30).index
returns_raw.loc[missing_reason_idx, "return_reason"] = np.nan

# --- 8. Recompute revenue/profit incorrectly for some rows (simulating formula errors) left as-is
# (we intentionally do NOT recompute revenue/profit for dirty rows -> inconsistency for cleaning practice)

# Shuffle order rows so dupes aren't adjacent (more realistic)
orders_raw = orders_raw.sample(frac=1, random_state=31).reset_index(drop=True)

# Save RAW (dirty) versions
orders_raw.to_csv(f"{OUT_RAW}/orders_raw.csv", index=False)
customers_raw.to_csv(f"{OUT_RAW}/customers_raw.csv", index=False)
returns_raw.to_csv(f"{OUT_RAW}/returns_raw.csv", index=False)

# copy dimension tables into raw folder too (unchanged, but kept alongside for full raw dataset)
for fname in ["categories.csv", "products.csv", "regions.csv", "sales_reps.csv", "monthly_targets.csv"]:
    pd.read_csv(f"{OUT_CLEAN}/{fname}").to_csv(f"{OUT_RAW}/{fname}", index=False)

print("\n--- RAW (dirty) dataset generated ---")
print(f"Orders raw: {len(orders_raw)} rows (includes duplicates)")
print(f"Customers raw: {len(customers_raw)} rows")
print(f"Returns raw: {len(returns_raw)} rows")
print(f"Missing discount values: {orders_raw['discount'].isna().sum()}")
print(f"Missing customer emails: {customers_raw['email'].isna().sum()}")
print(f"Negative quantities: {(orders_raw['quantity'] < 0).sum()}")
print(f"Outlier quantities (>500): {(orders_raw['quantity'] > 500).sum()}")
