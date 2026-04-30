"""
Telecom Customer Churn Analysis
================================
Author: Haseeb Waqas
Description: Full data cleaning, EDA, and export pipeline
             for Telecom Customer Churn Dashboard project.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# ── Style Config ──────────────────────────────────────────────────────────────
CHURN_NO   = '#2ECC71'   # green
CHURN_YES  = '#E74C3C'   # red
BG_COLOR   = '#F8F9FA'
GRID_COLOR = '#E0E0E0'
FONT       = 'DejaVu Sans'

plt.rcParams.update({
    'figure.facecolor': BG_COLOR,
    'axes.facecolor':   BG_COLOR,
    'axes.grid':        True,
    'grid.color':       GRID_COLOR,
    'grid.linewidth':   0.8,
    'font.family':      FONT,
    'axes.spines.top':  False,
    'axes.spines.right':False,
})

VISUALS = '../visuals/'

# ═══════════════════════════════════════════════════════════════════════════════
# 1. LOAD DATA
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("TELECOM CHURN ANALYSIS — Haseeb Waqas")
print("=" * 60)

df = pd.read_csv('../data/telco_churn.csv')
print(f"\n✅ Loaded dataset: {df.shape[0]:,} rows × {df.shape[1]} columns")

# ═══════════════════════════════════════════════════════════════════════════════
# 2. DATA CLEANING
# ═══════════════════════════════════════════════════════════════════════════════
print("\n── Data Cleaning ──")

# Fix TotalCharges stored as string (if any)
df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')

# Drop missing rows
missing = df.isnull().sum().sum()
df.dropna(inplace=True)
print(f"   Dropped {missing} missing values → {len(df):,} rows remain")

# Encode Churn as binary
df['Churn_Binary'] = df['Churn'].map({'Yes': 1, 'No': 0})

# Tenure buckets for segmentation
df['Tenure_Group'] = pd.cut(df['tenure'],
    bins=[0, 12, 24, 48, 72],
    labels=['0–12 mo', '13–24 mo', '25–48 mo', '49–72 mo']
)

# Charge tier
df['Charge_Tier'] = pd.cut(df['MonthlyCharges'],
    bins=[0, 35, 65, 90, 200],
    labels=['Low (<$35)', 'Mid ($35–65)', 'High ($65–90)', 'Premium (>$90)']
)

print(f"   Churn rate: {df['Churn_Binary'].mean():.1%}")
print(f"   Avg tenure: {df['tenure'].mean():.1f} months")
print(f"   Avg monthly charge: ${df['MonthlyCharges'].mean():.2f}")

# ═══════════════════════════════════════════════════════════════════════════════
# 3. EDA VISUALIZATIONS
# ═══════════════════════════════════════════════════════════════════════════════
print("\n── Generating Visualizations ──")

# ── 3.1 Overall Churn Distribution ───────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 5))
counts = df['Churn'].value_counts()
bars = ax.bar(['Active Customers', 'Churned Customers'],
              [counts['No'], counts['Yes']],
              color=[CHURN_NO, CHURN_YES], width=0.5, edgecolor='white', linewidth=1.5)
for bar, count in zip(bars, [counts['No'], counts['Yes']]):
    pct = count / len(df) * 100
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 40,
            f'{count:,}\n({pct:.1f}%)', ha='center', va='bottom', fontsize=12, fontweight='bold')
ax.set_title('Overall Customer Churn Distribution', fontsize=15, fontweight='bold', pad=15)
ax.set_ylabel('Number of Customers', fontsize=11)
ax.set_ylim(0, counts['No'] * 1.18)
plt.tight_layout()
plt.savefig(f'{VISUALS}01_churn_distribution.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ 01_churn_distribution.png")

# ── 3.2 Churn by Contract Type ───────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))
contract_churn = df.groupby('Contract')['Churn_Binary'].agg(['mean', 'count']).reset_index()
contract_churn['mean'] *= 100
bars = ax.bar(contract_churn['Contract'], contract_churn['mean'],
              color=[CHURN_YES, '#F39C12', CHURN_NO], width=0.5, edgecolor='white', linewidth=1.5)
for bar, (_, row) in zip(bars, contract_churn.iterrows()):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f"{row['mean']:.1f}%\n(n={row['count']:,})",
            ha='center', va='bottom', fontsize=11, fontweight='bold')
ax.set_title('Churn Rate by Contract Type', fontsize=15, fontweight='bold', pad=15)
ax.set_ylabel('Churn Rate (%)', fontsize=11)
ax.set_ylim(0, contract_churn['mean'].max() * 1.25)
plt.tight_layout()
plt.savefig(f'{VISUALS}02_churn_by_contract.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ 02_churn_by_contract.png")

# ── 3.3 Monthly Charges vs Churn ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))
churned     = df[df['Churn'] == 'Yes']['MonthlyCharges']
not_churned = df[df['Churn'] == 'No']['MonthlyCharges']
ax.hist(not_churned, bins=35, alpha=0.7, color=CHURN_NO,  label=f'Active  (avg ${not_churned.mean():.0f})')
ax.hist(churned,     bins=35, alpha=0.7, color=CHURN_YES, label=f'Churned (avg ${churned.mean():.0f})')
ax.axvline(not_churned.mean(), color=CHURN_NO,  linestyle='--', linewidth=2)
ax.axvline(churned.mean(),     color=CHURN_YES, linestyle='--', linewidth=2)
ax.set_title('Monthly Charges Distribution by Churn Status', fontsize=15, fontweight='bold', pad=15)
ax.set_xlabel('Monthly Charges ($)', fontsize=11)
ax.set_ylabel('Number of Customers', fontsize=11)
ax.legend(fontsize=11)
plt.tight_layout()
plt.savefig(f'{VISUALS}03_monthly_charges_churn.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ 03_monthly_charges_churn.png")

# ── 3.4 Tenure Distribution by Churn ─────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))
tenure_group = df.groupby(['Tenure_Group', 'Churn']).size().unstack(fill_value=0)
tenure_pct   = tenure_group.div(tenure_group.sum(axis=1), axis=0) * 100
tenure_pct[['No','Yes']].plot(kind='bar', ax=ax,
    color=[CHURN_NO, CHURN_YES], width=0.6, edgecolor='white', linewidth=1.5)
ax.set_title('Churn Rate by Customer Tenure Group', fontsize=15, fontweight='bold', pad=15)
ax.set_xlabel('Tenure Group', fontsize=11)
ax.set_ylabel('Percentage (%)', fontsize=11)
ax.set_xticklabels(tenure_pct.index, rotation=0, fontsize=10)
ax.legend(['Active', 'Churned'], fontsize=11)
plt.tight_layout()
plt.savefig(f'{VISUALS}04_tenure_churn.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ 04_tenure_churn.png")

# ── 3.5 Churn by Internet Service ────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))
internet_churn = df.groupby('InternetService')['Churn_Binary'].mean().reset_index()
internet_churn['Churn_Binary'] *= 100
colors = [CHURN_YES if v > 30 else '#F39C12' if v > 15 else CHURN_NO
          for v in internet_churn['Churn_Binary']]
bars = ax.bar(internet_churn['InternetService'], internet_churn['Churn_Binary'],
              color=colors, width=0.5, edgecolor='white', linewidth=1.5)
for bar, val in zip(bars, internet_churn['Churn_Binary']):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f'{val:.1f}%', ha='center', va='bottom', fontsize=12, fontweight='bold')
ax.set_title('Churn Rate by Internet Service Type', fontsize=15, fontweight='bold', pad=15)
ax.set_ylabel('Churn Rate (%)', fontsize=11)
ax.set_ylim(0, internet_churn['Churn_Binary'].max() * 1.2)
plt.tight_layout()
plt.savefig(f'{VISUALS}05_internet_service_churn.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ 05_internet_service_churn.png")

# ── 3.6 Churn by Payment Method ──────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5))
pay_churn = df.groupby('PaymentMethod')['Churn_Binary'].mean().sort_values(ascending=False) * 100
colors = [CHURN_YES if v > 30 else '#F39C12' if v > 20 else CHURN_NO for v in pay_churn.values]
bars = ax.barh(pay_churn.index, pay_churn.values, color=colors, edgecolor='white', linewidth=1.5)
for bar, val in zip(bars, pay_churn.values):
    ax.text(val + 0.3, bar.get_y() + bar.get_height()/2,
            f'{val:.1f}%', va='center', fontsize=11, fontweight='bold')
ax.set_title('Churn Rate by Payment Method', fontsize=15, fontweight='bold', pad=15)
ax.set_xlabel('Churn Rate (%)', fontsize=11)
ax.set_xlim(0, pay_churn.max() * 1.2)
plt.tight_layout()
plt.savefig(f'{VISUALS}06_payment_method_churn.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ 06_payment_method_churn.png")

# ── 3.7 Correlation Heatmap ───────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 6))
num_cols = ['tenure', 'MonthlyCharges', 'TotalCharges', 'Churn_Binary', 'SeniorCitizen']
corr = df[num_cols].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdYlGn',
            center=0, ax=ax, linewidths=0.5,
            cbar_kws={'shrink': 0.8},
            annot_kws={'fontsize': 11})
ax.set_title('Feature Correlation with Churn', fontsize=15, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig(f'{VISUALS}07_correlation_heatmap.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ 07_correlation_heatmap.png")

# ── 3.8 Summary Dashboard ─────────────────────────────────────────────────────
fig = plt.figure(figsize=(16, 10))
fig.patch.set_facecolor('#1A1A2E')
fig.suptitle('Telecom Customer Churn — Executive Summary Dashboard',
             fontsize=20, fontweight='bold', color='white', y=0.98)

# KPI boxes
kpis = [
    ('Total Customers', f"{len(df):,}", '#3498DB'),
    ('Churn Rate',      f"{df['Churn_Binary'].mean():.1%}", '#E74C3C'),
    ('Avg Monthly Charge', f"${df['MonthlyCharges'].mean():.0f}", '#F39C12'),
    ('Avg Tenure',      f"{df['tenure'].mean():.0f} mo", '#2ECC71'),
]
for i, (label, value, color) in enumerate(kpis):
    ax = fig.add_axes([0.03 + i*0.245, 0.80, 0.22, 0.14])
    ax.set_facecolor(color)
    ax.text(0.5, 0.62, value, ha='center', va='center', fontsize=24,
            fontweight='bold', color='white', transform=ax.transAxes)
    ax.text(0.5, 0.22, label, ha='center', va='center', fontsize=10,
            color='white', alpha=0.85, transform=ax.transAxes)
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values(): spine.set_visible(False)

# Contract churn bar
ax1 = fig.add_axes([0.04, 0.40, 0.44, 0.34])
ax1.set_facecolor('#16213E')
cc = df.groupby('Contract')['Churn_Binary'].mean() * 100
ax1.bar(cc.index, cc.values, color=[CHURN_YES, '#F39C12', CHURN_NO],
        width=0.5, edgecolor='none')
for i, (label, val) in enumerate(cc.items()):
    ax1.text(i, val + 0.5, f'{val:.1f}%', ha='center', fontsize=11,
             fontweight='bold', color='white')
ax1.set_title('Churn Rate by Contract', color='white', fontsize=12, fontweight='bold')
ax1.set_facecolor('#16213E')
ax1.tick_params(colors='white'); ax1.set_ylabel('Churn Rate (%)', color='white')
for spine in ax1.spines.values(): spine.set_color('#333366')
ax1.set_ylim(0, cc.max() * 1.25)
ax1.grid(color='#333366', linewidth=0.5)

# Tenure churn
ax2 = fig.add_axes([0.54, 0.40, 0.44, 0.34])
ax2.set_facecolor('#16213E')
tg = df.groupby('Tenure_Group', observed=True)['Churn_Binary'].mean() * 100
ax2.bar(tg.index.astype(str), tg.values,
        color=[CHURN_YES, '#F39C12', '#F39C12', CHURN_NO],
        width=0.5, edgecolor='none')
for i, val in enumerate(tg.values):
    ax2.text(i, val + 0.5, f'{val:.1f}%', ha='center', fontsize=11,
             fontweight='bold', color='white')
ax2.set_title('Churn Rate by Tenure Group', color='white', fontsize=12, fontweight='bold')
ax2.tick_params(colors='white'); ax2.set_ylabel('Churn Rate (%)', color='white')
for spine in ax2.spines.values(): spine.set_color('#333366')
ax2.set_ylim(0, tg.max() * 1.25)
ax2.grid(color='#333366', linewidth=0.5)

# Recommendations text box
ax3 = fig.add_axes([0.04, 0.02, 0.92, 0.32])
ax3.set_facecolor('#16213E')
ax3.set_xticks([]); ax3.set_yticks([])
for spine in ax3.spines.values(): spine.set_color('#333366')
recs = [
    "📌 REC 1: Month-to-month customers churn at 3x the rate — offer loyalty discounts at the 3-month mark to drive annual upgrades.",
    "📌 REC 2: New customers (0–12 months) have highest churn risk — implement onboarding check-ins and first-year retention programs.",
    "📌 REC 3: Fiber optic users churn more despite paying premium — review service quality and pricing competitiveness for this segment.",
    "📌 REC 4: Electronic check users show highest churn — incentivize auto-pay enrollment with a monthly bill discount.",
]
ax3.text(0.5, 0.92, '💡 Business Recommendations', ha='center', va='top',
         fontsize=13, fontweight='bold', color='#F39C12', transform=ax3.transAxes)
for i, rec in enumerate(recs):
    ax3.text(0.02, 0.75 - i*0.20, rec, ha='left', va='top',
             fontsize=10, color='white', transform=ax3.transAxes, wrap=True)

plt.savefig(f'{VISUALS}00_executive_dashboard.png', dpi=150, bbox_inches='tight',
            facecolor='#1A1A2E')
plt.close()
print("   ✅ 00_executive_dashboard.png")

# ═══════════════════════════════════════════════════════════════════════════════
# 4. EXPORT CLEANED DATA FOR TABLEAU
# ═══════════════════════════════════════════════════════════════════════════════
df.to_csv('../data/telco_churn_cleaned.csv', index=False)
print(f"\n✅ Cleaned CSV exported: {len(df):,} rows, {df.shape[1]} columns")

# ── Summary Stats ─────────────────────────────────────────────────────────────
print("\n── Key Findings ──")
print(f"   Overall churn rate          : {df['Churn_Binary'].mean():.1%}")
month_churn = df[df['Contract']=='Month-to-month']['Churn_Binary'].mean()
annual_churn = df[df['Contract']=='Two year']['Churn_Binary'].mean()
print(f"   Month-to-month churn rate   : {month_churn:.1%}")
print(f"   Two-year contract churn rate: {annual_churn:.1%}")
print(f"   Ratio (M2M vs 2-yr)         : {month_churn/annual_churn:.1f}x higher")
avg_churned = df[df['Churn']=='Yes']['MonthlyCharges'].mean()
avg_active  = df[df['Churn']=='No']['MonthlyCharges'].mean()
print(f"   Avg charge — churned        : ${avg_churned:.2f}")
print(f"   Avg charge — active         : ${avg_active:.2f}")
new_churn = df[df['Tenure_Group']=='0–12 mo']['Churn_Binary'].mean()
print(f"   New customer churn (0-12mo) : {new_churn:.1%}")
print("\n✅ All done! Open visuals/ to see your charts.")
print("✅ Import data/telco_churn_cleaned.csv into Tableau.")
