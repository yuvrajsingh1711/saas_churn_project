"""Phase 2+3: Cleaning (Pandas) + RFM segmentation -> cleaned + rfm_segmented.csv"""
import pandas as pd
import numpy as np
import os

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))
users = pd.read_csv(os.path.join(BASE, "users.csv"))
act = pd.read_csv(os.path.join(BASE, "activity_logs.csv"), parse_dates=["date"])

print("BEFORE:", act.shape, "nulls:", act["session_minutes"].isna().sum(), "dupes:", act.duplicated().sum())

# --- Cleaning (Pandas wala part, Power Query me bhi repeat karna) ---
act = act.drop_duplicates()
act["session_minutes"] = act["session_minutes"].fillna(act["session_minutes"].median())
act["region"] = act.get("region", np.nan)  # safety
act = act[act["session_minutes"] < 24 * 60]  # impossible outlier
act["date"] = pd.to_datetime(act["date"])
users["signup_date"] = pd.to_datetime(users["signup_date"])

END = act["date"].max()
LAST30 = END - pd.Timedelta(days=29)
PREV30 = END - pd.Timedelta(days=59)

def agg(g):
    active = g[g["logins"] > 0]
    last_active = active["date"].max() if len(active) else g["date"].min()
    last30 = g[g["date"] >= LAST30]["logins"].sum()
    prev30 = g[(g["date"] >= PREV30) & (g["date"] < LAST30)]["logins"].sum()
    return pd.Series({
        "last_active_date": last_active,
        "recency_days": (END - last_active).days,
        "frequency_30d": last30,
        "frequency_prev30d": prev30,
        "total_session_30d": g[g["date"] >= LAST30]["session_minutes"].sum(),
        "avg_features": g[g["date"] >= LAST30]["features_used"].mean(),
        "tickets_90d": g["support_tickets"].sum(),
    })

feat = act.groupby("user_id").apply(agg, include_groups=False).reset_index()
feat["activity_drop_pct"] = (feat["frequency_prev30d"] - feat["frequency_30d"]) / feat["frequency_prev30d"].replace(0, np.nan)
feat["activity_drop_pct"] = feat["activity_drop_pct"].fillna(0).clip(-1, 1)
feat["is_churned"] = (feat["recency_days"] > 30).astype(int)

df = users.merge(feat, on="user_id", how="left")
df.to_csv(os.path.join(BASE, "cleaned_churn_data.csv"), index=False)
print("cleaned:", df.shape, "churn_rate:", round(df["is_churned"].mean() * 100, 2), "%")

# --- RFM ---
df["R_Score"] = pd.qcut(df["recency_days"].rank(method="first", ascending=True), 5, labels=[5, 4, 3, 2, 1]).astype(int)
df["F_Score"] = pd.qcut(df["frequency_30d"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
df["M_Score"] = pd.qcut(df["monthly_revenue"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
df["RFM_Score"] = df["R_Score"].astype(str) + df["F_Score"].astype(str) + df["M_Score"].astype(str)

def tier(r):
    if r["R_Score"] >= 4 and r["F_Score"] >= 4 and r["M_Score"] >= 4:
        return "VIP"
    if r["R_Score"] >= 3 and r["F_Score"] >= 3:
        return "Loyal"
    if r["R_Score"] <= 2 or r["F_Score"] <= 2:
        return "At-Risk"
    return "Needs Attention"

df["Tier"] = df.apply(tier, axis=1)
# simple churn probability: drop + recency + tickets
df["churn_probability"] = (
    0.5 * df["activity_drop_pct"].clip(0, 1)
    + 0.3 * (df["recency_days"] / 90).clip(0, 1)
    + 0.2 * (df["tickets_90d"] / 5).clip(0, 1)
).round(2)

df.to_csv(os.path.join(BASE, "rfm_segmented.csv"), index=False)
print(df["Tier"].value_counts().to_string())
print("SAVED -> cleaned_churn_data.csv, rfm_segmented.csv")
