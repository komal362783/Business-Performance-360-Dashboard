"""
Business Performance 360 Dashboard - Dataset Generator
=========================================================
Generates a realistic, production-scale retail dataset for GlobalMart Retail Inc.
Produces BOTH a clean reference version and a deliberately "dirty" raw version
(missing values, duplicates, incorrect values, outliers) to simulate real-world data.

Author: Data Analytics Portfolio Project
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

# ------------------------------------------------------------------
# Reproducibility
# ------------------------------------------------------------------
np.random.seed(42)
random.seed(42)

OUT_RAW = "/home/claude/Business-Performance-360-Dashboard/Dataset/raw"
OUT_CLEAN = "/home/claude/Business-Performance-360-Dashboard/Dataset/cleaned"

N_ORDERS = 105000          # will drop some to duplicates/bad rows -> ~100K+ usable
N_CUSTOMERS = 8000
N_PRODUCTS = 500

# ------------------------------------------------------------------
# 1. CATEGORIES
# ------------------------------------------------------------------
categories_data = [
    (1, "Electronics", "Hardgoods"),
    (2, "Furniture", "Hardgoods"),
    (3, "Apparel", "Softlines"),
    (4, "Footwear", "Softlines"),
    (5, "Home & Kitchen", "Hardgoods"),
    (6, "Sports & Outdoors", "Hardgoods"),
    (7, "Beauty & Personal Care", "Softlines"),
    (8, "Groceries", "Consumables"),
]
categories = pd.DataFrame(categories_data, columns=["category_id", "category_name", "department"])

# ------------------------------------------------------------------
# 2. PRODUCTS
# ------------------------------------------------------------------
product_name_pool = {
    "Electronics": ["Wireless Headphones", "4K Smart TV", "Bluetooth Speaker", "Laptop Pro 14", "Smartphone X",
                    "Tablet Air", "Gaming Console", "Smartwatch Series", "Digital Camera", "Wireless Mouse",
                    "Mechanical Keyboard", "Portable Charger", "Home Router", "Noise Cancelling Earbuds", "Drone Mini"],
    "Furniture": ["Office Chair", "Standing Desk", "Bookshelf", "Sofa 3-Seater", "Dining Table",
                  "Bed Frame Queen", "Coffee Table", "Wardrobe", "Recliner Chair", "TV Stand"],
    "Apparel": ["Men's Jacket", "Women's Dress", "Cotton T-Shirt", "Denim Jeans", "Formal Shirt",
                "Winter Coat", "Yoga Pants", "Hooded Sweatshirt", "Summer Shorts", "Wool Sweater"],
    "Footwear": ["Running Shoes", "Leather Boots", "Casual Sneakers", "Formal Loafers", "Sandals",
                 "Hiking Shoes", "Sports Sandals", "High Heels", "Slip-On Shoes", "Basketball Shoes"],
    "Home & Kitchen": ["Air Fryer", "Coffee Maker", "Blender Pro", "Non-Stick Cookware Set", "Vacuum Cleaner",
                       "Microwave Oven", "Toaster", "Dinnerware Set", "Knife Set", "Electric Kettle"],
    "Sports & Outdoors": ["Yoga Mat", "Dumbbell Set", "Camping Tent", "Cycling Helmet", "Fitness Tracker",
                          "Football", "Tennis Racket", "Sleeping Bag", "Hiking Backpack", "Resistance Bands"],
    "Beauty & Personal Care": ["Face Moisturizer", "Shampoo & Conditioner", "Electric Toothbrush", "Perfume Set",
                               "Hair Dryer", "Makeup Kit", "Sunscreen SPF50", "Beard Trimmer", "Skincare Serum", "Body Lotion"],
    "Groceries": ["Organic Coffee Beans", "Extra Virgin Olive Oil", "Almond Butter", "Green Tea Pack",
                  "Protein Powder", "Granola Bars", "Pasta Pack", "Honey Jar", "Mixed Nuts", "Herbal Tea Set"],
}
brands = ["Zenova", "Urbanix", "NovaCraft", "PrimeLine", "EcoWell", "TrueForm", "Apex", "Nordic Home",
          "Vertex", "Luxora", "CoreTech", "Bright & Co", "Stratus", "Everline", "Kindred"]

products_rows = []
pid = 1
variants = ["", " Plus", " Lite", " Pro", " 2.0", " Max"]
n_categories = len(categories)
base_per_cat = N_PRODUCTS // n_categories
remainder = N_PRODUCTS % n_categories

for cat_idx, (_, cat) in enumerate(categories.iterrows()):
    names = product_name_pool[cat["category_name"]]
    # distribute products evenly across categories (give the last category the remainder)
    n_for_this_cat = base_per_cat + (remainder if cat_idx == n_categories - 1 else 0)

    # build enough (name, variant) combos to cover n_for_this_cat without early exhaustion
    combos = [(n, v) for v in variants for n in names]
    random.shuffle(combos)
    while len(combos) < n_for_this_cat:
        extra = [(n, v) for v in variants for n in names]
        random.shuffle(extra)
        combos += extra
    combos = combos[:n_for_this_cat]

    for base_name, variant in combos:
        unit_cost = round(np.random.uniform(5, 400), 2)
        markup = np.random.uniform(1.3, 2.8)
        unit_price = round(unit_cost * markup, 2)
        launch_date = datetime(2019, 1, 1) + timedelta(days=int(np.random.uniform(0, 2000)))
        products_rows.append([pid, cat["category_id"], base_name + variant, random.choice(brands),
                               unit_price, unit_cost, launch_date.date()])
        pid += 1

products = pd.DataFrame(products_rows, columns=["product_id", "category_id", "product_name", "brand",
                                                  "unit_price", "unit_cost", "launch_date"])
products["product_id"] = range(1, len(products) + 1)

# ------------------------------------------------------------------
# 3. REGIONS  (country -> states/regions)
# ------------------------------------------------------------------
region_map = {
    "USA": ["California", "Texas", "New York", "Florida", "Illinois", "Washington", "Georgia", "Ohio"],
    "UK": ["England", "Scotland", "Wales", "Northern Ireland"],
    "Canada": ["Ontario", "Quebec", "British Columbia", "Alberta"],
    "Australia": ["New South Wales", "Victoria", "Queensland", "Western Australia"],
    "Germany": ["Bavaria", "Berlin", "Hesse", "North Rhine-Westphalia"],
    "India": ["Maharashtra", "Karnataka", "Delhi", "Tamil Nadu", "Gujarat", "Uttar Pradesh"],
}
regions_rows = []
rid = 1
for country, states in region_map.items():
    for state in states:
        region_name = f"{country} - {state}"
        regions_rows.append([rid, country, state, region_name])
        rid += 1
regions = pd.DataFrame(regions_rows, columns=["region_id", "country", "state", "region_name"])

# ------------------------------------------------------------------
# 4. SALES REPS
# ------------------------------------------------------------------
first_names = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda", "David", "Barbara",
               "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen", "Daniel", "Nancy",
               "Priya", "Raj", "Amit", "Sunita", "Oliver", "Emma", "Liam", "Sophie", "Noah", "Chloe"]
last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
              "Wilson", "Anderson", "Taylor", "Thomas", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
              "Sharma", "Patel", "Kapoor", "Iyer", "Clarke", "Evans", "Hughes", "Bennett", "Murphy", "Cole"]

sales_reps_rows = []
for rep_id in range(1, 61):
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    region_id = random.choice(regions["region_id"].tolist())
    hire_date = datetime(2018, 1, 1) + timedelta(days=int(np.random.uniform(0, 2400)))
    sales_reps_rows.append([rep_id, name, region_id, hire_date.date()])
sales_reps = pd.DataFrame(sales_reps_rows, columns=["rep_id", "rep_name", "region_id", "hire_date"])

# ------------------------------------------------------------------
# 5. CUSTOMERS
# ------------------------------------------------------------------
segments = ["Consumer", "Corporate", "Small Business"]
segment_weights = [0.55, 0.25, 0.20]

customers_rows = []
for cust_id in range(1, N_CUSTOMERS + 1):
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    region = regions.sample(1, random_state=cust_id).iloc[0]
    email = f"{name.lower().replace(' ', '.')}{cust_id}@mail.com"
    segment = np.random.choice(segments, p=segment_weights)
    signup_date = datetime(2019, 1, 1) + timedelta(days=int(np.random.uniform(0, 2500)))
    customers_rows.append([cust_id, name, email, segment, region["country"], region["state"], signup_date.date()])

customers = pd.DataFrame(customers_rows, columns=["customer_id", "customer_name", "email", "segment",
                                                    "country", "state", "signup_date"])

# ------------------------------------------------------------------
# NOTE: Monthly_Targets are generated in 01_generate_orders_returns.py
# instead of here, because realistic targets need to be calibrated
# against actual regional revenue (so achievement % has a believable
# mix of over- and under-performing regions rather than random noise).
# ------------------------------------------------------------------

# Save clean dimension tables now (these don't need heavy dirtying, minor issues added to orders/customers instead)
categories.to_csv(f"{OUT_CLEAN}/categories.csv", index=False)
products.to_csv(f"{OUT_CLEAN}/products.csv", index=False)
regions.to_csv(f"{OUT_CLEAN}/regions.csv", index=False)
sales_reps.to_csv(f"{OUT_CLEAN}/sales_reps.csv", index=False)
customers.to_csv(f"{OUT_CLEAN}/customers_clean_reference.csv", index=False)

print("Dimension tables generated:")
print(f"  Categories: {len(categories)}")
print(f"  Products: {len(products)}")
print(f"  Regions: {len(regions)}")
print(f"  Sales_Reps: {len(sales_reps)}")
print(f"  Customers: {len(customers)}")
