"""Executive Dashboard generator - Power BI jaisa, Python me (matplotlib)"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

BASE = "/Users/kishansingh/saas-churn-project"
DATA = os.path.join(BASE, "data/rfm_segmented.csv")
OUT = os.path.join(BASE, "powerbi/dashboard_images")
os.makedirs(OUT, exist_ok=True)

df = pd.read_csv(DATA)
act = pd.read_csv(os.path.join(BASE, "data/activity_logs.csv"), parse_dates=["date"])

total = len(df)
churn_rate = df["is_churned"].mean() * 100
mrr_lost = df.loc[df.is_churned == 1, "monthly_revenue"].sum()
at_risk = (df["Tier"] == "At-Risk").sum()
at_risk_rev = df.loc[df.Tier == "At-Risk", "monthly_revenue"].sum()

plt.rcParams.update({"figure.figsize": (8, 5), "axes.titlesize": 12})

# 1. Donut - Churn by Tier
ct = df.groupby("subscription_tier")["is_churned"].mean() * 100
fig, ax = plt.subplots()
ax.pie(ct.values, labels=[f"{i}\n{v:.1f}%" for i, v in zip(ct.index, ct.values)],
       autopct="", startangle=90, pctdistance=0.8,
       wedgeprops=dict(width=0.4, edgecolor="white"))
ax.set_title("Churn Rate by Subscription Tier")
plt.tight_layout(); plt.savefig(f"{OUT}/01_churn_by_tier.png", dpi=120); plt.close()

# 2. Bar - Churn by Region
cr = df.groupby("region")["is_churned"].mean().sort_values() * 100
fig, ax = plt.subplots()
cr.plot(kind="barh", ax=ax, color="#E74C3C")
ax.set_xlabel("Churn Rate %"); ax.set_title("Churn Rate by Region")
for i, v in enumerate(cr.values):
    ax.text(v + 0.2, i, f"{v:.1f}%", va="center")
plt.tight_layout(); plt.savefig(f"{OUT}/02_churn_by_region.png", dpi=120); plt.close()

# 3. Monthly trend (signup month vs churned share proxy + activity)
trend = act.copy()
trend["month"] = trend["date"].dt.to_period("M").astype(str)
monthly_logins = trend.groupby("month")["logins"].sum()
fig, ax = plt.subplots()
monthly_logins.plot(kind="line", marker="o", ax=ax, color="#2E86C1")
ax.set_title("User Activity Trend (Total Logins per Month)")
ax.set_ylabel("Total logins"); plt.xticks(rotation=30)
plt.tight_layout(); plt.savefig(f"{OUT}/03_activity_trend.png", dpi=120); plt.close()

# 4. Activity drop by Tier
ad = df.groupby("Tier")["activity_drop_pct"].mean().sort_values()
fig, ax = plt.subplots()
ad.plot(kind="bar", ax=ax, color=["#27AE60", "#F39C12", "#E74C3C"])
ax.set_title("Avg Activity Drop % by RFM Tier")
ax.set_ylabel("Avg drop"); plt.xticks(rotation=0)
plt.tight_layout(); plt.savefig(f"{OUT}/04_drop_by_tier.png", dpi=120); plt.close()

# 5. RFM distribution
tc = df["Tier"].value_counts()
fig, ax = plt.subplots()
tc.plot(kind="bar", ax=ax, color=["#E74C3C", "#2E86C1", "#F39C12"])
ax.set_title("Users by RFM Tier"); plt.xticks(rotation=0)
for i, v in enumerate(tc.values):
    ax.text(i, v + 20, str(v), ha="center")
plt.tight_layout(); plt.savefig(f"{OUT}/05_rfm_dist.png", dpi=120); plt.close()

# Top 20 at-risk table
top20 = df[df.Tier == "At-Risk"].sort_values("churn_probability", ascending=False).head(20)
top20[["user_id", "email", "subscription_tier", "region", "recency_days", "churn_probability", "monthly_revenue"]].to_csv(f"{OUT}/top20_atrisk.csv", index=False)

# HTML executive summary
html = f"""<html><head><meta charset="utf-8"><title>SaaS Churn Executive Summary</title>
<style>body{{font-family:Arial;max-width:1000px;margin:auto;padding:20px;background:#f4f6f7}}
.kpi{{display:flex;gap:15px}} .card{{flex:1;background:#fff;padding:20px;border-radius:10px;text-align:center;box-shadow:0 2px 5px #ccc}}
.card h2{{margin:0;color:#2E86C1}} img{{width:100%;background:#fff;border-radius:10px;margin:15px 0;padding:10px}}
table{{border-collapse:collapse;width:100%;background:#fff}} th,td{{border:1px solid #ddd;padding:8px;font-size:13px}} th{{background:#2E86C1;color:#fff}}</style>
</head><body>
<h1>SaaS Customer Churn - Executive Summary</h1>
<p>Power BI layout ka Python version | Data: rfm_segmented.csv (2000 users)</p>
<div class="kpi">
<div class="card"><p>Total Users</p><h2>{total}</h2></div>
<div class="card"><p>Churn Rate</p><h2>{churn_rate:.1f}%</h2></div>
<div class="card"><p>MRR Lost</p><h2>Rs {mrr_lost:,.0f}</h2></div>
<div class="card"><p>At-Risk Users</p><h2>{at_risk}</h2><p>Revenue at risk: Rs {at_risk_rev:,.0f}</p></div>
</div>
<h2>1. Churn by Subscription Tier</h2><img src="dashboard_images/01_churn_by_tier.png">
<p>Enterprise me churn % sabse zyada (~20.9%) - MRR loss ka main reason.</p>
<h2>2. Churn by Region</h2><img src="dashboard_images/02_churn_by_region.png">
<h2>3. Activity Trend (last 90 days)</h2><img src="dashboard_images/03_activity_trend.png">
<p>Last 30 din me activity giri - churn ka early signal.</p>
<h2>4. Activity Drop by RFM Tier</h2><img src="dashboard_images/04_drop_by_tier.png">
<h2>5. RFM Distribution</h2><img src="dashboard_images/05_rfm_dist.png">
<h2>6. Top 20 At-Risk Users (Retention Action List)</h2>
{top20[["user_id","email","subscription_tier","region","recency_days","churn_probability","monthly_revenue"]].to_html(index=False)}
<p><b>Retention plan:</b> VIP At-Risk ko personal call + discount, Basic Sharp-Drop ko onboarding email, tickets>2 walo ko priority support.</p>
</body></html>"""
with open(os.path.join(BASE, "powerbi/executive_dashboard.html"), "w") as f:
    f.write(html)

print(f"KPI: users={total} churn={churn_rate:.1f}% mrr_lost={mrr_lost:.0f} at_risk={at_risk}")
print("Saved:", OUT, "+ executive_dashboard.html")
