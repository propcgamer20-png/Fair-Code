import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# 1. Load your uploaded file
df = pd.read_csv(Path(__file__).parent / 'compas-scores-raw.csv')

# 2. Filter for clear comparison (African-American vs Caucasian) 
# and focus on 'Risk of Recidivism'
df = df[df['Ethnic_Code_Text'].isin(['African-American', 'Caucasian'])]
df = df[df['DisplayText'] == 'Risk of Recidivism']

# 3. Create Target: 1 for High/Medium Risk, 0 for Low
df['is_high_risk'] = df['ScoreText'].apply(lambda x: 1 if x in ['High', 'Medium'] else 0)
df['race_binary'] = df['Ethnic_Code_Text'].map({'African-American': 1, 'Caucasian': 0})

# 4. Prepare Features (Include Race)
X = pd.get_dummies(df[['Sex_Code_Text', 'race_binary', 'CustodyStatus', 'MaritalStatus']])
y = df['is_high_risk']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 5. Train and Check Gap
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

test_results = X_test.copy()
test_results['prediction'] = model.predict(X_test)

aa_rate = test_results[test_results['race_binary'] == 1]['prediction'].mean()
c_rate = test_results[test_results['race_binary'] == 0]['prediction'].mean()

print(f"--- BIASED MODEL RESULTS ---")
print(f"Black Defendant High-Risk Rate: {aa_rate:.2%}")
print(f"White Defendant High-Risk Rate: {c_rate:.2%}")
print(f"Fairness Gap: {aa_rate - c_rate:.2%}")