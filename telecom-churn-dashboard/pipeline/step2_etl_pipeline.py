"""
STEP 2 — ETL PIPELINE (Replaces SSIS)
======================================
E — Extract   : Read from Excel + JSON sources
T — Transform : Standardize, validate, merge, enrich
L — Load      : Write to SQLite database (3 tables)

In a real project this would be done in SSIS visually,
but the logic is identical — this script teaches you
exactly what SSIS does under the hood.

Author : Haseeb Waqas
"""

import pandas as pd
import numpy as np
import sqlite3
import json
import os
from datetime import datetime

RAW_DIR = '../data/raw/'
DB_PATH = '../data/telecom_churn.db'

print("=" * 60)
print("ETL PIPELINE — Telecom Customer Churn")
print(f"Started : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

# ═══════════════════════════════════════════════════════════════════════════════
# EXTRACT
# ═══════════════════════════════════════════════════════════════════════════════
print("\n── EXTRACT ──")

# Extract Source A (Excel)
df_demo = pd.read_excel(f'{RAW_DIR}source_a_demographics.xlsx')
print(f"   Source A extracted : {len(df_demo):,} rows from Excel")

# Extract Source B (JSON API)
with open(f'{RAW_DIR}source_b_billing_api.json') as f:
    api_response = json.load(f)
df_bill = pd.DataFrame(api_response['data'])
print(f"   Source B extracted : {len(df_bill):,} rows from JSON API")

# ═══════════════════════════════════════════════════════════════════════════════
# TRANSFORM — Source A (Demographics)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n── TRANSFORM — Demographics ──")

before = len(df_demo)

# T1: Remove duplicates
df_demo.drop_duplicates(subset='customerID', keep='first', inplace=True)
print(f"   Duplicates removed  : {before - len(df_demo)} rows dropped → {len(df_demo):,} remain")

# T2: Standardize gender casing
df_demo['gender'] = df_demo['gender'].str.capitalize()
print(f"   Gender standardized : all values → 'Male' / 'Female'")

# T3: Fill missing Partner values with mode
mode_partner = df_demo['Partner'].mode()[0]
nulls = df_demo['Partner'].isnull().sum()
df_demo['Partner'].fillna(mode_partner, inplace=True)
print(f"   Partner nulls filled: {nulls} missing → filled with '{mode_partner}'")

# T4: Validate SeniorCitizen is 0 or 1
invalid_sc = df_demo[~df_demo['SeniorCitizen'].isin([0, 1])]
if len(invalid_sc) > 0:
    df_demo = df_demo[df_demo['SeniorCitizen'].isin([0, 1])]
    print(f"   SeniorCitizen       : {len(invalid_sc)} invalid rows removed")
else:
    print(f"   SeniorCitizen       : ✅ All values valid (0/1)")

# ═══════════════════════════════════════════════════════════════════════════════
# TRANSFORM — Source B (Billing)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n── TRANSFORM — Billing ──")

# T5: Fix TotalCharges (string → numeric)
df_bill['TotalCharges'] = df_bill['TotalCharges'].replace(' ', np.nan)
df_bill['TotalCharges'] = pd.to_numeric(df_bill['TotalCharges'], errors='coerce')
null_tc = df_bill['TotalCharges'].isnull().sum()
df_bill['TotalCharges'].fillna(
    df_bill['MonthlyCharges'] * 1,  # estimate: 1 month if unknown
    inplace=True
)
print(f"   TotalCharges fixed  : {null_tc} blanks → estimated from MonthlyCharges")

# T6: Remove invalid MonthlyCharges (negative values)
invalid_mc = (df_bill['MonthlyCharges'] < 0).sum()
df_bill = df_bill[df_bill['MonthlyCharges'] >= 0]
print(f"   MonthlyCharges      : {invalid_mc} negative values removed")

# T7: Encode Churn as binary
df_bill['Churn_Binary'] = df_bill['Churn'].map({'Yes': 1, 'No': 0})
print(f"   Churn encoded       : 'Yes'→1, 'No'→0")

# ═══════════════════════════════════════════════════════════════════════════════
# TRANSFORM — Merge & Enrich
# ═══════════════════════════════════════════════════════════════════════════════
print("\n── TRANSFORM — Merge & Feature Engineering ──")

# T8: Inner join on customerID
df_master = pd.merge(df_demo, df_bill, on='customerID', how='inner')
print(f"   Merge result        : {len(df_master):,} rows (inner join on customerID)")

# T9: Feature Engineering
df_master['Tenure_Group'] = pd.cut(
    df_master['tenure'],
    bins=[0, 12, 24, 48, 72],
    labels=['0-12 Months', '13-24 Months', '25-48 Months', '49-72 Months']
)

df_master['Charge_Tier'] = pd.cut(
    df_master['MonthlyCharges'],
    bins=[0, 35, 65, 90, 500],
    labels=['Low', 'Mid', 'High', 'Premium']
)

df_master['Revenue_Segment'] = np.where(
    df_master['TotalCharges'] > df_master['TotalCharges'].quantile(0.75), 'High Value',
    np.where(df_master['TotalCharges'] > df_master['TotalCharges'].quantile(0.25),
             'Mid Value', 'Low Value')
)

df_master['Is_Senior'] = df_master['SeniorCitizen'].map({1: 'Senior', 0: 'Non-Senior'})

print(f"   Features created    : Tenure_Group, Charge_Tier, Revenue_Segment, Is_Senior")

# ═══════════════════════════════════════════════════════════════════════════════
# LOAD — Write to SQLite Database (3 tables)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n── LOAD → SQLite Database ──")

conn = sqlite3.connect(DB_PATH)

# Table 1: fact_customers (main fact table)
df_master.to_sql('fact_customers', conn, if_exists='replace', index=False)
print(f"   ✅ fact_customers    : {len(df_master):,} rows loaded")

# Table 2: dim_contract (contract dimension)
dim_contract = df_master[['Contract', 'Churn_Binary']].groupby('Contract').agg(
    Total_Customers=('Churn_Binary', 'count'),
    Churned=('Churn_Binary', 'sum'),
    Churn_Rate=('Churn_Binary', 'mean')
).reset_index().round(4)
dim_contract.to_sql('dim_contract', conn, if_exists='replace', index=False)
print(f"   ✅ dim_contract      : {len(dim_contract)} contract types loaded")

# Table 3: agg_churn_summary (pre-aggregated for Power BI)
agg = df_master.groupby(
    ['Contract', 'InternetService', 'Tenure_Group', 'Charge_Tier', 'PaymentMethod']
, observed=True).agg(
    Total_Customers=('customerID', 'count'),
    Churned_Customers=('Churn_Binary', 'sum'),
    Avg_Monthly_Charge=('MonthlyCharges', 'mean'),
    Avg_Tenure=('tenure', 'mean'),
    Total_Revenue=('TotalCharges', 'sum')
).reset_index().round(2)
agg.to_sql('agg_churn_summary', conn, if_exists='replace', index=False)
print(f"   ✅ agg_churn_summary : {len(agg):,} aggregated rows loaded")

conn.close()

# ── Validate Load ─────────────────────────────────────────────────────────────
conn = sqlite3.connect(DB_PATH)
tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
print(f"\n── Database Validation ──")
for t in tables['name']:
    count = pd.read_sql(f"SELECT COUNT(*) as n FROM {t}", conn)['n'][0]
    print(f"   Table '{t}': {count:,} rows ✅")
conn.close()

# Also export master CSV for Power BI
df_master.to_csv('../data/telco_master_powerbi.csv', index=False)
print(f"\n✅ Power BI export saved: telco_master_powerbi.csv")
print(f"\n✅ STEP 2 COMPLETE — ETL pipeline finished")
print(f"   Ended : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("   → Run step3_sql_analysis.py next")
