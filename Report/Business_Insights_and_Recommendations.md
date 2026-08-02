# Business Insights & Executive Recommendations
## Business Performance 360° Dashboard — GlobalMart Retail Inc.

Every insight below is computed directly from the cleaned, feature-engineered
dataset (Python Phase 5) — none are generic or illustrative. Figures reference
the full 101,800-order dataset unless noted otherwise. Where a number has a
known caveat (e.g. the repeat-customer rate, or the incomplete reporting
window), that caveat is stated plainly rather than smoothed over.

---

## Part 1 — Business Insights (27 statements, covering 29 data-driven findings)

### Revenue & Growth
1. **Total revenue reached $112.6M** at a 47.2% blended profit margin ($53.1M profit).
2. **Comparing like-for-like Jan–Jul periods, revenue grew 74.5% year-over-year**
   (2025 vs. 2024) — the fairest growth read given this dataset's reporting window.
3. **Q3 is the strongest quarter historically**, generating $32.2M, with month 7
   (July) the single strongest month at $11.3M across all years.
4. *(Data transparency)* Order volume tapers in the final months before the
   2025-12-29 collection cutoff — a sampling artifact, not a genuine business
   decline. Trend KPIs use data through 2025-07 for this reason.

### Category & Product Performance
5. **Apparel is the top revenue category** at $16.4M (14.5% of total).
6. **Furniture carries the highest profit margin** at 47.2% — the most
   profitable category per dollar sold, despite not leading on raw revenue.
7. **Electronics is the lowest revenue category** at $12.2M — a candidate for
   review or a targeted promotion.
8. **The Hardgoods department leads overall**, at $56.2M (49.9% of total revenue).
9. **'TV Stand Plus' is the single best-selling product** by revenue at $818K.
10. **The bottom 10 products collectively generated just $125K** — under 0.5%
    of total revenue — a concrete delisting shortlist.
11. **Stratus is the top-performing brand** by revenue at $9.3M.

### Regional Performance
12. **USA – Texas is the top-performing region** by revenue at $4.3M; Texas is
    also the top state/province by total profit at $2.0M.
13. **USA is the top country by revenue** at $31.1M (27.6% of total).
14. **459 of 1,080 region-month combinations (42.5%) missed their revenue
    target** — a substantial minority worth a structured regional review, even
    while the company average sits above target overall.

### Customer Behavior
15. **The Consumer segment drives the most revenue**, $62.6M (55.6% of total).
16. **The top 10% of customers by spend account for 19.7% of total revenue** —
    a concentration worth protecting with loyalty/retention programs.
17. *(Data caveat)* 100% of customers show more than one order in this dataset
    — a statistical artifact of the order-to-customer ratio (~12.7 orders per
    customer), not a validated retention metric. Flagged for transparency.

### Sales Channel & Rep Performance
18. **Online is the leading sales channel**, generating $51.0M (45.2% of revenue)
    and the highest average order value ($1,110.41) — suggesting higher-intent
    or bulk purchases through that channel.
19. **Patricia Jones is the top-performing sales rep**, generating $4.5M.
20. **21 of 58 sales reps (36.2%) perform above the company average** of
    $1.94M per rep — useful for identifying coaching opportunities among the
    remaining 64%.

### Profitability
21. **Discounted orders average 41.1% margin vs. 48.2% for full-price orders**
    — a 7.1-point margin cost from discounting that should inform promotional
    strategy.
22. **5.6% of all orders carry a profit margin below 20%** — a meaningful
    share of low-profitability transactions worth root-causing.

### Returns & Quality
23. **Returns cost $5.81M in refunds — 5.16% of total revenue** — a direct,
    quantifiable profit leakage point.
24. **'Not as Described' is the leading return reason** (970 of 6,120 returns,
    15.8%) — typically a listing/photography fix, not a product-quality fix.
25. **Sports & Outdoors has the highest category return rate**, 6.3% —
    warranting a fit/sizing or quality review specific to that category.

### Operations
26. **28.6% of orders take more than 5 days to ship** — a logistics pattern
    worth investigating by region and channel.

### Data Quality (transparency, as a real analyst would report)
27. **After cleaning, the dataset retains 101,800 valid order records** from
    103,530 raw records — duplicates, negative quantities, outliers, missing
    values, and inconsistent labels were identified and resolved across the
    SQL, Excel, and Python layers of this project, each independently.

---

## Part 2 — Executive Recommendations (15)

Each recommendation is tied to the specific insight(s) that motivate it, with
a priority and expected impact so leadership can sequence action.

| # | Recommendation | Tied to Insight(s) | Priority | Expected Impact |
|---|---|---|---|---|
| 1 | Launch a root-cause review of the 42.5% of region-months missing target — start with the lowest-achievement regions identified on the Regional Analysis page. | #14 | **High** | Directly recovers lost revenue in underperforming regions |
| 2 | Fix product listings/photography for high-return SKUs before assuming a quality problem — 'Not as Described' is the #1 return reason company-wide. | #24, #23 | **High** | Lower-cost fix than quality remediation; reduces the $5.81M refund line |
| 3 | Commission a fit/sizing and quality audit specifically for Sports & Outdoors, the highest-return category. | #25 | **High** | Targets the single highest return-rate category directly |
| 4 | Build a formal loyalty/retention program for the top 10% of customers by spend, who already generate ~20% of revenue. | #16 | **High** | Protects a concentrated, high-value revenue base |
| 5 | Re-evaluate discount depth and targeting — discounted orders run a 7.1-point lower margin than full-price orders. | #21 | **High** | Improves blended margin without necessarily cutting volume |
| 6 | Review the bottom 10 products for delisting or repositioning; they collectively contribute under 0.5% of revenue. | #10 | **Medium** | Frees shelf/catalog space and operational overhead for higher-yield SKUs |
| 7 | Investigate the logistics/fulfillment pattern behind the 28.6% of orders shipping in more than 5 days, broken out by region and channel. | #26 | **Medium** | Improves customer experience and may reduce returns tied to slow delivery |
| 8 | Double down on Furniture's margin advantage — consider a merchandising push, since it's the most profitable category per dollar despite not leading on raw revenue. | #6 | **Medium** | Improves overall blended margin by shifting mix toward high-margin categories |
| 9 | Investigate Electronics' underperformance (lowest-revenue category) — pricing, assortment, or competitive positioning review. | #7 | **Medium** | Potential to lift a clearly underperforming category |
| 10 | Formalize a sales rep coaching program pairing the 64% of reps below company average with top performers like Patricia Jones. | #19, #20 | **Medium** | Structured path to lift the majority of the sales team toward top-quartile performance |
| 11 | Investigate the 5.6% of orders with sub-20% margin for a common root cause (specific products, regions, or discount tiers). | #22 | **Medium** | Identifies and closes a specific margin leak |
| 12 | Invest further in the Online channel's growth, given it already leads both revenue share and average order value. | #18 | **Medium** | Compounds strength in the highest-performing, highest-AOV channel |
| 13 | Build a repeat-purchase/retention metric using order recency and frequency (not just order count) before using "repeat rate" in strategic decisions — the current 100% figure is a known dataset artifact. | #17 | **Medium** | Prevents a strategic decision being made on a misleading metric |
| 14 | Use Q3/July seasonal strength to plan inventory and staffing ahead of the peak window each year. | #3 | **Low** | Operational efficiency gain, lower urgency than margin/return items |
| 15 | Replicate whatever is driving Texas's regional leadership (both revenue and profit) in other underperforming regions as a playbook. | #12, #14 | **Low** | Longer-term structural upside, dependent on further root-cause analysis |

---

## Methodology Note

Insights and recommendations were generated programmatically from the cleaned
dataset (`Python/06_kpi_insights_export.py`) to ensure every figure is
traceable to source data rather than hand-written. Recommendations were then
authored by mapping each insight to a concrete, actionable next step and
assigning priority based on (a) direct revenue/profit impact and (b) how
concentrated/specific the underlying finding is (e.g., a single category or
region vs. a broad, diffuse pattern).
