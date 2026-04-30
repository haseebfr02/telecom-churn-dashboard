import pandas as pd
import numpy as np

np.random.seed(42)
n = 7043

tenure = np.random.exponential(scale=30, size=n).clip(1, 72).astype(int)
monthly_charges = np.random.normal(65, 30, n).clip(18, 120).round(2)
total_charges = (tenure * monthly_charges * np.random.uniform(0.85, 1.05, n)).round(2)

contract = np.random.choice(['Month-to-month', 'One year', 'Two year'], n, p=[0.55, 0.24, 0.21])
internet_service = np.random.choice(['DSL', 'Fiber optic', 'No'], n, p=[0.34, 0.44, 0.22])
payment_method = np.random.choice(
    ['Electronic check', 'Mailed check', 'Bank transfer (automatic)', 'Credit card (automatic)'],
    n, p=[0.34, 0.23, 0.22, 0.21]
)
gender = np.random.choice(['Male', 'Female'], n)
senior_citizen = np.random.choice([0, 1], n, p=[0.84, 0.16])
partner = np.random.choice(['Yes', 'No'], n)
dependents = np.random.choice(['Yes', 'No'], n, p=[0.3, 0.7])
phone_service = np.random.choice(['Yes', 'No'], n, p=[0.9, 0.1])
multiple_lines = np.where(phone_service == 'No', 'No phone service',
                 np.random.choice(['Yes', 'No'], n))
online_security = np.where(internet_service == 'No', 'No internet service',
                  np.random.choice(['Yes', 'No'], n))
tech_support = np.where(internet_service == 'No', 'No internet service',
               np.random.choice(['Yes', 'No'], n))
streaming_tv = np.where(internet_service == 'No', 'No internet service',
               np.random.choice(['Yes', 'No'], n))
paperless_billing = np.random.choice(['Yes', 'No'], n, p=[0.59, 0.41])

churn_prob = np.full(n, 0.05)
churn_prob += np.where(contract == 'Month-to-month', 0.28, 0)
churn_prob += np.where(contract == 'One year', 0.06, 0)
churn_prob += np.where(internet_service == 'Fiber optic', 0.12, 0)
churn_prob += np.where(monthly_charges > 80, 0.10, 0)
churn_prob += np.where(tenure < 12, 0.15, 0)
churn_prob += np.where(payment_method == 'Electronic check', 0.08, 0)
churn_prob += np.where(online_security == 'No', 0.06, 0)
churn_prob += np.where(senior_citizen == 1, 0.05, 0)
churn_prob = churn_prob.clip(0, 0.85)
churn_binary = (np.random.random(n) < churn_prob).astype(int)
churn = np.where(churn_binary == 1, 'Yes', 'No')

df = pd.DataFrame({
    'customerID': [f'TELCO-{str(i).zfill(5)}' for i in range(1, n+1)],
    'gender': gender,
    'SeniorCitizen': senior_citizen,
    'Partner': partner,
    'Dependents': dependents,
    'tenure': tenure,
    'PhoneService': phone_service,
    'MultipleLines': multiple_lines,
    'InternetService': internet_service,
    'OnlineSecurity': online_security,
    'TechSupport': tech_support,
    'StreamingTV': streaming_tv,
    'Contract': contract,
    'PaperlessBilling': paperless_billing,
    'PaymentMethod': payment_method,
    'MonthlyCharges': monthly_charges,
    'TotalCharges': total_charges,
    'Churn': churn
})

df.to_csv('/home/claude/telecom-churn-dashboard/data/telco_churn.csv', index=False)
print(f"Dataset generated: {len(df)} rows")
print(f"Churn rate: {df['Churn'].value_counts(normalize=True)['Yes']:.1%}")
