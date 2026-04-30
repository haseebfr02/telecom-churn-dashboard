"""
STEP 1 — DATA SOURCING
======================
Simulates two real-world data sources:
  Source A : Excel file  (customer demographics)
  Source B : API response (billing & contract data)

In a real project:
  - Source A would be an Excel export from CRM
  - Source B would be a REST API call to billing system

Author : Haseeb Waqas
"""

import pandas as pd
import numpy as np
import json
import os

np.random.seed(42)

RAW_DIR = '../data/raw/'
os.makedirs(RAW_DIR, exist_ok=True)

# ── Load base dataset ─────────────────────────────────────────────────────────
df = pd.read_csv('../data/telco_churn.csv')
print(f"✅ Base dataset loaded: {df.shape[0]:,} rows")

# ═══════════════════════════════════════════════════════════════════════════════
# SOURCE A — Excel File (Customer Demographics)
# Simulates an Excel export from a CRM system
# ═══════════════════════════════════════════════════════════════════════════════
demo_cols = ['customerID', 'gender', 'SeniorCitizen', 'Partner',
             'Dependents', 'tenure', 'PhoneService', 'MultipleLines']

df_demographics = df[demo_cols].copy()

# Introduce realistic messiness (as real Excel exports have)
# 1. Random casing issues
df_demographics['gender'] = df_demographics['gender'].apply(
    lambda x: x.upper() if np.random.random() < 0.15 else x
)
# 2. Some blank Partner values
mask = np.random.random(len(df_demographics)) < 0.02
df_demographics.loc[mask, 'Partner'] = np.nan

# 3. Duplicate a few rows (common in Excel exports)
dupes = df_demographics.sample(12, random_state=1)
df_demographics = pd.concat([df_demographics, dupes], ignore_index=True)

df_demographics.to_excel(f'{RAW_DIR}source_a_demographics.xlsx', index=False)
print(f"✅ Source A saved: source_a_demographics.xlsx  ({len(df_demographics):,} rows, includes duplicates & nulls)")

# ═══════════════════════════════════════════════════════════════════════════════
# SOURCE B — API Response (Billing & Contract Data)
# Simulates a JSON response from a billing REST API
# ═══════════════════════════════════════════════════════════════════════════════
billing_cols = ['customerID', 'InternetService', 'OnlineSecurity', 'TechSupport',
                'StreamingTV', 'Contract', 'PaperlessBilling',
                'PaymentMethod', 'MonthlyCharges', 'TotalCharges', 'Churn']

df_billing = df[billing_cols].copy()

# Introduce messiness
# 1. TotalCharges as string (common API issue)
df_billing['TotalCharges'] = df_billing['TotalCharges'].astype(str)
# 2. Inject a few blank TotalCharges
mask2 = np.random.random(len(df_billing)) < 0.015
df_billing.loc[mask2, 'TotalCharges'] = ' '
# 3. MonthlyCharges with some outliers
mask3 = np.random.random(len(df_billing)) < 0.005
df_billing.loc[mask3, 'MonthlyCharges'] = -1  # bad data

# Save as JSON (API simulation)
records = df_billing.to_dict(orient='records')
with open(f'{RAW_DIR}source_b_billing_api.json', 'w') as f:
    json.dump({"status": "success", "count": len(records), "data": records}, f, indent=2)

print(f"✅ Source B saved: source_b_billing_api.json   ({len(records):,} records, includes data quality issues)")

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n── Source Summary ──")
print(f"   Source A (Excel) : {len(df_demographics):,} rows | {len(demo_cols)} columns | demographics")
print(f"   Source B (API)   : {len(records):,} rows | {len(billing_cols)} columns | billing")
print("\n✅ STEP 1 COMPLETE — Raw sources ready for ETL pipeline")
print("   → Run step2_etl_pipeline.py next")
