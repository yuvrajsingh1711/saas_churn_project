"""SaaS Churn - Phase 1: Dummy Data Generator (2000 users, 90 days activity)"""
import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import os

fake = Faker()
np.random.seed(42)
Faker.seed(42)

N_USERS = 2000
END_DATE = datetime(2026, 9, 30).date()
START_ACTIVITY = END_DATE - timedelta(days=89)

DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")
DATA_DIR = os.path.abspath(DATA_DIR)
os.makedirs(DATA_DIR, exist_ok=True)

regions = ["Delhi", "Mumbai", "Bangalore", "Hyderabad", "US-East", "UK-London"]
tiers = ["Basic", "Pro", "Enterprise"]
tier_probs = [0.60, 0.30, 0.10]
tier_price = {"Basic": 499, "Pro": 1499, "Enterprise": 4999}

# ---- users.csv ----
users = []
for i in range(1, N_USERS + 1):
    tier = np.random.choice(tiers, p=tier_probs)
    signup = fake.date_between(start_date="-2y", end_date="-3m")
    users.append({
        "user_id": f"U{i:04d}",
        "signup_date": str(signup),
        "region": str(np.random.choice(regions)),
        "subscription_tier": tier,
        "monthly_revenue": tier_price[tier] + int(np.random.randint(-50, 51)),
        "email": fake.email(),
    })
users_df = pd.DataFrame(users)
# 20% users ko At-Risk banane ke liye flag (activity me use hoga)
# 15% users pure churned: last 35-60 din zero activity
churned_ids = set(np.random.choice(users_df["user_id"], size=int(N_USERS * 0.15), replace=False))
at_risk_ids = set(np.random.choice(list(set(users_df["user_id"]) - churned_ids), size=int(N_USERS * 0.20), replace=False))
users_df.to_csv(os.path.join(DATA_DIR, "users.csv"), index=False)
print(f"users.csv: {users_df.shape}")

# ---- activity_logs.csv ----
churn_cutoff = {uid: int(np.random.randint(35, 61)) for uid in churned_ids}
rows = []
for _, u in users_df.iterrows():
    uid = u["user_id"]
    is_risky = uid in at_risk_ids
    base_logins = {"Basic": 2.5, "Pro": 4.0, "Enterprise": 5.5}[u["subscription_tier"]]
    for d in range(90):
        day = START_ACTIVITY + timedelta(days=d)
        # churned users: last 35-60 din bilkul zero
        if uid in churned_ids and d >= 90 - int(churn_cutoff[uid]):
            logins = 0
        # last 30 din me risky users ka activity 70% gira do
        elif is_risky and d >= 60:
            lam = base_logins * 0.3
            lam = max(lam, 0.2)
            logins = int(np.random.poisson(lam))
        else:
            lam = base_logins
            lam = max(lam, 0.2)
            logins = int(np.random.poisson(lam))
        # kuch din 0 login
        if np.random.rand() < 0.08:
            logins = 0
        session = round(logins * np.random.uniform(8, 25), 1) if logins > 0 else 0.0
        rows.append({
            "user_id": uid,
            "date": str(day),
            "logins": logins,
            "session_minutes": session,
            "features_used": int(np.random.randint(0, 16)) if logins > 0 else 0,
            "support_tickets": int(np.random.choice([0, 0, 0, 1, 2], p=[0.7, 0.1, 0.1, 0.07, 0.03])),
        })

activity_df = pd.DataFrame(rows)
# thode missing + duplicate daalo taaki cleaning demo ho sake
idx = np.random.choice(activity_df.index, size=200, replace=False)
activity_df.loc[idx, "session_minutes"] = np.nan
activity_df = pd.concat([activity_df, activity_df.sample(100, random_state=42)], ignore_index=True)

activity_df.to_csv(os.path.join(DATA_DIR, "activity_logs.csv"), index=False)
print(f"activity_logs.csv: {activity_df.shape}")
print(f"Churned planted: {len(churned_ids)}, At-Risk planted: {len(at_risk_ids)}")
print("DONE ->", DATA_DIR)
