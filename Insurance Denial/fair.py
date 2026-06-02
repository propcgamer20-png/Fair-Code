import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# ============================================================
# INSURANCE DENIAL BIAS AUDIT — FAIR MODEL
# Dataset: Insurance Claim Analysis: Demographic & Health
# https://www.kaggle.com/datasets/thedevastator/insurance-claim-analysis-demographic-and-health
#
# Protected attributes removed: age, gender
# Proxy variables removed:      bmi, smoker, diabetic
#
# Retained: only features that reflect documented policy
# context — not who the person is or proxies for their
# race, class, or protected status.
# ============================================================

df = pd.read_csv(Path(__file__).parent / 'insurance.csv')

# Same binarization threshold as unfair.py — valid comparison.
median_charge = df['claim'].median()
y = (df['claim'] > median_charge).astype(int)

df['age_group'] = df['age'].apply(lambda x: 'Young (<35)' if x < 35 else 'Older (35+)')

# ── THE FIX: Policy signals only ────────────────────────────
X = pd.get_dummies(df[[
    'bloodpressure', # objective clinical measurement
    'children',      # number of dependants — policy-level fact
    'region',        # geographic region — policy-level factor
    # age      removed ✓  (protected attribute)
    # gender   removed ✓  (protected attribute)
    # bmi      removed ✓  (proxy: encodes race via population BMI distributions)
    # smoker   removed ✓  (proxy: encodes income/class → race)
    # diabetic removed ✓  (proxy: diagnosis rates differ 60–100% by race)
]])

# ── TRAIN FAIR MODEL ─────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

accuracy = accuracy_score(y_test, model.predict(X_test))

# ── MEASURE FAIRNESS GAP ─────────────────────────────────────
df_test = X_test.copy()
df_test['age_group'] = df.loc[X_test.index, 'age_group'].values
df_test['gender']    = df.loc[X_test.index, 'gender'].values
df_test['prediction'] = model.predict(X_test)

age_approval    = df_test.groupby('age_group')['prediction'].mean()
gender_approval = df_test.groupby('gender')['prediction'].mean()

print("=" * 60)
print("FAIR MODEL — RESULTS")
print("=" * 60)
print(f"\nModel Accuracy: {accuracy:.2%}\n")

print("── High-Cost Claim Flag Rate by Age Group ────────────")
for group, rate in age_approval.items():
    print(f"  {group:<20} {rate:.2%}")
age_gap = abs(age_approval.iloc[0] - age_approval.iloc[1])
print(f"\n  Fairness Gap (Age):    {age_gap:.2%}")

print("\n── High-Cost Claim Flag Rate by Gender ───────────────")
for group, rate in gender_approval.items():
    print(f"  {group:<20} {rate:.2%}")
gender_gap = abs(gender_approval['male'] - gender_approval['female'])
print(f"\n  Fairness Gap (Gender): {gender_gap:.2%}")

print("\n" + "=" * 60)
print("WHAT CHANGED")
print("=" * 60)
print("""
THE FIX: Drop the protected attributes AND their proxies.

  age      → removed. Age is a protected characteristic.
              Young patients were flagged at higher rates
              not because of medical risk, but because
              age itself was a training signal.

  gender   → removed. Gender discrimination in insurance
              is illegal under the ACA. Removing it
              eliminates the channel through which the
              model learned to penalise women.

  bmi      → removed. BMI is not an independent health
              signal — it is partially a function of race,
              ethnicity, and socioeconomic status. A model
              that penalises high BMI is partially
              penalising race, regardless of whether
              "race" appears anywhere in the feature list.

  smoker   → removed. Smoking rates correlate with income
              and education. Including smoker status allows
              the model to encode class (and by extension
              racial) signal through an apparently neutral
              variable.

  diabetic → removed. Black and Hispanic Americans are
              diagnosed diabetic at 60–100% higher rates.
              Using diabetic status as a feature encodes
              racial disparities in healthcare access and
              diagnosis rates — not individual health risk.

Key Insight: Insurance AI models don't need to name race
to discriminate by race. BMI, smoking, and diabetic status
are the CustodyStatus of health insurance — clinical-
sounding features that carry protected-class signal because
of structural inequalities baked into American healthcare.
""")