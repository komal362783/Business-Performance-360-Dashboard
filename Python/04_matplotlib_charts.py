"""
Business Performance 360 Dashboard - Static Charts (Matplotlib)
===================================================================
Generates the core set of executive-facing static charts from the
feature-engineered dataset. Saved as high-res PNGs for the project report
and portfolio README.
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
    "grid.alpha": 0.25,
    "figure.dpi": 130,
    "font.size": 10,
})
NAVY, GOLD, GREEN, RED, GREY, BLUE = "#1F3864", "#C9A961", "#2E7D32", "#C62828", "#595959", "#2E5395"

orders = pd.read_csv(f"{DATA}/orders_engineered.csv", parse_dates=["order_date"])
returns = pd.read_csv(f"{DATA}/returns_clean.csv", parse_dates=["return_date"])

def money_fmt(ax, axis="y"):
    fmt = mticker.FuncFormatter(lambda x, _: f"${x/1e6:.1f}M" if abs(x) >= 1e6 else f"${x/1e3:.0f}K")
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(fmt)

def fmt_money_short(v):
    return f"${v/1e6:.1f}M" if abs(v) >= 1e6 else f"${v/1e3:.0f}K"

# ============================================================================
# CHART 1: Monthly Revenue Trend
# ============================================================================
monthly = orders.groupby("order_yearmonth")["revenue"].sum().reset_index()
COMPLETE_THROUGH = "2025-07"
fig, ax = plt.subplots(figsize=(11, 4.5))
ax.plot(monthly["order_yearmonth"], monthly["revenue"], color=NAVY, linewidth=2)
ax.fill_between(range(len(monthly)), monthly["revenue"], color=NAVY, alpha=0.08)
# Shade + annotate the incomplete reporting window (see data window note in insights)
taper_start_idx = monthly[monthly["order_yearmonth"] > COMPLETE_THROUGH].index.min()
if pd.notna(taper_start_idx):
    ax.axvspan(taper_start_idx - 0.5, len(monthly) - 0.5, color=GREY, alpha=0.12)
    ax.text(taper_start_idx, monthly["revenue"].max() * 0.95, "  Incomplete\n  reporting window",
            fontsize=8, color=GREY, va="top")
ax.set_title("Monthly Revenue Trend (2023–2025)", fontsize=13, fontweight="bold", color=NAVY)
money_fmt(ax)
ax.set_xticks(range(0, len(monthly), 3))
ax.set_xticklabels(monthly["order_yearmonth"][::3], rotation=45, ha="right")
plt.tight_layout()
plt.savefig(f"{IMG}/01_monthly_revenue_trend.png")
plt.close()

# ============================================================================
# CHART 2: Revenue & Profit by Category
# ============================================================================
cat = orders.groupby("category_name")[["revenue", "profit"]].sum().sort_values("revenue", ascending=True)
fig, ax = plt.subplots(figsize=(9, 5))
y = np.arange(len(cat))
ax.barh(y - 0.2, cat["revenue"], height=0.4, color=NAVY, label="Revenue")
ax.barh(y + 0.2, cat["profit"], height=0.4, color=GOLD, label="Profit")
ax.set_yticks(y)
ax.set_yticklabels(cat.index)
ax.set_title("Revenue & Profit by Category", fontsize=13, fontweight="bold", color=NAVY)
money_fmt(ax, axis="x")
ax.legend(frameon=False)
plt.tight_layout()
plt.savefig(f"{IMG}/02_revenue_profit_by_category.png")
plt.close()

# ============================================================================
# CHART 3: Top 10 Products by Revenue
# ============================================================================
top_prod = orders.groupby("product_name")["revenue"].sum().sort_values(ascending=False).head(10)
fig, ax = plt.subplots(figsize=(9, 5))
ax.barh(top_prod.index[::-1], top_prod.values[::-1], color=BLUE)
ax.set_title("Top 10 Products by Revenue", fontsize=13, fontweight="bold", color=NAVY)
money_fmt(ax, axis="x")
plt.tight_layout()
plt.savefig(f"{IMG}/03_top10_products.png")
plt.close()

# ============================================================================
# CHART 4: Revenue by Sales Channel (donut, labels pulled outside with leader lines)
# ============================================================================
channel = orders.groupby("sales_channel")["revenue"].sum().sort_values(ascending=False)
total_channel = channel.sum()
colors = [NAVY, BLUE, GOLD, GREY]

fig, ax = plt.subplots(figsize=(8, 7))
wedges, _ = ax.pie(
    channel.values, startangle=90, colors=colors,
    wedgeprops=dict(width=0.4, edgecolor="white"), labels=None
)

# Pull percentage + label text outside the donut with a leader line, positioned
# so they don't overlap each other (classic matplotlib "exploded label" pattern).
# IMPORTANT: use the SAME radial multiplier for x and y (true polar scaling) --
# scaling x and y by different factors pulls top/bottom labels in closer to the
# donut than side labels, which is what caused labels to crowd/overlap the edge.
bbox_props = dict(boxstyle="round,pad=0.3", fc="white", ec="none", alpha=0.0)
kw = dict(arrowprops=dict(arrowstyle="-", color=GREY, lw=0.9),
          bbox=bbox_props, zorder=0, va="center")

LABEL_RADIUS = 1.38   # consistent radial distance for every label
ANCHOR_RADIUS = 1.02  # leader line starts just outside the wedge, not inside it

for i, wedge in enumerate(wedges):
    ang = (wedge.theta2 - wedge.theta1) / 2. + wedge.theta1
    y = np.sin(np.deg2rad(ang))
    x = np.cos(np.deg2rad(ang))
    horizontalalignment = "left" if x >= 0 else "right"
    connectionstyle = f"angle,angleA=0,angleB={ang}"
    kw["arrowprops"].update({"connectionstyle": connectionstyle})
    pct = channel.values[i] / total_channel * 100
    label = f"{channel.index[i]}\n{pct:.1f}%  ({fmt_money_short(channel.values[i])})"
    ax.annotate(
        label, xy=(x * ANCHOR_RADIUS, y * ANCHOR_RADIUS), xytext=(x * LABEL_RADIUS, y * LABEL_RADIUS),
        horizontalalignment=horizontalalignment, fontsize=10, fontweight="bold",
        color=NAVY, **kw
    )

ax.set_title("Revenue Share by Sales Channel", fontsize=13, fontweight="bold", color=NAVY, pad=20)
ax.set_xlim(-1.8, 1.8)
ax.set_ylim(-1.6, 1.6)
plt.tight_layout()
plt.savefig(f"{IMG}/04_revenue_by_channel.png")
plt.close()

# ============================================================================
# CHART 5: Revenue by Country
# ============================================================================
country = orders.groupby("country")["revenue"].sum().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.bar(country.index, country.values, color=NAVY)
ax.set_title("Revenue by Country", fontsize=13, fontweight="bold", color=NAVY)
money_fmt(ax)
plt.tight_layout()
plt.savefig(f"{IMG}/05_revenue_by_country.png")
plt.close()

# ============================================================================
# CHART 6: Customer Segment Revenue Split
# ============================================================================
seg = orders.groupby("segment")["revenue"].sum().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(7, 4.5))
bars = ax.bar(seg.index, seg.values, color=[NAVY, GOLD, GREEN])
money_fmt(ax)
ax.set_title("Revenue by Customer Segment", fontsize=13, fontweight="bold", color=NAVY)
plt.tight_layout()
plt.savefig(f"{IMG}/06_revenue_by_segment.png")
plt.close()

# ============================================================================
# CHART 7: Return Reason Breakdown
# ============================================================================
reason = returns["return_reason"].value_counts().sort_values(ascending=True)
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.barh(reason.index, reason.values, color=RED)
ax.set_title("Return Reason Breakdown", fontsize=13, fontweight="bold", color=NAVY)
plt.tight_layout()
plt.savefig(f"{IMG}/07_return_reasons.png")
plt.close()

# ============================================================================
# CHART 8: Profit Margin Distribution (histogram)
# ============================================================================
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.hist(orders["profit_margin_pct"], bins=40, color=BLUE, edgecolor="white")
ax.axvline(orders["profit_margin_pct"].mean(), color=RED, linestyle="--", linewidth=1.5,
           label=f"Mean = {orders['profit_margin_pct'].mean():.1f}%")
ax.set_title("Profit Margin Distribution", fontsize=13, fontweight="bold", color=NAVY)
ax.set_xlabel("Profit Margin %")
ax.legend(frameon=False)
plt.tight_layout()
plt.savefig(f"{IMG}/08_profit_margin_distribution.png")
plt.close()

# ============================================================================
# CHART 9: Quantity Outlier Check (boxplot, before vs after conceptually shown via raw distribution)
# ============================================================================
fig, ax = plt.subplots(figsize=(6, 5))
ax.boxplot(orders["quantity"], vert=True, patch_artist=True,
           boxprops=dict(facecolor=NAVY, alpha=0.6), medianprops=dict(color=GOLD, linewidth=2))
ax.set_title("Order Quantity Distribution (post-cleaning)", fontsize=13, fontweight="bold", color=NAVY)
ax.set_ylabel("Quantity")
plt.tight_layout()
plt.savefig(f"{IMG}/09_quantity_boxplot.png")
plt.close()

# ============================================================================
# CHART 10: Target Achievement by Region (top/bottom 10)
# ============================================================================
ta = pd.read_csv(f"{DATA}/target_achievement.csv")
ta_summary = ta.groupby("region_id")["target_achievement_pct"].mean().reset_index()
regions_df = pd.read_csv(f"{DATA}/regions.csv")
ta_summary = ta_summary.merge(regions_df[["region_id", "region_name"]], on="region_id")
ta_summary = ta_summary.sort_values("target_achievement_pct", ascending=False)
top_bottom = pd.concat([ta_summary.head(8), ta_summary.tail(8)])
fig, ax = plt.subplots(figsize=(9, 6))
colors_bar = [GREEN if v >= 100 else RED for v in top_bottom["target_achievement_pct"]]
ax.barh(top_bottom["region_name"], top_bottom["target_achievement_pct"], color=colors_bar)
ax.axvline(100, color=GREY, linestyle="--", linewidth=1)
ax.set_title("Target Achievement % — Best & Worst Regions", fontsize=13, fontweight="bold", color=NAVY)
ax.set_xlabel("Target Achievement %")
plt.tight_layout()
plt.savefig(f"{IMG}/10_target_achievement_regions.png")
plt.close()

print(f"Saved 10 charts to {IMG}/")
import os
for f in sorted(os.listdir(IMG)):
    print(" -", f)
