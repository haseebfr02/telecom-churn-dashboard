# 📊 Telecom Customer Churn End-to-End BI Pipeline

> A complete **data analytics and BI pipeline** project  from raw data ingestion
> through ETL, SQL analysis, and interactive Power BI dashboard delivery.

---

## 📌 Project Overview

Customer churn costs the telecom industry billions annually.
Acquiring a new customer costs **5–7x more** than retaining one.

This project builds a **full enterprise BI pipeline** on 7,012 customer records to:
- Identify the key drivers of churn
- Quantify monthly revenue at risk
- Deliver actionable retention recommendations

---

## 🏗 Pipeline Architecture

```
[Excel File]      [JSON API]
(Demographics)    (Billing)
      ↓                ↓
 ┌─────────────────────────┐
 │   ETL Pipeline          │  (replaces SSIS)
 │   Extract→Transform     │
 │   →Load to SQLite DB    │
 └────────────┬────────────┘
              ↓
 ┌─────────────────────────┐
 │   SQL Analysis          │
 │   Clean + Aggregate     │
 │   10 business queries   │
 └────────────┬────────────┘
              ↓
 ┌─────────────────────────┐
 │   Power BI Dashboard    │
 │   KPIs + 8 Charts       │
 │   DAX Measures          │
 └─────────────────────────┘
```

---

## 🗂 Project Structure

```
telecom-churn-dashboard/
├── data/
│   ├── telco_churn.csv                 ← Base dataset (7,043 rows)
│   ├── telco_churn_cleaned.csv         ← Cleaned data (Tableau)
│   ├── telco_master_powerbi.csv        ← ETL output (Power BI input)
│   ├── telecom_churn.db                ← SQLite database (3 tables)
│   ├── sql_analysis_results.xlsx       ← SQL results (7 sheets)
│   └── raw/
│       ├── source_a_demographics.xlsx  ← Simulated CRM Excel export
│       └── source_b_billing_api.json   ← Simulated billing API response
├── pipeline/
│   ├── step1_data_sourcing.py
│   ├── step2_etl_pipeline.py
│   └── step3_sql_analysis.py
├── notebooks/
│   ├── 01_cleaning_eda.ipynb
│   └── 02_bi_pipeline.ipynb
├── visuals/                            ← 8 auto-generated charts
├── dashboard/
│   ├── POWERBI_GUIDE.md
│   └── TABLEAU_GUIDE.md
├── requirements.txt
└── README.md
```

---

## 📊 Executive Dashboard Preview

![Executive Dashboard](visuals/00_executive_dashboard.png)

---

## 🔍 Key Findings

| Finding | Detail |
|---|---|
| **Overall Churn Rate** | 41.7% — 2,925 of 7,012 customers churned |
| **Monthly Revenue at Risk** | ~$195,500/month from churned customers |
| **Contract Type** | Month-to-month churn at **53.3%** vs 23.7% for two-year |
| **New Customers** | 0–12 month customers churn at **51%** — critical risk window |
| **Internet Service** | Fiber optic customers churn at **49.9%** despite premium pricing |
| **Payment Method** | Electronic check users churn 6.8% more than auto-pay users |
| **Senior Citizens** | Churn at **44.8%** vs 41.1% for non-seniors |

---

## 💡 Business Recommendations

| # | Recommendation | Expected Impact |
|---|---|---|
| 1 | Loyalty discount at 3-month mark → push toward annual contract | Reduce M2M churn 15–20% |
| 2 | Proactive onboarding check-ins at months 1, 3, 6 | Reduce 51% first-year churn |
| 3 | Conduct Fiber Optic NPS survey; fix top pain points | Retain premium-paying users |
| 4 | $5/month discount for switching to auto-pay | Reduce electronic check churn |

---

## 🗄 Database Schema (SQLite)

- **fact_customers**  7,012 rows, main fact table
- **dim_contract** 3 rows, contract type dimension
- **agg_churn_summary**  572 rows, pre-aggregated for Power BI

---

## 🛠 Tools Used

| Tool | Role |
|---|---|
| Python 3 | Data sourcing, ETL, EDA |
| Pandas | Data manipulation |
| SQLite | Database + SQL analysis |
| Matplotlib / Seaborn | Static charts |
| Power BI Desktop | Interactive BI dashboard |
| Tableau Public | Secondary dashboard |
| Excel / JSON | Raw data source simulation |

---

## 👤 Author

**Haseeb Waqas** — Data Analyst  
📧 haseeb.fr02@gmail.com  
🔗 [LinkedIn](https://www.linkedin.com/in/haseeb-waqas-15531b2a0/)
