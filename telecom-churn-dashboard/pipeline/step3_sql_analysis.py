"""
STEP 3 — SQL DATA CLEANING & ANALYSIS
======================================
Runs SQL queries directly on the SQLite database
to validate, clean, and extract business insights.

This mirrors what a data analyst does in SQL Server
after SSIS loads data into staging tables.

Author : Haseeb Waqas
"""

import sqlite3
import pandas as pd

DB_PATH = '../data/telecom_churn.db'
SQL_DIR = '../data/'

print("=" * 60)
print("SQL DATA CLEANING & ANALYSIS — Telecom Churn")
print("=" * 60)

conn = sqlite3.connect(DB_PATH)

# ═══════════════════════════════════════════════════════════════════════════════
# SQL CLEANING QUERIES
# ═══════════════════════════════════════════════════════════════════════════════
print("\n── SQL Data Quality Checks ──")

# Q1: Check for nulls in key columns
q1 = """
SELECT
    SUM(CASE WHEN customerID   IS NULL THEN 1 ELSE 0 END) AS null_customerID,
    SUM(CASE WHEN MonthlyCharges IS NULL THEN 1 ELSE 0 END) AS null_MonthlyCharges,
    SUM(CASE WHEN Churn         IS NULL THEN 1 ELSE 0 END) AS null_Churn,
    SUM(CASE WHEN Contract      IS NULL THEN 1 ELSE 0 END) AS null_Contract,
    COUNT(*) AS total_rows
FROM fact_customers;
"""
df_q1 = pd.read_sql(q1, conn)
print("\n📋 NULL CHECK:")
print(df_q1.to_string(index=False))

# Q2: Validate MonthlyCharges range
q2 = """
SELECT
    ROUND(MIN(MonthlyCharges), 2)  AS min_charge,
    ROUND(MAX(MonthlyCharges), 2)  AS max_charge,
    ROUND(AVG(MonthlyCharges), 2)  AS avg_charge,
    SUM(CASE WHEN MonthlyCharges < 0 THEN 1 ELSE 0 END) AS negative_charges
FROM fact_customers;
"""
df_q2 = pd.read_sql(q2, conn)
print("\n📋 MONTHLY CHARGES RANGE:")
print(df_q2.to_string(index=False))

# Q3: Validate Churn values
q3 = """
SELECT Churn, COUNT(*) AS count
FROM fact_customers
GROUP BY Churn;
"""
df_q3 = pd.read_sql(q3, conn)
print("\n📋 CHURN VALUES:")
print(df_q3.to_string(index=False))

# ═══════════════════════════════════════════════════════════════════════════════
# SQL BUSINESS ANALYSIS QUERIES
# ═══════════════════════════════════════════════════════════════════════════════
print("\n── SQL Business Analysis ──")

# Q4: Overall KPIs
q4 = """
SELECT
    COUNT(*)                                    AS Total_Customers,
    SUM(Churn_Binary)                           AS Total_Churned,
    ROUND(AVG(Churn_Binary) * 100, 2)           AS Churn_Rate_Pct,
    ROUND(AVG(MonthlyCharges), 2)               AS Avg_Monthly_Charge,
    ROUND(AVG(tenure), 1)                       AS Avg_Tenure_Months,
    ROUND(SUM(TotalCharges), 0)                 AS Total_Revenue
FROM fact_customers;
"""
df_q4 = pd.read_sql(q4, conn)
print("\n📊 KPI SUMMARY:")
print(df_q4.to_string(index=False))

# Q5: Churn by Contract (key business insight)
q5 = """
SELECT
    Contract,
    COUNT(*)                              AS Total_Customers,
    SUM(Churn_Binary)                     AS Churned,
    ROUND(AVG(Churn_Binary) * 100, 2)     AS Churn_Rate_Pct,
    ROUND(AVG(MonthlyCharges), 2)         AS Avg_Monthly_Charge
FROM fact_customers
GROUP BY Contract
ORDER BY Churn_Rate_Pct DESC;
"""
df_q5 = pd.read_sql(q5, conn)
print("\n📊 CHURN BY CONTRACT:")
print(df_q5.to_string(index=False))

# Q6: Churn by Tenure Group
q6 = """
SELECT
    Tenure_Group,
    COUNT(*)                              AS Total_Customers,
    SUM(Churn_Binary)                     AS Churned,
    ROUND(AVG(Churn_Binary) * 100, 2)     AS Churn_Rate_Pct
FROM fact_customers
WHERE Tenure_Group IS NOT NULL
GROUP BY Tenure_Group
ORDER BY Churn_Rate_Pct DESC;
"""
df_q6 = pd.read_sql(q6, conn)
print("\n📊 CHURN BY TENURE GROUP:")
print(df_q6.to_string(index=False))

# Q7: Churn by Internet Service
q7 = """
SELECT
    InternetService,
    COUNT(*)                              AS Total_Customers,
    SUM(Churn_Binary)                     AS Churned,
    ROUND(AVG(Churn_Binary) * 100, 2)     AS Churn_Rate_Pct,
    ROUND(AVG(MonthlyCharges), 2)         AS Avg_Monthly_Charge
FROM fact_customers
GROUP BY InternetService
ORDER BY Churn_Rate_Pct DESC;
"""
df_q7 = pd.read_sql(q7, conn)
print("\n📊 CHURN BY INTERNET SERVICE:")
print(df_q7.to_string(index=False))

# Q8: Churn by Payment Method
q8 = """
SELECT
    PaymentMethod,
    COUNT(*)                              AS Total_Customers,
    SUM(Churn_Binary)                     AS Churned,
    ROUND(AVG(Churn_Binary) * 100, 2)     AS Churn_Rate_Pct
FROM fact_customers
GROUP BY PaymentMethod
ORDER BY Churn_Rate_Pct DESC;
"""
df_q8 = pd.read_sql(q8, conn)
print("\n📊 CHURN BY PAYMENT METHOD:")
print(df_q8.to_string(index=False))

# Q9: High-Value Churned Customers (revenue at risk)
q9 = """
SELECT
    Revenue_Segment,
    COUNT(*)                              AS Total_Customers,
    SUM(Churn_Binary)                     AS Churned,
    ROUND(AVG(Churn_Binary) * 100, 2)     AS Churn_Rate_Pct,
    ROUND(SUM(CASE WHEN Churn_Binary=1 THEN MonthlyCharges ELSE 0 END), 0)
                                          AS Monthly_Revenue_At_Risk
FROM fact_customers
GROUP BY Revenue_Segment
ORDER BY Monthly_Revenue_At_Risk DESC;
"""
df_q9 = pd.read_sql(q9, conn)
print("\n📊 REVENUE AT RISK BY SEGMENT:")
print(df_q9.to_string(index=False))

# Q10: Senior vs Non-Senior Churn
q10 = """
SELECT
    Is_Senior,
    COUNT(*)                              AS Total_Customers,
    SUM(Churn_Binary)                     AS Churned,
    ROUND(AVG(Churn_Binary) * 100, 2)     AS Churn_Rate_Pct
FROM fact_customers
GROUP BY Is_Senior;
"""
df_q10 = pd.read_sql(q10, conn)
print("\n📊 SENIOR vs NON-SENIOR CHURN:")
print(df_q10.to_string(index=False))

# ── Save all SQL results to Excel (for reference) ──────────────────────────────
with pd.ExcelWriter(f'{SQL_DIR}sql_analysis_results.xlsx', engine='openpyxl') as writer:
    df_q4.to_excel(writer, sheet_name='KPI_Summary',         index=False)
    df_q5.to_excel(writer, sheet_name='Churn_by_Contract',   index=False)
    df_q6.to_excel(writer, sheet_name='Churn_by_Tenure',     index=False)
    df_q7.to_excel(writer, sheet_name='Churn_by_Internet',   index=False)
    df_q8.to_excel(writer, sheet_name='Churn_by_Payment',    index=False)
    df_q9.to_excel(writer, sheet_name='Revenue_at_Risk',     index=False)
    df_q10.to_excel(writer, sheet_name='Senior_vs_NonSenior',index=False)

print("\n✅ SQL results exported: sql_analysis_results.xlsx (7 sheets)")
print("\n✅ STEP 3 COMPLETE — SQL analysis done")
print("   → Import telco_master_powerbi.csv into Power BI now")
conn.close()
