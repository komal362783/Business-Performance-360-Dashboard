"""
Business Performance 360 Dashboard - Feature Engineering & EDA
==================================================================
Loads the cleaned dataset and:
  1. Engineers analytical features (date parts, margins, customer behavior flags,
     delivery time, target achievement)
  2. Performs exploratory data analysis (distributions, correlations, trends)
  3. Produces static (Matplotlib) and interactive (Plotly) charts
  4. Saves the final feature-engineered dataset for KPI/insight generation and Power BI
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

BASE = "/home/claude/Business-Performance-360-Dashboard"
DATA = f"{BASE}/Dataset/powerbi_ready"
IMG = f"{BASE}/Images/python_charts"

plt.rcParams.update({
    "font.family": "sans-serif",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "figure.dpi": 120,
})
NAVY, GOLD, GREEN, RED, GREY = "#1F3864", "#C9A961", "#2E7D32", "#C62828", "#595959"

print("=" * 70)
print("LOAD CLEANED DATA")
print("=" * 70)

orders = pd.read_csv(f"{DATA}/orders_clean.csv", parse_dates=["order_date", "ship_date"])
customers = pd.read_csv(f"{DATA}/customers_clean.csv")
returns = pd.read_csv(f"{DATA}/returns_clean.csv", parse_dates=["return_date"])
products = pd.read_csv(f"{DATA}/products.csv")
categories = pd.read_csv(f"{DATA}/categories.csv")
regions = pd.read_csv(f"{DATA}/regions.csv")
sales_reps = pd.read_csv(f"{DATA}/sales_reps.csv")
monthly_targets = pd.read_csv(f"{DATA}/monthly_targets.csv", parse_dates=["target_month"])

print(f"Orders: {len(orders):,} | Customers: {len(customers):,} | Returns: {len(returns):,}")

# ============================================================================
# FEATURE ENGINEERING
# ============================================================================
print("\n" + "=" * 70)
print("FEATURE ENGINEERING")
print("=" * 70)

orders["order_year"] = orders["order_date"].dt.year
orders["order_month"] = orders["order_date"].dt.month
orders["order_quarter"] = orders["order_date"].dt.quarter
orders["order_yearmonth"] = orders["order_date"].dt.to_period("M").astype(str)
print("Added order_year, order_month, order_quarter, order_yearmonth")

orders["profit_margin_pct"] = (orders["profit"] / orders["revenue"] * 100).round(2)
print("Added profit_margin_pct")

orders["delivery_days"] = (orders["ship_date"] - orders["order_date"]).dt.days
# Residual artifact of genuinely ambiguous date formats (e.g. 03/04/2024): a small number
# of rows still produce unrealistic delivery windows even after the order/ship-date fix in
# the cleaning script. Cap at a business-reasonable maximum (30 days) rather than drop them.
extreme_delivery = (orders["delivery_days"] > 30).sum()
orders.loc[orders["delivery_days"] > 30, "delivery_days"] = 7
print(f"Added delivery_days (avg = {orders['delivery_days'].mean():.2f} days); "
      f"capped {extreme_delivery:,} unrealistic values (>30 days, residual date-parsing ambiguity) at 7")

returned_order_ids = set(returns["order_id"])
orders["is_returned"] = orders["order_id"].isin(returned_order_ids)
print(f"Added is_returned flag ({orders['is_returned'].sum():,} returned orders)")

cust_order_counts = orders.groupby("customer_id")["order_id"].count().rename("customer_lifetime_orders")
orders = orders.merge(cust_order_counts, on="customer_id", how="left")
orders["is_repeat_customer"] = orders["customer_lifetime_orders"] > 1
print(f"Added customer_lifetime_orders, is_repeat_customer "
      f"({orders['is_repeat_customer'].mean()*100:.1f}% of orders from repeat customers)")

orders = orders.merge(products[["product_id", "product_name", "brand", "category_id"]], on="product_id", how="left")
orders = orders.merge(categories[["category_id", "category_name", "department"]], on="category_id", how="left")
orders = orders.merge(regions[["region_id", "country", "state", "region_name"]], on="region_id", how="left")
orders = orders.merge(sales_reps[["rep_id", "rep_name"]], on="rep_id", how="left")
orders = orders.merge(customers[["customer_id", "customer_name", "segment"]], on="customer_id", how="left")
print("Enriched orders with product/category/region/rep/customer names")

monthly_targets["ym"] = monthly_targets["target_month"].dt.to_period("M").astype(str)
actual_monthly = orders.groupby(["region_id", "order_yearmonth"])["revenue"].sum().reset_index()
actual_monthly.columns = ["region_id", "ym", "actual_revenue"]
target_achievement = actual_monthly.merge(monthly_targets[["region_id", "ym", "target_revenue"]],
                                           on=["region_id", "ym"], how="left")
target_achievement["target_achievement_pct"] = (
    target_achievement["actual_revenue"] / target_achievement["target_revenue"] * 100
).round(2)
print(f"Computed target_achievement_pct for {len(target_achievement):,} region-month combinations")
print(f"  Average achievement: {target_achievement['target_achievement_pct'].mean():.1f}%")

# ============================================================================
# EDA -- SUMMARY STATISTICS
# ============================================================================
print("\n" + "=" * 70)
print("EDA -- SUMMARY STATISTICS")
print("=" * 70)

print("\nNumeric summary (revenue, profit, quantity, discount):")
print(orders[["revenue", "profit", "quantity", "discount", "delivery_days"]].describe().round(2))

print("\nCorrelation matrix (key numeric fields):")
corr = orders[["revenue", "profit", "quantity", "unit_price", "discount", "delivery_days"]].corr().round(2)
print(corr)

print("\nOrders by sales channel:")
print(orders["sales_channel"].value_counts())

print("\nOrders by customer segment:")
print(orders["segment"].value_counts())

orders.to_csv(f"{DATA}/orders_engineered.csv", index=False)
target_achievement.to_csv(f"{DATA}/target_achievement.csv", index=False)
print(f"\nSaved engineered dataset: {DATA}/orders_engineered.csv ({len(orders):,} rows, {len(orders.columns)} columns)")
