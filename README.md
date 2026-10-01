# SaaS Customer Churn Prediction & Retention

A subscription analytics project that identifies customers likely to cancel next month, segments them with an RFM model, and delivers an executive dashboard for retention action.

## Business Problem

Acquiring a new subscriber costs 5–7x more than retaining one. This project answers three questions for the leadership team:

1. What is the monthly churn rate, and is it rising?
2. Which subscription tier and region lose the most revenue?
3. Which customers are **VIP**, **Loyal**, or **At-Risk** — and who should the retention team contact first?

**Churn definition:** a user with zero logins in the trailing 30 days (`recency_days > 30`) is marked churned.

## Results (Synthetic Dataset, n = 2,000)

| Metric | Value |
|---|---|
| Total users | 2,000 |
| Churn rate | 15.0% (300 users) |
| MRR lost | Rs 4,13,301 |
| At-Risk users | 1,073 |
| RFM split | VIP 284 · Loyal 643 · At-Risk 1,073 |

Churn by tier: Enterprise 20.9% · Pro 15.3% · Basic 13.9%. Volume churn sits in Basic, but value churn concentrates in Enterprise — so VIP At-Risk accounts get priority outreach.

## Repository Structure

```
saas-churn-project/
├── data/
│   ├── users.csv               # user master (tier, region, revenue)
│   ├── activity_logs.csv       # 90 days of daily activity (~180k rows)
│   ├── cleaned_churn_data.csv  # cleaned + engineered features
│   └── rfm_segmented.csv       # final model output (Tier, scores, churn probability)
├── notebooks/
│   ├── generate_dummy_data.py  # reproducible synthetic data generator
│   ├── cleaning_rfm.py         # Pandas cleaning + RFM segmentation
│   └── build_dashboard.py      # matplotlib executive dashboard generator
├── powerbi/
│   ├── PowerBI_Checklist.md    # step-by-step .pbix build guide with DAX
│   ├── executive_dashboard.html# one-page executive summary (open in browser)
│   └── dashboard_images/       # charts + Top-20 At-Risk list
└── README.md
```

## Method

### 1. Data Cleaning (Pandas + Power Query)

- Dropped duplicates, imputed missing `session_minutes` with the median, removed impossible sessions (> 24h).
- Power Query (in Power BI): data-type checks + conditional column `Activity_Flag = "Sharp Drop" if activity_drop_pct > 0.5`.

### 2. Feature Engineering

Per user, over a 90-day window:

- `recency_days` — days since last login with activity
- `frequency_30d` / `frequency_prev30d` — logins in last vs. prior 30 days
- `activity_drop_pct = (prev30 − last30) / prev30`
- `is_churned = 1 if recency_days > 30`

### 3. RFM Segmentation

Quintile-scored with `qcut`:

- **R** (Recency, inverted) · **F** (Frequency) · **M** (Monetary), each 1–5
- `VIP` — R ≥ 4, F ≥ 4, M ≥ 4
- `Loyal` — R ≥ 3 and F ≥ 3
- `At-Risk` — R ≤ 2 or F ≤ 2

A *churn probability* blends the three strongest signals:

```
churn_probability = 0.5 × activity_drop + 0.3 × recency/90 + 0.2 × tickets/5
```

### 4. Executive Dashboard

`powerbi/executive_dashboard.html` (Python-generated mirror of the Power BI layout):

- KPI cards: users, churn rate, MRR lost, At-Risk revenue
- Churn by subscription tier (donut) and by region (bar)
- 90-day activity trend and activity-drop by RFM tier
- **Top-20 At-Risk table** (user, email, tier, churn probability) for the retention team

To build the native Power BI version, follow `powerbi/PowerBI_Checklist.md` — it includes the four DAX measures (`Total Users`, `Churn Rate %`, `MRR Lost`, `At-Risk Revenue`) and the one-page layout.

## Reproduce

```bash
pip install pandas numpy faker matplotlib
python notebooks/generate_dummy_data.py   # data/
python notebooks/cleaning_rfm.py          # cleaned + RFM
python notebooks/build_dashboard.py       # powerbi/executive_dashboard.html
```

Then open `powerbi/executive_dashboard.html` in a browser, or load `data/rfm_segmented.csv` into Power BI Desktop per the checklist.

## Retention Recommendations

- **VIP At-Risk** — personal outreach + discount; highest MRR exposure.
- **Basic with sharp activity drop (> 50%)** — onboarding email sequence.
- **Users with 2+ support tickets** — priority support queue.
- Investigate high-churn regions for language/support coverage gaps.

## Data Note

All data is **synthetic**, generated reproducibly (`seed = 42`) for demonstration. Swap in real `users` + `activity_logs` CSVs with the same schema to run the identical pipeline.

## Tech Stack

Python 3.9 · Pandas · NumPy · Faker · Matplotlib · Power BI (Power Query + DAX)
