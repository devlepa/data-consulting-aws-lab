import pandas as pd
import numpy as np
import os

np.random.seed(42)

# ============================================
# 0. Try to load orders from Finance (for links)
# ============================================
orders = None
available_order_ids = None

try:
    orders = pd.read_csv("../../data/raw/finance/orders.csv")
    # Use only completed orders for marketing-driven sales
    completed_orders = orders[orders["status"] == "completed"].copy()
    available_order_ids = completed_orders["order_id"].values
    print(f"Loaded {len(completed_orders)} completed orders from finance.")
except FileNotFoundError:
    print("WARNING: finance/orders.csv not found. "
          "Marketing will generate synthetic order links only.")
    available_order_ids = np.arange(1, 5001)


# ============================================
# 1. Campaigns (high-level view)
# ============================================
num_campaigns = 60
campaign_ids = np.arange(1, num_campaigns + 1)

campaigns = pd.DataFrame({
    "campaign_id": campaign_ids,
    "campaign_name": [f"Campaign_{i}" for i in campaign_ids],
    "objective": np.random.choice(
        ["Awareness", "Traffic", "Leads", "Sales"],
        num_campaigns
    ),
    "start_date": pd.date_range("2023-01-01", periods=num_campaigns, freq="5D"),
    "end_date": pd.date_range("2023-01-10", periods=num_campaigns, freq="5D"),
    "platform": np.random.choice(
        ["Facebook", "Instagram", "Google", "TikTok", "Email"],
        num_campaigns
    ),
    "budget": np.round(np.random.uniform(1_000, 50_000, num_campaigns), 2)
})


# ============================================
# 2. Ad Groups (segment-level)
# ============================================
num_ad_groups = 200
ad_group_ids = np.arange(1, num_ad_groups + 1)

ad_groups = pd.DataFrame({
    "ad_group_id": ad_group_ids,
    "campaign_id": np.random.choice(campaign_ids, num_ad_groups),
    "target_audience": np.random.choice(
        ["18-24", "25-34", "35-44", "45-54", "55+"],
        num_ad_groups
    ),
    "gender": np.random.choice(["Male", "Female", "All"], num_ad_groups),
    "interests": np.random.choice(
        ["Tech", "Sports", "Beauty", "Fitness", "Business", "Education"],
        num_ad_groups
    ),
    "device_type": np.random.choice(
        ["Mobile", "Desktop", "Tablet", "All"],
        num_ad_groups
    )
})


# ============================================
# 3. Ads (creative-level)
# ============================================
num_ads = 700
ad_ids = np.arange(1, num_ads + 1)

ads = pd.DataFrame({
    "ad_id": ad_ids,
    "ad_group_id": np.random.choice(ad_group_ids, num_ads),
    "creative_type": np.random.choice(["Image", "Video", "Carousel"], num_ads),
    "copy_length": np.random.choice(["Short", "Medium", "Long"], num_ads),
    "cta": np.random.choice(
        ["Buy Now", "Learn More", "Sign Up", "Download"],
        num_ads
    ),
    "language": np.random.choice(["EN", "ES", "PT"], num_ads)
})


# ============================================
# 4. Daily Ad Performance (impressions, clicks, spend)
# ============================================
dates = pd.date_range("2023-01-01", "2023-06-30", freq="D")
records = []

for ad in ad_ids:
    # Not every ad runs every day → sparsity
    active_days = np.random.choice(
        dates,
        size=np.random.randint(30, len(dates)),
        replace=False
    )
    for date in active_days:
        impressions = np.random.randint(500, 100_000)
        clicks = np.random.randint(0, max(1, impressions // 20))  # up to 5% CTR
        spend = np.round(np.random.uniform(5, 300), 2)

        ctr = clicks / impressions if impressions > 0 else 0
        cpc = spend / clicks if clicks > 0 else None
        cpm = (spend / impressions * 1000) if impressions > 0 else None

        records.append({
            "ad_id": ad,
            "date": date,
            "impressions": impressions,
            "clicks": clicks,
            "spend": spend,
            "ctr": ctr,
            "cpc": cpc,
            "cpm": cpm
        })

daily_performance = pd.DataFrame(records)


# ============================================
# 5. Leads (from ads) with links to orders & customers
# ============================================
num_leads = 20_000

lead_dates = np.random.choice(dates, num_leads)

leads = pd.DataFrame({
    "lead_id": np.arange(1, num_leads + 1),
    "ad_id": np.random.choice(ad_ids, num_leads),
    "lead_date": lead_dates,
    "lead_source": np.random.choice(
        ["Facebook", "Google", "Instagram", "TikTok", "Email"],
        num_leads
    ),
    "utm_medium": np.random.choice(
        ["paid_social", "paid_search", "email", "referral"],
        num_leads
    ),
    "utm_campaign": np.random.choice(campaigns["campaign_name"], num_leads),
    "email": [f"user_{i}@example.com" for i in range(1, num_leads + 1)],
    "phone": [f"300-{np.random.randint(1000000,9999999)}" for _ in range(num_leads)],
})

# Conversion flags (funnel logic)
# 1) Lead became MQL (marketing qualified lead)
leads["is_mql"] = np.random.choice([0, 1], num_leads, p=[0.5, 0.5])

# 2) MQL converted to customer
leads["converted_to_customer"] = 0
mql_mask = leads["is_mql"] == 1
leads.loc[mql_mask, "converted_to_customer"] = np.random.choice(
    [0, 1],
    mql_mask.sum(),
    p=[0.7, 0.3]  # 30% of MQLs become customers
)

# 3) Some customers actually purchase (become buyers)
leads["became_buyer"] = 0
customer_mask = leads["converted_to_customer"] == 1
leads.loc[customer_mask, "became_buyer"] = np.random.choice(
    [0, 1],
    customer_mask.sum(),
    p=[0.4, 0.6]  # 60% of customers end up buying
)

buyer_mask = leads["became_buyer"] == 1
num_buyers = buyer_mask.sum()

# Assign order_ids to buyers (link to finance domain)
leads["order_id"] = pd.NA
if num_buyers > 0:
    leads.loc[buyer_mask, "order_id"] = np.random.choice(
        available_order_ids,
        num_buyers,
        replace=True
    )

# If we have real orders, map to customer_id from finance
if orders is not None:
    leads = leads.merge(
        completed_orders[["order_id", "customer_id"]],
        on="order_id",
        how="left"
    )
else:
    # Synthetic customer_id if finance does not exist yet
    leads["customer_id"] = np.where(
        buyer_mask,
        np.random.randint(1, 1001, num_leads),
        np.nan
    )

# Funnel stage label
def infer_stage(row):
    if row["became_buyer"] == 1:
        return "Customer (Buyer)"
    if row["converted_to_customer"] == 1:
        return "Customer (No Purchase Yet)"
    if row["is_mql"] == 1:
        return "MQL"
    return "Raw Lead"

leads["funnel_stage"] = leads.apply(infer_stage, axis=1)


# ============================================
# SAVE DATA
# ============================================
path = "../../data/raw/marketing/"
os.makedirs(path, exist_ok=True)

campaigns.to_csv(path + "campaigns.csv", index=False)
ad_groups.to_csv(path + "ad_groups.csv", index=False)
ads.to_csv(path + "ads.csv", index=False)
daily_performance.to_csv(path + "daily_performance.csv", index=False)
leads.to_csv(path + "leads.csv", index=False)

print("Full marketing domain generated successfully.")
