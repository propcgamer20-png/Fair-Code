# Fair Code — Algorithmic Bias Detection & Mitigation

> *AI systems are making decisions about your freedom, your job, and your healthcare. This project proves the bias is real — and shows exactly how to fix it.*

**by Yash Kewlani · [@thefaircodeproject](https://instagram.com/thefaircodeproject)**

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat-square&logo=python)
![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-orange?style=flat-square&logo=scikit-learn)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)
![Contributions Welcome](https://img.shields.io/badge/Contributions-Welcome-blueviolet?style=flat-square)

---

## What This Is

Fair Code is an ongoing research and engineering project that exposes bias in real-world AI systems and demonstrates concrete mitigation strategies. Every audit follows the same pipeline:

**train a biased model → measure the fairness gap → engineer a fair model → measure again**

No theory. No hand-waving. Just data, code, and results.

---

## Results at a Glance

| Project | Bias Type | Protected Attribute | Gap Before | Gap After | Reduction |
|---|---|---|---|---|---|
| [COMPAS](#01--compas--criminal-justice-bias) | Racial | Race + Custody Status (proxy) | 86.77% | 15.69% | **71%** |
| [AI Fair Recruitment](#02--ai-fair-recruitment--hiring-bias) | Gender | Gender + Age | 4.51% | 0.12% | **97.3%** |
| [German Credit Lending](#03--german-credit-lending--lending-bias) | Age | Age + Employment Tenure (proxy) | 7.16% | 1.89% | **73.6%** |
| [Insurance Denial](#04--insurance-denial--healthcare-bias) | Age + Gender | Age + Gender + BMI + Smoker + Diabetic (proxies) | Age: 7.93% / Gender: 5.44% | Age: 3.18% / Gender: 1.54% | **Age: 60% / Gender: 72%** |

---

## Repository Structure

```
Fair-Code/
│
├── COMPAS/
│   ├── unfair.py                  # Biased model (race + custody status included)
│   ├── fair.py                    # Mitigated model (race + proxy removed)
│   ├── compas-scores-raw.csv      # ProPublica COMPAS dataset
│   ├── unfair.png                 # Terminal output — biased results
│   └── fair.png                   # Terminal output — mitigated results
│
├── AI Fair Recruitment/
│   ├── unfair.py                  # Biased model (gender + age included)
│   ├── fair.py                    # Mitigated model (merit only)
│   ├── AI_Fair_Recruitment_Dataset.csv
│   ├── unfair.png                 # Terminal output — biased results
│   └── fair.png                   # Terminal output — mitigated results
│
├── German Credit Lending/
│   ├── unfair.py                  # Biased model (age + employment tenure included)
│   ├── fair.py                    # Mitigated model (financial signals only)
│   ├── credit_customers.csv       # UCI German Credit dataset
│   ├── unfair.png                 # Terminal output — biased results
│   └── fair.png                   # Terminal output — mitigated results
│
├── Insurance Denial/
│   ├── unfair.py                  # Biased model (age + gender + BMI + smoker + diabetic)
│   ├── fair.py                    # Mitigated model (policy signals only)
│   ├── insurance.csv              # Kaggle Insurance Claim dataset (1,340 records)
│   ├── unfair.png                 # Terminal output — biased results
│   └── fair.png                   # Terminal output — mitigated results
│
├── explainers/
│   ├── proxy-variables.md         # What is a proxy variable? (concept + detection code)
│   ├── sampling-bias.md           # What is sampling bias? (concept + simulation + mitigation)
│   └── shap-values.md             # What are SHAP values? (explainability + bias auditing)
│
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── index.html                     # Project website
└── requirements.txt
```

---

## Projects

### 01 · COMPAS — Criminal Justice Bias

> *"A real algorithm used in US courtrooms flags Black defendants as high-risk at 87%. White defendants? 0.4%. Same system. Different outcomes."*

**Dataset:** `compas-scores-raw.csv` — ProPublica's public COMPAS dataset (70,000+ records)

COMPAS (Correctional Offender Management Profiling for Alternative Sanctions) is deployed across 46 US states to predict whether a defendant will reoffend. Judges use its scores to make bail, sentencing, and parole decisions. More than 1 million people are assessed by COMPAS-style tools annually. Zero states require it to be audited for bias.

#### The Problem — `unfair.py`

Trained with race and custody status as features — inputs that COMPAS-style systems actually use in production.

| Group | High-Risk Flag Rate |
|---|---|
| Black Defendants | 87.16% |
| White Defendants | 0.40% |
| **Fairness Gap** | **86.77%** |

#### The Fix — `fair.py`

Dropped race directly, and `CustodyStatus` as a known proxy variable — a correlated feature that smuggles racial signal back in even after the race column is removed.

```python
# THE FIX: Drop race + proxy variables
X = pd.get_dummies(df[[
    'Sex_Code_Text',
    'MaritalStatus'
    # Race removed ✓
    # CustodyStatus removed ✓ (proxy for race due to over-policing)
]])
```

| Group | High-Risk Flag Rate |
|---|---|
| Black Defendants | 84.71% |
| White Defendants | 69.02% |
| **New Fairness Gap** | **15.69%** |

**Result: 71% reduction in the fairness gap.**

**Key Insight:** Removing race alone isn't enough. Proxy variables like custody status carry the same racial signal because of historical over-policing of Black communities. Both the protected attribute and its proxies must be removed.

---

### 02 · AI Fair Recruitment — Hiring Bias

> *"Women were hired 20.9% less than equally qualified men. The algorithm wasn't told to discriminate. It learned to."*

**Dataset:** `AI_Fair_Recruitment_Dataset.csv` — Recruitment dataset with gender, age, experience, and technical test scores

#### The Problem — `unfair.py`

Biased model trained with gender and age alongside merit-based inputs.

| Group | Hire Rate |
|---|---|
| Men | 21.62% |
| Women | 17.10% |
| **Fairness Gap** | **4.51%** |

Women were hired ~21% less than men with identical experience and test scores.

#### The Fix — `fair.py`

Dropped gender and age entirely. Retained only merit-based features: experience years and technical test score.

```python
# THE FIX: Merit only
X = df[['experience_years', 'test_score']]
# gender removed ✓
# age removed ✓
```

| Group | Hire Rate |
|---|---|
| Men | 11.48% |
| Women | 11.35% |
| **New Fairness Gap** | **0.12%** |

**Result: 97.3% reduction in the fairness gap.**

**Key Insight:** The model was never explicitly told to discriminate by gender. It inferred a gender penalty from historical hiring patterns in the training data — patterns reflecting human bias, not merit. Restricting inputs to demonstrated ability eliminates the channel through which that bias flows.

---

### 03 · German Credit Lending — Lending Bias

> *"A credit scoring model rates young applicants as bad credit risks at 6.39 percentage points higher than older applicants with identical financial profiles. The algorithm doesn't know it's discriminating. It learned age from job tenure."*

**Dataset:** `credit_customers.csv` — UCI Statlog German Credit dataset (1,000 records). [Kaggle source](https://www.kaggle.com/datasets/ppb00x/credit-risk-customers) — public domain, no login required.

Age discrimination in lending is documented across financial systems worldwide. Young borrowers face higher rejection rates not because of creditworthiness, but because the features used to measure it — employment tenure, account history, savings — are structurally correlated with age.

#### The Problem — `unfair.py`

Biased model trained with `age` and `employment` (tenure) as features.

| Group | Good Credit Rate |
|---|---|
| Older Applicants (30+) | 83.97% |
| Young Applicants (<30) | 76.81% |
| **Fairness Gap** | **7.16%** |

#### Proxy Variable: `employment` (tenure)

```python
print(pd.crosstab(df['employment'], df['is_young'], normalize='columns').round(3))

# Result:
# is_young          0      1
# employment
# <1yr           0.113  0.272   ← young applicants have short tenure at 2.4x the rate
# >=7yr          0.359  0.073   ← older applicants have long tenure at 4.9x the rate
```

Employment tenure is not an independent signal — it is structurally determined by age. A 24-year-old cannot have 10 years of employment history.

#### The Fix — `fair.py`

Dropped `age` and `employment`. Retained only objective financial signals.

| Group | Good Credit Rate |
|---|---|
| Older Applicants (30+) | 80.15% |
| Young Applicants (<30) | 78.26% |
| **New Fairness Gap** | **1.89%** |

**Result: 73.6% reduction in the fairness gap.**

**Key Insight:** Employment tenure looks like a legitimate financial signal, and in isolation it is. But it's also a near-perfect proxy for age. A model that penalizes short tenure is partially penalizing youth, regardless of whether the word "age" appears anywhere in the feature list.

---

### 04 · Insurance Denial — Healthcare Bias

> *"An insurance AI flags older patients for high-cost claims at 7.93 percentage points higher than younger patients, and flags women at 5.44 percentage points higher than men — using BMI, smoking status, and diabetic status as proxies for race and class."*

**Dataset:** `insurance.csv` — Insurance Claim Analysis: Demographic & Health  
[Kaggle: thedevastator/insurance-claim-analysis-demographic-and-health](https://www.kaggle.com/datasets/thedevastator/insurance-claim-analysis-demographic-and-health) — 1,340 records.

#### The Problem — `unfair.py`

| Group | High-Cost Claim Flag Rate |
|---|---|
| Older (35+) | 44.59% |
| Young (<35) | 36.67% |
| **Fairness Gap (Age)** | **7.93%** |

| Group | High-Cost Claim Flag Rate |
|---|---|
| Female | 43.85% |
| Male | 38.41% |
| **Fairness Gap (Gender)** | **5.44%** |

#### The Fix — `fair.py`

Dropped `age`, `gender`, `bmi`, `smoker`, and `diabetic`. Retained only objective policy-level signals: `bloodpressure`, `children`, `region`.

| Group | High-Cost Claim Flag Rate |
|---|---|
| Older (35+) | 50.68% |
| Young (<35) | 47.50% |
| **New Fairness Gap (Age)** | **3.18%** |

| Group | High-Cost Claim Flag Rate |
|---|---|
| Female | 48.46% |
| Male | 50.00% |
| **New Fairness Gap (Gender)** | **1.54%** |

**Result: 60% reduction in age gap. 72% reduction in gender gap.**

**Key Insight:** Insurance AI models don't need to name race to discriminate by race. BMI, smoking, and diabetic status are the `CustodyStatus` of health insurance — clinical-sounding features that carry protected-class signal because of structural inequalities baked into American healthcare.

---

## Explainers

| Explainer | Concept |
|---|---|
| [What is a Proxy Variable?](explainers/proxy-variables.md) | Why AI stays biased even after you remove race from the data |
| [What is Sampling Bias?](explainers/sampling-bias.md) | Why your AI works great in the lab and fails on the people who need it most |
| [What Are SHAP Values?](explainers/shap-values.md) | How to see exactly what drove an AI decision — and use that to catch bias |
| Equalized Odds | Fairness metric requiring equal TPR and FPR across groups | explainers/equalized-odds.md |
| Coming soon | What is demographic parity? |
| Coming soon | Why fairness metrics conflict with each other |

---

## Methodology

All projects use the same bias detection and mitigation pipeline:

```
1. Load dataset
2. Train biased model (protected attributes included)
3. Measure fairness gap across demographic groups
4. Identify proxy variables via correlation analysis
5. Remove protected attributes + known proxy variables
6. Retrain fair model (merit features only)
7. Measure fairness gap again
8. Compare
```

**Model:** Random Forest Classifier (`sklearn.ensemble.RandomForestClassifier`)  
**Split:** 80/20 train/test, `random_state=42`  
**Fairness Metric:** Demographic Parity — difference in positive prediction rates across groups  
**Mitigation Strategy:** Pre-processing attribute dropping (protected attributes + proxy variables)

---

## Why This Matters

- **87%** of companies use AI to screen job applicants before a human sees a resume
- **46** US states have used algorithmic risk tools in criminal sentencing
- **1M+** people are assessed by COMPAS-style tools annually
- **0** states require the algorithm to be audited for bias

These aren't edge cases or hypotheticals. Algorithms like COMPAS are deployed in courtrooms today. Hiring AIs filter your resume before a human ever reads it. Credit scoring models penalize young borrowers for not having lived long enough to build tenure. The bias in these systems is documented, measurable — and fixable.

---

## Getting Started

```bash
git clone https://github.com/yakew7/Fair-Code.git
cd Fair-Code
pip install -r requirements.txt
```

**Run the COMPAS project:**
```bash
cd COMPAS
python unfair.py   # See the bias
python fair.py     # See the fix
```

**Run the recruitment project:**
```bash
cd "AI Fair Recruitment"
python unfair.py
python fair.py
```

**Run the German Credit project:**
```bash
cd "German Credit Lending"
python unfair.py
python fair.py
```

**Run the Insurance Denial project:**
```bash
cd "Insurance Denial"
python unfair.py
python fair.py
```

---

## Tech Stack

| Component | Details |
|---|---|
| Language | Python 3 |
| Libraries | `pandas`, `scikit-learn` |
| Datasets | ProPublica COMPAS (public domain), AI Fair Recruitment (Kaggle), UCI German Credit / Statlog (Kaggle), Insurance Claims (Kaggle) |

---

## What's Next

- [x] COMPAS Criminal Justice Bias
- [x] AI Fair Recruitment Bias
- [x] German Credit Lending Bias
- [x] Insurance Denial — Healthcare Bias
- [x] Explainer: Proxy Variables
- [x] Explainer: Sampling Bias
- [x] Explainer: SHAP Values
- [ ] Facial recognition accuracy gaps (MIT Gender Shades methodology)
- [ ] HMDA mortgage lending bias
- [ ] LLM bias audit
- [ ] Fairness audit web dashboard

Want to contribute an audit or explainer? See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Connect

Follow the project on Instagram: **[@thefaircodeproject](https://instagram.com/thefaircodeproject)**  
Data. Code. Accountability. One post at a time.

---

*All datasets used in this project are publicly available. Fair Code is for educational and awareness purposes.*
