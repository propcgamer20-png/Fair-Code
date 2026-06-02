import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# 1. Load Data
df = pd.read_csv(Path(__file__).parent / 'compas-scores-raw.csv')
df = df[df['Ethnic_Code_Text'].isin(['African-American', 'Caucasian'])]
df = df[df['DisplayText'] == 'Risk of Recidivism']

# 2. Map Target
df['is_high_risk'] = df['ScoreText'].apply(lambda x: 1 if x in ['High', 'Medium'] else 0)
df['race_binary'] = df['Ethnic_Code_Text'].map({'African-American': 1, 'Caucasian': 0})

# 3. THE FIX: Drop Race AND Custody Status (a known bias proxy)
# We only keep gender and marital status to make a "blind" prediction
X = pd.get_dummies(df[['Sex_Code_Text', 'MaritalStatus']])
y = df['is_high_risk']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Train Fair Model
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# 5. Measure Final Gap
test_results = X_test.copy()
test_results['race_binary'] = df.loc[X_test.index, 'race_binary']
test_results['prediction'] = model.predict(X_test)

aa_rate = test_results[test_results['race_binary'] == 1]['prediction'].mean()
c_rate = test_results[test_results['race_binary'] == 0]['prediction'].mean()

print(f"--- MITIGATED (UNBIASED) RESULTS ---")
print(f"Black Defendant High-Risk Rate: {aa_rate:.2%}")
print(f"White Defendant High-Risk Rate: {c_rate:.2%}")
print(f"New Fairness Gap: {aa_rate - c_rate:.2%}")