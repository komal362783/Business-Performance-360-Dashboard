"""
Business Performance 360 Dashboard - Interactive Charts (Plotly)
====================================================================
Generates interactive HTML charts (hover tooltips, zoom, filtering) from the
feature-engineered dataset. These are the "explore it yourself" companions
to the static Matplotlib charts -- ideal for embedding in a portfolio site
or sharing as standalone HTML files.

NOTE ON THIS ENVIRONMENT: this sandbox has no internet access, so `plotly`
could not be pip-installed here to render actual output files. The code
below is complete and correct standard Plotly usage -- run it in any
environment with `pip install plotly` (or `pip install plotly --break-system-packages`)
to generate the HTML files. Each fig.write_html() call produces a
self-contained interactive chart.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

BASE = "/home/claude/Business-Performance-360-Dashboard"
DATA = f"{BASE}/Dataset/powerbi_ready"
OUT = f"{BASE}/Images/python_charts/interactive"

NAVY, GOLD, GREEN, RED, GREY, BLUE = "#1F3864", "#C9A961", "#2E7D32", "#C62828", "#595959", "#2E5395"
BRAND_SEQ = [NAVY, GOLD, GREEN, RED, BLUE, GREY]

orders = pd.read_csv(f"{DATA}/orders_engineered.csv", parse_dates=["order_date"])
returns = pd.read_csv(f"{DATA}/returns_clean.csv", parse_dates=["return_date"])
target_achievement = pd.read_csv(f"{DATA}/target_achievement.csv")
regions = pd.read_csv(f"{DATA}/regions.csv")

TEMPLATE = "plotly_white"

# ============================================================================
# CHART 1: Monthly Revenue Trend (interactive line, hover for exact values)
# ============================================================================
monthly = orders.groupby("order_yearmonth")["revenue"].sum().reset_index()
fig1 = px.line(
    monthly, x="order_yearmonth", y="revenue",
    title="Monthly Revenue Trend (2023-2025)",
    labels={"order_yearmonth": "Month", "revenue": "Revenue (USD)"},
    template=TEMPLATE,
)
fig1.update_traces(line_color=NAVY, line_width=3, fill="tozeroy", fillcolor="rgba(31,56,100,0.08)")
fig1.update_layout(hovermode="x unified", title_font=dict(size=18, color=NAVY))
fig1.write_html(f"{OUT}/01_monthly_revenue_trend.html")

# ============================================================================
# CHART 2: Revenue vs Profit by Category (grouped bar, hover for values)
# ============================================================================
cat = orders.groupby("category_name")[["revenue", "profit"]].sum().reset_index()
cat = cat.sort_values("revenue", ascending=False)
fig2 = px.bar(
    cat, x="category_name", y=["revenue", "profit"], barmode="group",
    title="Revenue vs Profit by Category",
    labels={"category_name": "Category", "value": "USD", "variable": "Metric"},
    color_discrete_sequence=[NAVY, GOLD], template=TEMPLATE,
)
fig2.update_layout(title_font=dict(size=18, color=NAVY))
fig2.write_html(f"{OUT}/02_revenue_profit_by_category.html")

# ============================================================================
# CHART 3: Revenue by Region -- Treemap (drill into country -> region)
# ============================================================================
region_rev = orders.groupby(["country", "region_name"])["revenue"].sum().reset_index()
fig3 = px.treemap(
    region_rev, path=["country", "region_name"], values="revenue",
    title="Revenue Breakdown: Country -> Region",
    color="revenue", color_continuous_scale=["#DCE6F1", NAVY],
    template=TEMPLATE,
)
fig3.update_layout(title_font=dict(size=18, color=NAVY))
fig3.write_html(f"{OUT}/03_revenue_treemap_country_region.html")

# ============================================================================
# CHART 4: Customer Segment x Sales Channel -- Sunburst
# ============================================================================
seg_channel = orders.groupby(["segment", "sales_channel"])["revenue"].sum().reset_index()
fig4 = px.sunburst(
    seg_channel, path=["segment", "sales_channel"], values="revenue",
    title="Revenue: Customer Segment -> Sales Channel",
    color_discrete_sequence=BRAND_SEQ, template=TEMPLATE,
)
fig4.update_layout(title_font=dict(size=18, color=NAVY))
fig4.write_html(f"{OUT}/04_segment_channel_sunburst.html")

# ============================================================================
# CHART 5: Profit Margin vs Revenue -- Scatter (bubble = quantity), by category
# ============================================================================
prod_summary = orders.groupby(["product_name", "category_name"]).agg(
    revenue=("revenue", "sum"), profit_margin_pct=("profit_margin_pct", "mean"),
    quantity=("quantity", "sum")
).reset_index()
fig5 = px.scatter(
    prod_summary, x="revenue", y="profit_margin_pct", size="quantity", color="category_name",
    hover_name="product_name",
    title="Product Performance: Revenue vs Profit Margin (bubble size = units sold)",
    labels={"revenue": "Revenue (USD)", "profit_margin_pct": "Profit Margin %"},
    color_discrete_sequence=BRAND_SEQ, template=TEMPLATE,
)
fig5.update_layout(title_font=dict(size=18, color=NAVY))
fig5.write_html(f"{OUT}/05_product_revenue_vs_margin.html")

# ============================================================================
# CHART 6: Target Achievement Heatmap (region x month)
# ============================================================================
ta = target_achievement.merge(regions[["region_id", "region_name"]], on="region_id")
pivot = ta.pivot_table(index="region_name", columns="ym", values="target_achievement_pct", aggfunc="mean")
fig6 = go.Figure(data=go.Heatmap(
    z=pivot.values, x=pivot.columns, y=pivot.index,
    colorscale=[[0, RED], [0.5, "#FFEB84"], [1, GREEN]], zmid=100,
    colorbar=dict(title="Achievement %"),
))
fig6.update_layout(
    title="Target Achievement % Heatmap (Region x Month)",
    title_font=dict(size=18, color=NAVY), template=TEMPLATE,
    height=700,
)
fig6.write_html(f"{OUT}/06_target_achievement_heatmap.html")

# ============================================================================
# CHART 7: Return Rate by Category (interactive bar with hover detail)
# ============================================================================
returns_merged = returns.merge(orders[["order_id", "category_name"]], on="order_id", how="left")
return_counts = returns_merged.groupby("category_name").size().reset_index(name="return_count")
order_counts = orders.groupby("category_name").size().reset_index(name="order_count")
return_rate = return_counts.merge(order_counts, on="category_name")
return_rate["return_rate_pct"] = (return_rate["return_count"] / return_rate["order_count"] * 100).round(2)
return_rate = return_rate.sort_values("return_rate_pct", ascending=False)
fig7 = px.bar(
    return_rate, x="category_name", y="return_rate_pct",
    title="Return Rate % by Category",
    labels={"category_name": "Category", "return_rate_pct": "Return Rate %"},
    color="return_rate_pct", color_continuous_scale=["#DCE6F1", RED],
    template=TEMPLATE,
)
fig7.update_layout(title_font=dict(size=18, color=NAVY))
fig7.write_html(f"{OUT}/07_return_rate_by_category.html")

# ============================================================================
# CHART 8: Customer Lifetime Value Distribution (interactive histogram)
# ============================================================================
clv = orders.groupby("customer_id")["revenue"].sum().reset_index(name="lifetime_value")
fig8 = px.histogram(
    clv, x="lifetime_value", nbins=50,
    title="Customer Lifetime Value Distribution",
    labels={"lifetime_value": "Lifetime Value (USD)"},
    color_discrete_sequence=[BLUE], template=TEMPLATE,
)
fig8.add_vline(x=clv["lifetime_value"].mean(), line_dash="dash", line_color=RED,
                annotation_text=f"Mean = ${clv['lifetime_value'].mean():,.0f}")
fig8.update_layout(title_font=dict(size=18, color=NAVY))
fig8.write_html(f"{OUT}/08_customer_ltv_distribution.html")

print(f"Saved 8 interactive Plotly charts to {OUT}/")
print("(Run this script locally with `pip install plotly` to generate the HTML files --")
print(" this sandbox has no internet access to install the plotly package.)")
