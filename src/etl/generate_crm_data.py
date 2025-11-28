import pandas as pd
import numpy as np
import os

np.random.seed(42)

# ============================================
# 0. Load existing domains (ecommerce, marketing, finance)
# ============================================

ecom_customers = None
finance_orders = None
marketing_leads = None

# E-commerce customers (base list)
try:
    ecom_customers = pd.read_csv("../../data/raw/ecommerce/customers.csv")
    print(f"Loaded {len(ecom_customers)} ecommerce customers.")
except FileNotFoundError:
    print("WARNING: ecommerce/customers.csv not found. CRM will be synthetic.")
    ecom_customers = pd.DataFrame(columns=["customer_id"])

# Finance orders (for activity & last purchase date)
try:
    finance_orders = pd.read_csv("../../data/raw/finance/orders.csv")
    print(f"Loaded {len(finance_orders)} finance orders.")
except FileNotFoundError:
    print("WARNING: finance/orders.csv not found.")
    finance_orders = pd.DataFrame(columns=["order_id", "customer_id", "order_date", "status"])

# Marketing leads (for lifecycle info)
try:
    marketing_leads = pd.read_csv("../../data/raw/marketing/leads.csv")
    print(f"Loaded {len(marketing_leads)} marketing leads.")
except FileNotFoundError:
    print("WARNING: marketing/leads.csv not found.")
    marketing_leads = pd.DataFrame(columns=["lead_id", "customer_id", "funnel_stage"])
    

# ============================================
# 1. CRM Customers (enriched)
# ============================================

# Start from ecommerce customers IDs, fallback if empty
if "customer_id" in ecom_customers.columns and len(ecom_customers) > 0:
    customer_ids = ecom_customers["customer_id"].astype(int).unique()
else:
    customer_ids = np.arange(1, 1501)

crm_customers = pd.DataFrame({"customer_id": customer_ids})

# Basic demographic / segmentation enrichment (if not already present)
segments = ["New", "Active", "Loyal", "At Risk", "Churned"]
lifecycle_stages = ["Lead", "MQL", "Customer", "Active", "Churned"]
preferred_channels = ["email", "phone", "whatsapp", "sms", "in_app"]

crm_customers["lifecycle_stage"] = np.random.choice(lifecycle_stages, len(crm_customers))
crm_customers["segment"] = np.random.choice(segments, len(crm_customers))
crm_customers["nps_score"] = np.random.randint(0, 11, len(crm_customers))  # 0–10
crm_customers["preferred_channel"] = np.random.choice(preferred_channels, len(crm_customers))
crm_customers["consent_marketing"] = np.random.choice([0, 1], len(crm_customers), p=[0.2, 0.8])

# Last order date & total orders from finance
if not finance_orders.empty:
    finance_orders["order_date"] = pd.to_datetime(finance_orders["order_date"])
    agg_orders = (
        finance_orders.groupby("customer_id")
        .agg(
            last_order_date=("order_date", "max"),
            total_orders=("order_id", "count")
        )
        .reset_index()
    )
    crm_customers = crm_customers.merge(
        agg_orders, on="customer_id", how="left"
    )
else:
    crm_customers["last_order_date"] = pd.NaT
    crm_customers["total_orders"] = 0

# Simple monetary metric: total_spent (from finance if available)
if "order_amount" in finance_orders.columns and not finance_orders.empty:
    agg_spent = (
        finance_orders.groupby("customer_id")["order_amount"]
        .sum()
        .reset_index()
        .rename(columns={"order_amount": "total_spent"})
    )
    crm_customers = crm_customers.merge(agg_spent, on="customer_id", how="left")
else:
    crm_customers["total_spent"] = np.round(
        np.random.uniform(0, 5000, len(crm_customers)), 2
    )

# Simple CLV estimation (toy formula)
crm_customers["clv_estimate"] = np.round(
    crm_customers["total_spent"] * np.random.uniform(1.1, 2.5, len(crm_customers)),
    2
)


# ============================================
# 2. Interactions (touchpoints)
# ============================================

interaction_types = ["email", "phone_call", "whatsapp", "meeting", "chatbot"]
interaction_outcomes = ["answered", "no_answer", "follow_up", "resolved", "escalated"]

interaction_rows = []
interaction_id = 1

for cid in customer_ids:
    num_interactions = np.random.randint(1, 15)
    dates = pd.date_range("2023-01-01", periods=num_interactions, freq="15D")

    for d in dates:
        interaction_rows.append({
            "interaction_id": interaction_id,
            "customer_id": cid,
            "interaction_date": d,
            "interaction_type": np.random.choice(interaction_types),
            "channel": np.random.choice(preferred_channels),
            "agent_id": np.random.randint(1, 51),
            "outcome": np.random.choice(interaction_outcomes),
            "notes": "Synthetic interaction for CRM lab."
        })
        interaction_id += 1

crm_interactions = pd.DataFrame(interaction_rows)


# ============================================
# 3. Support Tickets
# ============================================

ticket_categories = ["billing", "technical", "product", "shipping", "other"]
ticket_statuses = ["open", "in_progress", "resolved", "closed"]
priorities = ["low", "medium", "high", "urgent"]

ticket_rows = []
ticket_id = 1

for cid in customer_ids:
    num_tickets = np.random.randint(0, 5)  # not all customers open tickets
    if num_tickets == 0:
        continue

    dates = pd.date_range("2023-02-01", periods=num_tickets, freq="30D")

    for d in dates:
        created_at = d
        resolution_days = np.random.randint(1, 15)
        resolved_at = created_at + pd.to_timedelta(resolution_days, unit="D")

        ticket_rows.append({
            "ticket_id": ticket_id,
            "customer_id": cid,
            "created_at": created_at,
            "resolved_at": resolved_at,
            "category": np.random.choice(ticket_categories),
            "status": np.random.choice(ticket_statuses),
            "priority": np.random.choice(priorities),
            "resolution_time_days": resolution_days
        })
        ticket_id += 1

crm_tickets = pd.DataFrame(ticket_rows)


# ============================================
# 4. Churn Flags
# ============================================

# Simple heuristic: low activity + low NPS → higher churn risk
crm_churn = crm_customers[["customer_id", "nps_score", "total_orders", "segment"]].copy()

# Base probability
base_prob = np.random.uniform(0.05, 0.3, len(crm_churn))

# Adjust with NPS (lower NPS → higher churn)
nps_factor = (10 - crm_churn["nps_score"]) / 10.0

# Adjust with orders (fewer orders → higher churn)
order_factor = 1 / (1 + crm_churn["total_orders"].fillna(0))

churn_probability = base_prob + 0.4 * nps_factor + 0.3 * order_factor
churn_probability = churn_probability.clip(0, 1)

crm_churn["churn_probability"] = churn_probability

# Sample churned vs active
crm_churn["is_churned"] = np.random.binomial(1, churn_probability)

# Churn date & reason for churned customers
reasons = ["price", "competitor", "no_need", "bad_experience", "other"]
churn_dates = pd.date_range("2023-06-01", "2023-12-31", freq="D")

crm_churn["churn_date"] = pd.NaT
crm_churn["churn_reason"] = pd.NA

churn_mask = crm_churn["is_churned"] == 1
crm_churn.loc[churn_mask, "churn_date"] = np.random.choice(
    churn_dates, churn_mask.sum()
)
crm_churn.loc[churn_mask, "churn_reason"] = np.random.choice(
    reasons, churn_mask.sum()
)


# ============================================
# 5. SAVE ALL DATA
# ============================================

path = "../../data/raw/crm/"
os.makedirs(path, exist_ok=True)

crm_customers.to_csv(path + "crm_customers.csv", index=False)
crm_interactions.to_csv(path + "crm_interactions.csv", index=False)
crm_tickets.to_csv(path + "crm_tickets.csv", index=False)
crm_churn.to_csv(path + "crm_churn_flags.csv", index=False)

print("Full CRM domain generated successfully.")
