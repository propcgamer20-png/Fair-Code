import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# 1. Load the dataset
df = pd.read_csv('Ai Fair recrutment Dataset/AI_Fair_Recruitment_Dataset.csv')

# Drop missing metrics safely
df = df.dropna(subset=['Hiring_Decision', 'Gender', 'Age', 'Experience_Years', 'Technical_Test_Score'])
y = df['Hiring_Decision']

# 2. THE FIX: Train ONLY on merit-based columns (No gender, no age)
fair_features = ['Experience_Years', 'Technical_Test_Score']
X = pd.get_dummies(df[fair_features], drop_first=True)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Train Fair Model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 4. Measure Final Gap (Bring back gender data safely for metric tracking)
test_results = X_test.copy()
test_results['prediction'] = model.predict(X_test)

# Convert gender to dummy variables for the test set index only
df_gender = pd.get_dummies(df.loc[X_test.index, 'Gender'], drop_first=True)

# Select exactly ONE column name from the generated gender columns
male_col = df_gender.columns[0]
test_results[male_col] = df_gender[male_col]  # Fixed: Only passing a single column series

male_hire_rate = test_results[test_results[male_col] == 1]['prediction'].mean()
female_hire_rate = test_results[test_results[male_col] == 0]['prediction'].mean()

print("=" * 40)
print("--- MITIGATED MODEL OUTPUT (fair.jpg) ---")
print(f"Male Candidate Hire Rate: {male_hire_rate:.2%}")
print(f"Female Candidate Hire Rate: {female_hire_rate:.2%}")
print(f"New Fairness Gap: {abs(male_hire_rate - female_hire_rate):.2%}")
print("=" * 40)