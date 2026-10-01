# Power BI Executive Dashboard - Screenshot Wali Checklist 📸

File: `rfm_segmented.csv` ko Power BI Desktop me import karo.
Location: `saas-churn-project/data/rfm_segmented.csv`
Har step ke baad Screenshot lo — yehi portfolio / report me lagega.

---

## Step 0: Get Data (Screenshot 1)
1. Power BI Desktop > Home > **Get Data > Text/CSV**
2. `rfm_segmented.csv` select karo > Load
3. Left panel me **Data View** kholo, check karo: 2000 rows, columns: `user_id, region, subscription_tier, monthly_revenue, recency_days, frequency_30d, R_Score, F_Score, M_Score, Tier, churn_probability, is_churned`
📸 **Screenshot 1:** Data View table dikhe, status bar me "2000 rows"

## Step 1: Power Query Cleaning (Screenshot 2-3)
1. Home > **Transform Data** (Power Query khulega)
2. Check:
   - `date` / `signup_date` Type = Date
   - `monthly_revenue` = Decimal Number
   - `is_churned` = Whole Number
3. **Add Column > Conditional Column:**
   - Name: `Activity_Flag`
   - Rule: `IF [activity_drop_pct] > 0.5 THEN "Sharp Drop" ELSE "Stable"`
   - OK > **Close & Apply**
📸 **Screenshot 2:** Power Query window me `Activity_Flag` column banate hue
📸 **Screenshot 3:** Applied Steps pane: Source, Changed Type, Added Conditional Column

## Step 2: DAX Measures (Screenshot 4)
Modeling > **New Measure** > ek-ek karke 4 measures paste karo:

```dax
Total Users = COUNTROWS(rfm_segmented)

Churn Rate % = DIVIDE(SUM(rfm_segmented[is_churned]), [Total Users])

MRR Lost = SUMX(FILTER(rfm_segmented, rfm_segmented[is_churned]=1), rfm_segmented[monthly_revenue])

At-Risk Revenue = SUMX(FILTER(rfm_segmented, rfm_segmented[Tier]="At-Risk"), rfm_segmented[monthly_revenue])
```
Format: `Churn Rate %` ko % format do (Measure Tools > %).
📸 **Screenshot 4:** Model View / Data View me 4 measures list me dikhe

Expected values (verify karo):
- Total Users = 2000
- Churn Rate % = ~15%
- MRR Lost = ~4,13,301
- At-Risk Revenue = ~11-12 Lakh (1073 users × avg revenue)

## Step 3: Dashboard Layout - 1 Page (Screenshot 5 = Final)
**Page Name:** `Executive Summary` (double-click bottom tab se rename)

Layout (top se bottom):
```
[Slicer: region] [Slicer: subscription_tier] [Slicer: Tier]
[Card: Total Users] [Card: Churn Rate %] [Card: MRR Lost] [Card: At-Risk Revenue]
[Line: Churn Trend]        [Donut: Churn by Tier]
[Map: Churn by Region]     [Bar: Activity Drop by Tier]
[Table: Top 20 At-Risk Users]
```

### 3a. Slicers (top strip)
Insert > Slicer > Field: `region`, dusra Slicer: `subscription_tier`, teesra: `Tier`
📸 check: 3 slicers top me horizontal

### 3b. KPI Cards (4 cards)
Insert > Card > Field:
- Card 1: `[Total Users]`
- Card 2: `[Churn Rate %]`
- Card 3: `[MRR Lost]` (₹ format)
- Card 4: At-Risk Count = `COUNTROWS(FILTER(rfm_segmented, rfm_segmented[Tier]="At-Risk"))` ya Visual Filter se Tier=At-Risk
📸 check: 2000 | 15% | 4.1L | 1073

### 3c. Donut - Churn by Tier
Insert > Donut Chart:
- Legend: `subscription_tier`
- Values: `[Churn Rate %]`
- Expected: Enterprise ~20.9%, Pro ~15.3%, Basic ~13.9%
📸 **Screenshot 6:** Donut me Enterprise sabse bada slice

### 3d. Map - Churn by Region
Insert > Filled Map (ya Bar agar Map na chale):
- Location: `region`
- Tooltips / Values: `[Churn Rate %]`
📸 **Screenshot 7:** Map me 6 regions color-coded

### 3e. Bar - Activity Drop Proof
Insert > Clustered Bar:
- Y-axis: `Tier`
- X-axis: Average of `activity_drop_pct`
- Expected: At-Risk ka bar sabse lamba
📸 **Screenshot 8:** Bar chart proof: activity giri = churn

### 3f. Table - Retention Action List
Insert > Table:
- Columns: `user_id, email, subscription_tier, region, recency_days, churn_probability`
- Visual Filter: `Tier = At-Risk`
- Sort: `churn_probability` Descending
- Top N Filter: Top 20
📸 **Screenshot 9:** Table me Top 20 At-Risk users emails ke saath — yehi retention team ko doge

## Step 4: Formatting (Screenshot 10)
1. View > Theme: Dark ya Executive theme
2. Har visual ka Title ON: "Churn Rate by Tier" etc.
3. File > Save As: `powerbi/churn_dashboard.pbix`
📸 **Screenshot 10 (FINAL):** Pura 1-page dashboard, sab visuals ek screen me

---

## ✅ Final Verification Checklist
- [ ] 2000 rows loaded?
- [ ] Activity_Flag column bana?
- [ ] 4 DAX measures sahi value de rahe? (15% / 4.13L)
- [ ] Donut me Enterprise highest?
- [ ] Table me 20 At-Risk emails?
- [ ] .pbix saved in `powerbi/` folder?
- [ ] 10 screenshots folder me? (`powerbi/screenshots/` banao aur save karo)

## ❌ Common Errors
| Error | Fix |
|---|---|
| Map blank | Region names Delhi/Mumbai ko Category = Place banao (Column Tools > Data Category) |
| Churn % 0 dikhe | `is_churned` SUM hai, Average nahi — Aggregation check karo |
| MRR Lost bada number | Format ko Indian Rupee + Thousands separator do |
| Conditional column error | `activity_drop_pct` Decimal hai na, Text nahi — Type check karo |

Interview line: "Basic tier me churn volume zyada hai, lekin Enterprise me MRR loss sabse zyada hai, isliye VIP At-Risk ko priority retention offer diya."
