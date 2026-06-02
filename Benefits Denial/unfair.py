import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

# ============================================================
# BENEFITS DENIAL BIAS AUDIT — BIASED MODEL
# Dataset: UCI Adult Census Income
# https://www.kaggle.com/datasets/wenruliu/adult-income-dataset
#
# Framing: income threshold (>50K) used as eligibility proxy —
# the same logic automated welfare and benefits systems use to
# screen applicants via income/means tests.
#
# Protected attributes included: sex, race, native.country, age
# Proxy variables included:
#   relationship  → encodes sex: 'Husband' is 0% female,
#                   'Wife' is 0% male. Dropping sex while
#                   keeping relationship achieves nothing.
#   marital.status → Male applicants are Married-civ-spouse
#                   at 61.1% vs 15.4% for female applicants.
#                   The model reconstructs sex through marriage.
#   hours.per.week → Women average 36.4 hrs/wk vs 42.4 for men
#                   due to caregiving burdens, not productivity.
#                   Penalising low hours penalises gender roles.
#   occupation    → Racial occupational segregation: Black and
#                   Native applicants are in high-skill roles
#                   at ~15% vs 26% for White applicants.
#                   Occupation encodes race via labour market bias.
# ============================================================

df = pd.read_csv(Path(__file__).parent / 'adult.csv')

# Target: 1 = income >50K (above means-test threshold → likely ineligible)
#         0 = income <=50K (below threshold → eligible for benefits)
# In a benefits system: model flags 1 as "ineligible", 0 as "eligible"
df['target'] = (df['income'] == '>50K').astype(int)

# Protected attribute flags for fairness measurement
df['is_female']  = (df['sex'] == 'Female').astype(int)
df['is_foreign'] = (df['native.country'] != 'United-States').astype(int)
df['is_elderly'] = (df['age'] >= 55).astype(int)
df['is_minority'] = (~df['race'].isin(['White', 'Asian-Pac-Islander'])).astype(int)

# ── PROXY VARIABLE ANALYSIS ──────────────────────────────────
print("=" * 62)
print("PROXY VARIABLE ANALYSIS")
print("=" * 62)

print("\nrelationship distribution by sex:")
rel_sex = pd.crosstab(df['relationship'], df['sex'], normalize='columns').round(3)
print(rel_sex)
print("  → 'Husband' is 0% female; 'Wife' is 0% male.")
print("    relationship is sex encoded as a family role.")

print("\nMarried-civ-spouse rate by sex:")
married = df.groupby('sex').apply(
    lambda x: (x['marital.status'] == 'Married-civ-spouse').mean()
).round(3)
print(f"  Female: {married['Female']:.1%}")
print(f"  Male:   {married['Male']:.1%}")
print("  → marital.status reconstructs sex through spousal status.")

print("\nhours.per.week mean by sex:")
hrs = df.groupby('sex')['hours.per.week'].mean().round(1)
print(f"  Female: {hrs['Female']} hrs/wk")
print(f"  Male:   {hrs['Male']} hrs/wk")
print("  → Gap reflects caregiving burden, not work capacity.")

print("\nPct in high-skill occupations by race:")
df['high_occ'] = df['occupation'].isin(['Prof-specialty', 'Exec-managerial']).astype(int)
occ_race = df.groupby('race')['high_occ'].mean().round(3)
for r, v in occ_race.items():
    print(f"  {r:<25} {v:.1%}")
print("  → Occupational segregation encodes race via labour market.")
print()

# Encode categoricals
cat_cols = [
    'workclass', 'education', 'marital.status', 'occupation',
    'relationship', 'race', 'sex', 'native.country'
]
le = LabelEncoder()
df_enc = df.copy()
for col in cat_cols:
    df_enc[col] = le.fit_transform(df_enc[col].astype(str))

# ── FEATURES — BIASED (includes protected attrs + proxies) ───
features = [
    'age',             # protected attribute ✗
    'workclass',
    'fnlwgt',          # census weight — no causal link to eligibility
    'education',
    'education.num',
    'marital.status',  # proxy: encodes sex via spousal status ✗
    'occupation',      # proxy: encodes race via occupational segregation ✗
    'relationship',    # proxy: near-perfect sex encoding ✗
    'race',            # protected attribute ✗
    'sex',             # protected attribute ✗
    'capital.gain',
    'capital.loss',
    'hours.per.week',  # proxy: encodes sex via caregiving gap ✗
    'native.country',  # protected attribute (national origin) ✗
]

X = df_enc[features]
y = df_enc['target']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

accuracy = accuracy_score(y_test, model.predict(X_test))

# ── MEASURE FAIRNESS GAPS ────────────────────────────────────
results = X_test.copy()
results['pred']       = model.predict(X_test)
results['is_female']  = df.loc[X_test.index, 'is_female'].values
results['is_foreign'] = df.loc[X_test.index, 'is_foreign'].values
results['is_elderly'] = df.loc[X_test.index, 'is_elderly'].values
results['is_minority'] = df.loc[X_test.index, 'is_minority'].values

# In a benefits context: pred=1 means "flagged as ineligible (high income)"
# Fairness gap = how much MORE often a group is flagged ineligible
sex_flag    = results.groupby('is_female')['pred'].mean()
geo_flag    = results.groupby('is_foreign')['pred'].mean()
age_flag    = results.groupby('is_elderly')['pred'].mean()
race_flag   = results.groupby('is_minority')['pred'].mean()

print("=" * 62)
print("BIASED MODEL — RESULTS")
print("=" * 62)
print(f"\nModel Accuracy: {accuracy:.2%}\n")

print("── Ineligibility Flag Rate by Sex ───────────────────────")
print(f"  Male applicants    : {sex_flag[0]:.2%} flagged ineligible")
print(f"  Female applicants  : {sex_flag[1]:.2%} flagged ineligible")
sex_gap = (sex_flag[0] - sex_flag[1]) * 100
print(f"\n  Fairness Gap (Sex): {sex_gap:.2f}%")

print("\n── Ineligibility Flag Rate by National Origin ───────────")
print(f"  US-born            : {geo_flag[0]:.2%} flagged ineligible")
print(f"  Foreign-born       : {geo_flag[1]:.2%} flagged ineligible")
geo_gap = (geo_flag[0] - geo_flag[1]) * 100
print(f"\n  Fairness Gap (Origin): {geo_gap:.2f}%")

print("\n── Ineligibility Flag Rate by Age ───────────────────────")
print(f"  Under 55           : {age_flag[0]:.2%} flagged ineligible")
print(f"  55+ (elderly)      : {age_flag[1]:.2%} flagged ineligible")
age_gap = (age_flag[0] - age_flag[1]) * 100
print(f"\n  Fairness Gap (Age): {age_gap:.2f}%")

print("\n── Ineligibility Flag Rate by Race ──────────────────────")
print(f"  White/Asian-PI     : {race_flag[0]:.2%} flagged ineligible")
print(f"  Other minorities   : {race_flag[1]:.2%} flagged ineligible")
race_gap = (race_flag[0] - race_flag[1]) * 100
print(f"\n  Fairness Gap (Race): {race_gap:.2f}%")

print("\n" + "=" * 62)
print("WHAT'S WRONG")
print("=" * 62)
print("""
This model includes sex, race, native.country, and age as direct
inputs — all protected attributes under Title VII, the Age
Discrimination Act, and equal-protection principles.

It also includes four proxy variables:

  relationship  → 'Husband' is assigned to 0% of female applicants
                  and 'Wife' to 0% of male applicants. This feature
                  is sex with a different label. Removing sex while
                  keeping relationship achieves precisely nothing.

  marital.status → Male applicants appear as 'Married-civ-spouse'
                  at 61% vs 15% for female applicants. The model
                  learns to reconstruct sex through the marriage
                  column, penalising unmarried women who don't fit
                  the spousal-dependent pattern the data encodes.

  hours.per.week → Women in this dataset average 36 hrs/wk vs 42
                  for men — a gap driven by unpaid caregiving
                  responsibilities, not ability or productivity.
                  A model that treats lower hours as an eligibility
                  signal is penalising the gender pay gap, not
                  measuring economic need.

  occupation    → Racial occupational segregation means Black and
                  Native applicants appear in high-skill roles at
                  half the rate of White applicants. Including
                  occupation lets the model encode race through
                  a labour-market variable that looks purely
                  economic.

Run fair.py to see the fix.
""")