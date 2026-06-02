import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# ============================================================
# INSURANCE DENIAL BIAS AUDIT — BIASED MODEL
# Dataset: Insurance Claim Analysis: Demographic & Health
# https://www.kaggle.com/datasets/thedevastator/insurance-claim-analysis-demographic-and-health
#
# Protected attributes included: age, gender
# Proxy variables included:      bmi, smoker, diabetic
#
# BMI is a documented proxy for race — Black and Hispanic
# Americans are flagged as "obese" at higher rates due to
# population-level differences, not individual health risk.
# Smoker status correlates with income and education, which
# themselves correlate with race and class.
# Diabetic status correlates with race (Black and Hispanic
# Americans are diagnosed at 60–100% higher rates), encoding
# racial signal through an apparently clinical variable.
# ============================================================

df = pd.read_csv(Path(__file__).parent / 'insurance.csv')

# Binarize continuous claim charges at the median.
# Above median = high-cost claim (flagged for denial/review).
# At or below  = approved claim.
# Same threshold used in fair.py for a valid comparison.
median_charge = df['claim'].median()
y = (df['claim'] > median_charge).astype(int)

# Define age groups for fairness measurement
df['age_group'] = df['age'].apply(lambda x: 'Young (<35)' if x < 35 else 'Older (35+)')

# ── BIASED FEATURES ─────────────────────────────────────────
# age and gender are protected attributes.
# bmi      proxy: population BMI distributions differ by race;
#                 penalising high BMI penalises race.
# smoker   proxy: smoking rates correlate with poverty → race/class.
# diabetic proxy: Black and Hispanic Americans are diagnosed
#                 diabetic at 60–100% higher rates, encoding
#                 racial signal through a clinical label.
X = pd.get_dummies(df[[
    'age',          # protected attribute
    'gender',       # protected attribute
    'bmi',          # proxy: correlated with race via population BMI distributions
    'bloodpressure',
    'diabetic',     # proxy: diagnosis rates differ significantly by race
    'children',
    'smoker',       # proxy: correlated with income → race/class
    'region',
]])

# ── PROXY VARIABLE ANALYSIS ──────────────────────────────────
print("=" * 60)
print("PROXY VARIABLE ANALYSIS")
print("=" * 60)
print("\nBMI distribution by age group:")
print(df.groupby('age_group')['bmi'].mean().round(2))

smoker_age = pd.crosstab(df['smoker'], df['age_group'], normalize='columns').round(3)
print("\nSmoker rates by age group:")
print(smoker_age)

diabetic_age = pd.crosstab(df['diabetic'], df['age_group'], normalize='columns').round(3)
print("\nDiabetic rates by age group:")
print(diabetic_age)
print()

# ── TRAIN BIASED MODEL ───────────────────────────────────────
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
print("BIASED MODEL — RESULTS")
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
print("WHAT'S WRONG")
print("=" * 60)
print("""
This model includes age and gender as direct inputs — protected
attributes under the ACA and anti-discrimination law.

It also includes three proxy variables:

  BMI      → population-level BMI distributions differ by
              race/ethnicity. Flagging high BMI as a risk
              factor disproportionately penalises Black and
              Hispanic patients independent of actual health
              outcomes.

  Smoker   → smoking rates are inversely correlated with
              income and education. Income and education are
              themselves correlated with race and class.
              'Smoker' smuggles socioeconomic signal —
              and therefore racial signal — back into the
              model even if race is never named.

  Diabetic → Black and Hispanic Americans are diagnosed with
              diabetes at 60–100% higher rates than white
              Americans. A model that treats diabetic status
              as a risk factor is partially encoding race
              through a clinical label.

Run fair.py to see the fix.
""")