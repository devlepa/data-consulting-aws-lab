import pandas as pd
import numpy as np
import os
from datetime import timedelta

np.random.seed(42)

# ============================================
# Load existing domains (for linking)
# ============================================

# Ecommerce products & orders
try:
    products = pd.read_csv("../../data/raw/ecommerce/products.csv")
    print(f"Loaded {len(products)} products.")
except:
    products = pd.DataFrame({"product_id": np.arange(1, 301)})
    print("WARNING: Using synthetic products.")

try:
    orders = pd.read_csv("../../data/raw/ecommerce/orders.csv")
    orders["order_date"] = pd.to_datetime(orders["order_date"])
    print(f"Loaded {len(orders)} orders.")
except:
    orders = pd.DataFrame(columns=["order_id", "customer_id", "order_date", "net_amount"])
    print("WARNING: No ecommerce orders found.")

# ============================================
# 1. Sessions
# ============================================

num_sessions = 20000

session_ids = np.arange(1, num_sessions + 1)
dates = pd.date_range("2023-01-01", "2023-06-30", freq="D")

traffic_sources = ["organic", "paid_search", "paid_social", "email", "direct", "referral"]
devices = ["mobile", "desktop", "tablet"]

countries = ["USA", "Colombia", "Mexico", "Brazil", "Spain"]
landing_pages = [
    "/home",
    "/products",
    "/products/category",
    "/cart",
    "/checkout",
    "/blog",
    "/contact"
]

sessions = pd.DataFrame({
    "session_id": session_ids,
    "user_id": np.random.randint(1, 5000, num_sessions),
    "visit_date": np.random.choice(dates, num_sessions),
    "device": np.random.choice(devices, num_sessions),
    "country": np.random.choice(countries, num_sessions),
    "traffic_source": np.random.choice(traffic_sources, num_sessions),
    "landing_page": np.random.choice(landing_pages, num_sessions),
    "session_duration": np.random.randint(5, 900, num_sessions),  # seconds
    "pages_viewed": np.random.randint(1, 12, num_sessions),
})

sessions["engaged_session"] = (sessions["session_duration"] > 45).astype(int)


# ============================================
# 2. Pageviews
# ============================================

page_urls = [
    "/home",
    "/products",
    "/products/category",
    "/product/",
    "/cart",
    "/checkout",
    "/thank-you",
    "/blog",
    "/contact"
]

pageview_rows = []
pageview_id = 1

for _, row in sessions.iterrows():
    num_pages = row["pages_viewed"]
    ts = pd.Timestamp(row["visit_date"])

    for i in range(num_pages):
        page = np.random.choice(page_urls)

        # Random product page
        if page == "/product/":
            product_id = np.random.choice(products["product_id"])
            page = f"/product/{product_id}"

        pageview_rows.append({
            "pageview_id": pageview_id,
            "session_id": row["session_id"],
            "page_url": page,
            "timestamp": ts + timedelta(seconds=np.random.randint(0, row["session_duration"])),
            "scroll_depth": np.random.randint(20, 100),
            "time_on_page": np.random.randint(1, 120)
        })
        pageview_id += 1

pageviews = pd.DataFrame(pageview_rows)


# ============================================
# 3. Events
# ============================================

event_names = ["view_product", "add_to_cart", "remove_from_cart", "purchase", "click_ad", "search"]

event_rows = []
event_id = 1

for _, pv in pageviews.iterrows():
    # Probability of 1–3 events per page
    num_events = np.random.choice([0, 1, 2, 3], p=[0.4, 0.3, 0.2, 0.1])

    for _ in range(num_events):
        event = np.random.choice(event_names)
        product_id = None

        if event in ["view_product", "add_to_cart", "purchase"]:
            # extract from URL if applicable
            if "/product/" in pv["page_url"]:
                product_id = int(pv["page_url"].split("/")[-1])
            else:
                product_id = np.random.choice(products["product_id"])

        event_rows.append({
            "event_id": event_id,
            "session_id": pv["session_id"],
            "event_name": event,
            "event_timestamp": pv["timestamp"] + timedelta(seconds=np.random.randint(1, 30)),
            "product_id": product_id,
            "value": np.random.uniform(0, 100)
        })
        event_id += 1

events = pd.DataFrame(event_rows)


# ============================================
# 4. Conversions (mapping orders to sessions)
# ============================================

conversion_rows = []
conversion_id = 1

if not orders.empty:
    # match each order to a random session from the same week
    for _, order in orders.iterrows():
        order_date = pd.Timestamp(order["order_date"])
        week_sessions = sessions[
            (sessions["visit_date"] >= order_date - timedelta(days=3)) &
            (sessions["visit_date"] <= order_date + timedelta(days=3))
        ]

        if len(week_sessions) == 0:
            continue

        session_choice = week_sessions.sample(1).iloc[0]

        conversion_rows.append({
            "conversion_id": conversion_id,
            "session_id": session_choice["session_id"],
            "order_id": order["order_id"],
            "conversion_timestamp": order_date,
            "revenue": order.get("net_amount", np.nan),
            "conversion_type": "purchase"
        })

        conversion_id += 1

web_conversions = pd.DataFrame(conversion_rows)


# ============================================
# SAVE ALL FILES
# ============================================

path = "../../data/raw/web/"
os.makedirs(path, exist_ok=True)

sessions.to_csv(path + "sessions.csv", index=False)
pageviews.to_csv(path + "pageviews.csv", index=False)
events.to_csv(path + "events.csv", index=False)
web_conversions.to_csv(path + "web_conversions.csv", index=False)

print("Full Web Analytics domain generated successfully.")
