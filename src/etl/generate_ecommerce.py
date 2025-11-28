import pandas as pd
import numpy as np
import os

np.random.seed(42)

# ============================================
# 0. Load existing domains (Finance & Marketing)
# ============================================

finance_orders = None
marketing_leads = None

# ---- Finance orders (for order_id / customer_id / date / status)
try:
    finance_orders = pd.read_csv("../../data/raw/finance/orders.csv")
    print(f"Loaded {len(finance_orders)} finance orders.")
except FileNotFoundError:
    print("WARNING: finance/orders.csv not found. Generating synthetic orders.")
    finance_orders = pd.DataFrame({
        "order_id": np.arange(1, 3001),
        "customer_id": np.random.randint(1, 1501, 3000),
        "order_date": pd.date_range("2023-01-01", periods=3000, freq="H"),
        "order_amount": np.round(np.random.uniform(20, 1500, 3000), 2),
        "status": np.random.choice(["completed", "pending", "canceled"], 3000)
    })

# ---- Marketing leads (for additional customer_ids / order_ids)
try:
    marketing_leads = pd.read_csv("../../data/raw/marketing/leads.csv")
    print(f"Loaded {len(marketing_leads)} marketing leads.")
except FileNotFoundError:
    print("WARNING: marketing/leads.csv not found. Customers will be purely synthetic.")
    marketing_leads = None

# ============================================
# 1. Products catalog
# ============================================

num_products = 500
product_ids = np.arange(1, num_products + 1)

categories = ["Electronics", "Home", "Fashion", "Beauty", "Sports", "Books"]
subcategories = {
    "Electronics": ["Phones", "Laptops", "Audio", "Accessories"],
    "Home": ["Kitchen", "Furniture", "Decor", "Cleaning"],
    "Fashion": ["Men", "Women", "Shoes", "Accessories"],
    "Beauty": ["Skincare", "Makeup", "Haircare", "Fragrance"],
    "Sports": ["Gym", "Outdoor", "Team Sports", "Accessories"],
    "Books": ["Fiction", "Non-Fiction", "Education", "Comics"]
}
brands = ["FormuBrand", "DataTech", "InsightPro", "CloudGear", "NeoLife", "UrbanFit"]

product_rows = []
for pid in product_ids:
    cat = np.random.choice(categories)
    subcat = np.random.choice(subcategories[cat])
    base_cost = np.random.uniform(5, 200)
    margin_factor = np.random.uniform(1.2, 2.5)  # between 20% and 150% margin
    price = base_cost * margin_factor

    product_rows.append({
        "product_id": pid,
        "sku": f"SKU-{pid:05d}",
        "product_name": f"{cat} {subcat} Item {pid}",
        "category": cat,
        "subcategory": subcat,
        "brand": np.random.choice(brands),
        "base_cost": round(base_cost, 2),
        "list_price": round(price, 2),
        "margin_pct": round((price - base_cost) / price * 100, 2),
        "active_from": "2023-01-01",
        "active_to": None
    })

products = pd.DataFrame(product_rows)


# ============================================
# 2. Customers
# ============================================

# Collect customer_ids from finance and marketing
customer_ids_finance = set(finance_orders["customer_id"].dropna().astype(int).tolist())

if marketing_leads is not None and "customer_id" in marketing_leads.columns:
    customer_ids_marketing = set(
        marketing_leads["customer_id"]
        .dropna()
        .astype(int)
        .tolist()
    )
else:
    customer_ids_marketing = set()

all_customer_ids = sorted(customer_ids_finance.union(customer_ids_marketing))

if len(all_customer_ids) == 0:
    # fallback synthetic customers
    all_customer_ids = list(range(1, 1501))

num_customers = len(all_customer_ids)
print(f"Total unique customers: {num_customers}")

first_names = ["Alex", "Chris", "Sam", "Taylor", "Jordan", "Pat", "Morgan", "Jamie"]
last_names = ["Smith", "Johnson", "Garcia", "Martinez", "Brown", "Lopez", "Davis", "Miller"]
countries = ["Colombia", "Mexico", "USA", "Brazil", "Spain"]
cities = {
    "Colombia": ["Bogotá", "Medellín", "Cali", "Barranquilla"],
    "Mexico": ["CDMX", "Guadalajara", "Monterrey"],
    "USA": ["New York", "Miami", "Los Angeles"],
    "Brazil": ["São Paulo", "Rio de Janeiro", "Brasilia"],
    "Spain": ["Madrid", "Barcelona", "Valencia"],
}

customer_rows = []
for cid in all_customer_ids:
    country = np.random.choice(countries)
    city = np.random.choice(cities[country])
    first = np.random.choice(first_names)
    last = np.random.choice(last_names)
    signup_date = pd.Timestamp("2022-01-01") + pd.to_timedelta(
        np.random.randint(0, 730), unit="D"
    )  # within 2 years
    gender = np.random.choice(["Male", "Female", "Other"])
    age_group = np.random.choice(["18-24", "25-34", "35-44", "45-54", "55+"])
    segment = np.random.choice(["New", "Active", "Churn Risk", "VIP"])

    customer_rows.append({
        "customer_id": cid,
        "first_name": first,
        "last_name": last,
        "full_name": f"{first} {last}",
        "email": f"customer_{cid}@example.com",
        "signup_date": signup_date.date(),
        "country": country,
        "city": city,
        "gender": gender,
        "age_group": age_group,
        "segment": segment
    })

customers = pd.DataFrame(customer_rows)


# ============================================
# 3. E-commerce Orders (header)
# ============================================

ecom_orders = finance_orders.copy()

# Add e-commerce specific fields
channels = ["web", "mobile_app", "marketplace"]
payment_methods = ["credit_card", "debit_card", "cash_on_delivery", "paypal", "bank_transfer"]
shipping_methods = ["standard", "express", "pickup_point"]

ecom_orders["sales_channel"] = np.random.choice(channels, len(ecom_orders))
ecom_orders["payment_method"] = np.random.choice(payment_methods, len(ecom_orders))
ecom_orders["shipping_method"] = np.random.choice(shipping_methods, len(ecom_orders))
ecom_orders["shipping_cost"] = np.round(np.random.uniform(0, 25, len(ecom_orders)), 2)
ecom_orders["discount_amount"] = np.round(np.random.uniform(0, 50, len(ecom_orders)), 2)
ecom_orders["currency"] = "USD"
ecom_orders.rename(columns={"order_amount": "financial_order_amount"}, inplace=True)

# Placeholder for amounts that we’ll calculate from order_items
ecom_orders["items_gross_amount"] = 0.0
ecom_orders["net_amount"] = 0.0


# ============================================
# 4. Order Items (lines)
# ============================================

order_item_rows = []
order_item_id_counter = 1

for idx, order in ecom_orders.iterrows():
    if order["status"] == "canceled":
        # canceled orders: no items
        continue

    num_items = np.random.randint(1, 6)  # 1 to 5 items per order
    chosen_products = np.random.choice(product_ids, num_items, replace=True)

    line_totals = []
    for pid in chosen_products:
        quantity = np.random.randint(1, 5)
        product_data = products.loc[products["product_id"] == pid].iloc[0]
        unit_price = product_data["list_price"] * np.random.uniform(0.9, 1.05)
        unit_cost = product_data["base_cost"]

        line_revenue = unit_price * quantity
        line_cost = unit_cost * quantity

        order_item_rows.append({
            "order_item_id": order_item_id_counter,
            "order_id": order["order_id"],
            "product_id": pid,
            "quantity": quantity,
            "unit_price": round(unit_price, 2),
            "unit_cost": round(unit_cost, 2),
            "line_revenue": round(line_revenue, 2),
            "line_cost": round(line_cost, 2),
            "line_margin": round(line_revenue - line_cost, 2)
        })

        order_item_id_counter += 1
        line_totals.append(line_revenue)

    items_total = float(np.sum(line_totals))
    ecom_orders.at[idx, "items_gross_amount"] = round(items_total, 2)

    net_amount = items_total + order["shipping_cost"] - order["discount_amount"]
    ecom_orders.at[idx, "net_amount"] = round(net_amount, 2)


order_items = pd.DataFrame(order_item_rows)

# ============================================
# 5. Returns
# ============================================

return_rows = []
return_id_counter = 1

# We’ll assume ~10% of completed orders have at least one returned item
completed_orders = ecom_orders[ecom_orders["status"] == "completed"]["order_id"].values
returned_orders = np.random.choice(completed_orders,
                                   size=int(len(completed_orders) * 0.1),
                                   replace=False)

for oid in returned_orders:
    related_items = order_items[order_items["order_id"] == oid]
    if related_items.empty:
        continue

    # 1 to 2 lines returned from this order
    num_return_lines = np.random.randint(1, min(3, len(related_items) + 1))
    returned_lines = related_items.sample(num_return_lines)

    for _, line in returned_lines.iterrows():
        qty_returned = np.random.randint(1, line["quantity"] + 1)
        refund_amount = (line["unit_price"] * qty_returned) * np.random.uniform(0.8, 1.0)
        restocking_fee = np.random.uniform(0, 10)

        return_rows.append({
            "return_id": return_id_counter,
            "order_id": oid,
            "order_item_id": line["order_item_id"],
            "product_id": line["product_id"],
            "customer_id": int(
                ecom_orders.loc[ecom_orders["order_id"] == oid, "customer_id"].iloc[0]
            ),
            "return_date": pd.Timestamp(
                ecom_orders.loc[ecom_orders["order_id"] == oid, "order_date"].iloc[0]
            ) + pd.to_timedelta(np.random.randint(1, 30), unit="D"),
            "reason": np.random.choice(
                ["Damaged", "Wrong size", "Not as described", "Changed mind"]
            ),
            "qty_returned": qty_returned,
            "refund_amount": round(refund_amount, 2),
            "restocking_fee": round(restocking_fee, 2)
        })

        return_id_counter += 1

returns = pd.DataFrame(return_rows)


# ============================================
# 6. SAVE ALL DATA
# ============================================

path = "../../data/raw/ecommerce/"
os.makedirs(path, exist_ok=True)

products.to_csv(path + "products.csv", index=False)
customers.to_csv(path + "customers.csv", index=False)
ecom_orders.to_csv(path + "orders.csv", index=False)
order_items.to_csv(path + "order_items.csv", index=False)
returns.to_csv(path + "returns.csv", index=False)

print("Full ecommerce domain generated successfully.")
