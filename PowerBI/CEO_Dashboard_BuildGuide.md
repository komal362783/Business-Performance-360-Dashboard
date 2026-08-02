# CEO Dashboard — Power BI Build Guide
## Business Performance 360° Dashboard | GlobalMart Retail Inc.

This guide is written so you can rebuild the full dashboard in Power BI Desktop
from scratch, page by page. It assumes the star-schema tables from
`Dataset/powerbi_ready/` are already imported (see **Data Model Setup** below)
and the DAX measures from `PowerBI/DAX/measures.dax` are already created.

---

## 1. Data Model Setup

1. **Get Data > Text/CSV**, import all 8 files from `Dataset/powerbi_ready/`:
   `fact_orders`, `dim_customers`, `dim_products`, `dim_categories`, `dim_regions`,
   `dim_sales_reps`, `fact_returns`, `fact_target_achievement`.
2. **Create a dedicated date table** (Modeling > New Table):
   ```
   dim_date = CALENDAR ( DATE(2023,1,1), DATE(2025,12,31) )
   ```
   Add columns: `Year = YEAR(dim_date[date])`, `Month = FORMAT(dim_date[date],"MMM")`,
   `MonthNum = MONTH(dim_date[date])`, `Quarter = "Q" & QUARTER(dim_date[date])`,
   `YearMonth = FORMAT(dim_date[date],"YYYY-MM")`.
   Mark it as the official **Date Table** (Table tools > Mark as Date Table).
3. **Build relationships** (Model view) exactly as documented at the top of
   `measures.dax`: all single-direction, many-side on the fact tables.
   Drag `fact_orders[order_date]` -> `dim_date[date]` last, after confirming the
   other joins resolve cleanly.
4. **Hide foreign keys** on the fact tables from Report view (right-click each
   `_id` column > Hide in report view) -- keep only the friendly dimension
   columns and measures visible to report builders.
5. Paste all measures from `measures.dax` into a dedicated **_Measures** table
   (Modeling > New Table > `_Measures = ROW("x",0)`, then delete the dummy
   column) so they're easy to find in the field list.

---

## 2. Global Design System

Applied consistently across all 8 pages for a cohesive executive look:

| Element | Spec |
|---|---|
| Primary color | Navy `#1F3864` (headers, primary bars) |
| Secondary color | Gold `#C9A961` (highlights, secondary series) |
| Positive | Green `#2E7D32` |
| Negative | Red `#C62828` |
| Neutral/text | Grey `#595959` |
| Background | White `#FFFFFF` / light grey `#F7F7F7` panels |
| Font | Segoe UI (Power BI default) -- Bold for titles, Regular for body |
| Card corner radius | 4px, subtle drop shadow |
| Page canvas | 1280x720 (16:9), consistent across all pages |

**Theme JSON**: create a custom theme (View > Themes > Browse for themes) using
these hex values so every new visual inherits the palette automatically.

---

## 3. Navigation Shell (build once, applied to every page)

1. Add a **left navigation rail** (~120px wide) as a rectangle shape, Navy fill,
   spanning the full page height.
2. Add **8 navigation buttons** (Insert > Buttons > Blank) stacked vertically in
   the rail, one per page: Executive Overview, Sales Analysis, Customer Analysis,
   Product Analysis, Regional Analysis, Profit Analysis, Returns Dashboard,
   Forecast Dashboard.
3. For each button: **Action = Page navigation**, target = the corresponding page.
   Icon + label, white text, hover state slightly lighter navy fill.
4. Copy this navigation rail (Ctrl+C) onto every page (Ctrl+V) -- or better,
   build it once and use **Format Painter** / Power BI's **Sync visuals**
   (Selection pane > group as "NavRail", copy-paste group across pages) so it's
   identical everywhere.
5. Highlight the active page's button (manually set a slightly different fill
   per page, or use a bookmark-driven state if you want it dynamic).

---

## 4. PAGE 1 — Executive Overview

**Purpose**: the CEO's 10-second read of the business. Everything else drills from here.

**Layout** (top to bottom):
- **Header band** (full width, Navy): dynamic title text box bound to
  `[Dynamic Title - Executive Overview]`, plus current date/refresh timestamp.
- **KPI card row** (6 cards): Total Revenue, Total Profit, Profit Margin %,
  Total Orders, Average Order Value, Target Achievement %. Use Card visuals
  with a small trend sparkline underneath each (Power BI's "KPI" visual
  supports this natively for a couple of these).
- **Monthly Revenue Trend** (line chart, left 2/3 width): `dim_date[YearMonth]`
  on axis, `[Total Revenue]` as value. Add a reference line at the average.
  **Apply a filter** excluding the incomplete reporting window (see note in
  `measures.dax` Section 4) or add a visual-level note.
- **Revenue by Category** (donut, right 1/3 width): `dim_categories[category_name]`
  legend, `[Total Revenue]` values.
- **Regional Performance mini-map or bar** (bottom left): Top 5 regions by
  `[Total Revenue]`, horizontal bar.
- **Target Achievement gauge** (bottom right): `[Target Achievement %]`,
  min 0%, max 150%, target line at 100%.

**Slicers** (slicer panel, top of page, applies to whole page via sync):
Year, Quarter, Country, Sales Channel.

**Tooltips**: enable report-page tooltips -- build a small tooltip page showing
Revenue/Profit/Orders for whatever category or region is hovered.

**Drill-through**: right-click any category in the donut -> drills through to
**Page 4 (Product Analysis)** filtered to that category.

---

## 5. PAGE 2 — Sales Analysis

**Purpose**: how, where, and through which channel sales happen.

**Visuals**:
- **KPI cards**: Total Orders, Average Order Value, MoM Growth %, Total Units Sold.
- **Revenue by Sales Channel** (stacked column, by month): `dim_date[YearMonth]`
  axis, `sales_channel` legend, `[Total Revenue]` values -- shows channel mix
  shifting over time.
- **Orders vs Revenue Scatter** (by day-of-week or by rep): identifies
  high-volume/low-value vs low-volume/high-value patterns.
- **Discount Impact** (clustered bar): Avg profit margin for discounted vs
  full-price orders, using `[Average Discount %]` and margin measures.
- **Sales Rep Leaderboard** (table, sortable): rep name, revenue, orders, rank
  via `[Rep Revenue Rank]`, conditional formatting (data bars) on revenue column.

**Slicers**: Sales Channel, Sales Rep, Date range slider.
**Bookmark**: "Top 10 Reps Only" bookmark that pre-filters the leaderboard table.
**Dynamic title**: channel-aware title using a pattern like
`Dynamic Title - Regional Selection` adapted to `sales_channel`.

---

## 6. PAGE 3 — Customer Analysis

**Purpose**: who buys, how often, and how much they're worth.

**Visuals**:
- **KPI cards**: Total Customers, Active Customers, Repeat Customer Rate %,
  Average Order Value.
- **Customer Segment Treemap**: `segment` by `[Total Revenue]`.
- **Customer Lifetime Value Distribution** (histogram, via a calculated bucket
  column on `dim_customers` or a grouped measure): shows concentration of
  high-value customers.
- **New vs Repeat Revenue** (100% stacked bar by month): split revenue between
  one-time and repeat customers over time.
- **Top 20 Customers** (table): name, segment, lifetime revenue, order count --
  conditional formatting icon set on order count.
- **Country/Segment Matrix**: matrix visual, rows = country, columns = segment,
  values = `[Total Revenue]`, conditional formatting heatmap.

**Slicers**: Segment, Country.
**Drill-through**: click any customer row -> drills to a customer detail
tooltip page (order history mini-table + KPIs filtered to that customer).

---

## 7. PAGE 4 — Product Analysis

**Purpose**: what's selling, what isn't, and what's profitable.

**Visuals**:
- **KPI cards**: Total Products Sold, Total Units Sold, Category Profit Margin %
  (for the currently filtered category).
- **Top 10 / Bottom 10 Products** (two side-by-side horizontal bar charts):
  `[Total Revenue]` by `product_name`, using `TOPN`/`Revenue Rank (Product)`
  filters.
- **Category Performance Matrix**: category x profit margin %, conditional
  color scale (red->green), sized by revenue.
- **Brand Performance** (bar chart): revenue by `brand`.
- **Price vs Margin Scatter**: `unit_price` (x) vs `Category Profit Margin %`
  (y), bubble size = units sold, color = category -- mirrors the Python Plotly
  scatter chart from Phase 5.

**Slicers**: Category, Brand, Department.
**Drill-through target**: this page receives drill-through from Page 1's
category donut and Page 7's returns-by-product chart.

---

## 8. PAGE 5 — Regional Analysis

**Purpose**: geographic performance and target tracking.

**Visuals**:
- **KPI cards**: Regions Below Target, Target Achievement % (overall),
  Total Revenue, Total Profit.
- **Filled Map**: `country`/`state` shaded by `[Total Revenue]` (Power BI's
  native Map or Azure Maps visual -- requires state/country name matching or
  lat/long columns; `dim_regions` already has both country and state text).
- **Region Performance Table**: region name, revenue, profit, target
  achievement %, with data bars and a red/green icon (`[Target Status]`).
- **Target Achievement Trend** (line, by month, one line per region or an
  average line with a band showing min/max region spread).

**Slicers**: Country, State, Region.
**Dynamic title**: `[Dynamic Title - Regional Selection]`.
**Bookmark**: "Underperforming Regions" -- pre-applies a filter of
`[Target Achievement %] < 100%` to the table.

---

## 9. PAGE 6 — Profit Analysis

**Purpose**: where the company actually makes money.

**Visuals**:
- **KPI cards**: Total Profit, Profit Margin %, Low Margin Order Rate %,
  Total Cost.
- **Profit Bridge / Waterfall**: Revenue -> Discounts -> COGS -> Returns -> Net
  Profit, using a Waterfall visual.
- **Profit Margin by Category** (bar, sorted descending): reuses
  `[Category Profit Margin %]`.
- **Profit Margin Distribution** (histogram): mirrors the Python matplotlib
  chart from Phase 5, showing the spread of order-level margins.
- **Discount vs Margin trend** (dual-axis line): average discount % and
  average margin % over time, showing the tradeoff.

**Slicers**: Category, Segment, Sales Channel.

---

## 10. PAGE 7 — Returns Dashboard

**Purpose**: quantify and diagnose the cost of returns.

**Visuals**:
- **KPI cards**: Return Rate %, Total Refunded, Refund % of Revenue, Total Returns.
- **Return Reason Breakdown** (horizontal bar): `return_reason` by count.
- **Return Rate by Category** (bar, conditional color: red if >6%): mirrors
  the Python EDA finding (Sports & Outdoors led at 6.3%).
- **Returns Trend** (line, by month): return count and refund amount over time.
- **Top Returned Products** (table): product name, return count, refund total --
  drill-through target from Page 4.

**Slicers**: Return Reason, Category, Date range.

---

## 11. PAGE 8 — Forecast Dashboard

**Purpose**: forward-looking view for planning conversations.

**Visuals**:
- **Revenue Forecast** (line chart with Power BI's built-in **Analytics pane
  > Forecast** feature): monthly revenue with a forecasted continuation and
  confidence interval band. **Important**: base this on the complete reporting
  window only (through 2025-07) so the forecast isn't skewed by the
  incomplete-window taper -- apply a visual-level filter
  `dim_date[YearMonth] <= "2025-07"` before enabling the forecast.
- **What-If Parameter card**: slider bound to `Forecast Growth Rate`
  parameter, feeding `[Forecasted Next Month Revenue]`.
- **Target vs Forecast** (combo chart): actual revenue, target revenue, and
  forecasted revenue on one timeline.
- **Scenario table**: forecasted revenue at 0%, 5%, 10%, 15% growth assumptions
  (a small disconnected table + measure that responds to the parameter).

**Slicers**: none required (whole-company forward view) -- optionally Region.

---

## 12. Bookmarks Summary

| Bookmark | Page | Effect |
|---|---|---|
| Default View | Executive Overview | Resets all slicers |
| Top 10 Reps Only | Sales Analysis | Filters rep leaderboard to top 10 |
| Underperforming Regions | Regional Analysis | Filters to <100% target achievement |
| High Return Categories | Returns Dashboard | Filters to categories >6% return rate |

Add a small **bookmark navigator** (Insert > Buttons, grouped) on each relevant
page so executives can jump to a pre-filtered "story" state with one click.

---

## 13. Mobile Layout

For each page, switch to **View > Mobile Layout** and rebuild a single-column
stack: KPI cards first (2 per row), then the single most important chart per
page, then a "View full report on desktop" text note. Power BI's mobile
layout is a separate canvas per page -- budget roughly 15-20 minutes per page
to arrange.

---

## 14. Publish Checklist

- [ ] All 8 pages built and navigation rail consistent
- [ ] All slicers tested (single-select where it makes sense, e.g. Year)
- [ ] Drill-throughs tested from every source visual
- [ ] Tooltips page built and applied
- [ ] Bookmarks tested and buttons wired
- [ ] Dynamic titles verified against filter changes
- [ ] Mobile layout built for at least the Executive Overview page
- [ ] Data refresh scheduled (if connected to a live source rather than static CSVs)
- [ ] Sensitivity: confirm no PII (raw customer emails) is exposed on any visual
