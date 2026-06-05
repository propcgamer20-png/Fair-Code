# Fair Code — Algorithmic Bias Detection & Mitigation

> *AI systems are making decisions about your freedom, your job, and your healthcare. This project proves the bias is real — and shows exactly how to fix it.*

**by Yash Kewlani · [@thefaircodeproject](https://instagram.com/thefaircodeproject)**

🌐 **[fair-code-five.vercel.app](https://fair-code-five.vercel.app)** — live interactive website with all audits, explainers, and visualisations

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat-square&logo=python)
![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-orange?style=flat-square&logo=scikit-learn)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebooks-F37626?style=flat-square&logo=jupyter)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)
![Contributions Welcome](https://img.shields.io/badge/Contributions-Welcome-blueviolet?style=flat-square)
![Deployed](https://img.shields.io/badge/Deployed-Vercel-black?style=flat-square&logo=vercel)
![CI](https://github.com/yakew7/Fair-Code/actions/workflows/audits.yml/badge.svg)

---

## Star History

<a href="https://www.star-history.com/?repos=yakew7%2FFair-Code&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=yakew7/Fair-Code&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=yakew7/Fair-Code&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=yakew7/Fair-Code&type=date&legend=top-left" />
 </picture>
</a>

---

## What This Is

Fair Code is an ongoing research and engineering project that exposes bias in real-world AI systems and demonstrates concrete mitigation strategies. Every audit follows the same pipeline:

```
train a biased model → measure the fairness gap → engineer a fair model → measure again
```

No theory. No hand-waving. Just data, code, and results.

Each audit ships as both a pair of Python scripts (`unfair.py` / `fair.py`) for direct execution and a Jupyter notebook (`notebooks/`) that walks through the full pipeline step by step — with visualisations, proxy detection, and annotated findings.

---

## Results at a Glance

| # | Domain | Protected Attribute | Proxies Removed | Gap Before → After | Reduction |
|:-:|--------|--------------------|-----------------|--------------------|:---------:|
| 01 | [Criminal Justice](#01--compas--criminal-justice-bias) | Race | Custody Status | 86.77% → 15.69% | **71%** |
| 02 | [Hiring](#02--ai-fair-recruitment--hiring-bias) | Gender | Age | 4.51% → 0.12% | **97.3%** |
| 03 | [Lending](#03--german-credit-lending--lending-bias) | Age | Employment Tenure | 7.16% → 1.89% | **73.6%** |
| 04 | [Healthcare](#04--insurance-denial--healthcare-bias) | Age, Gender | BMI, Smoker, Diabetic | Age: 7.93% → 3.18% | **60%** |
| ↳  | | | | Gender: 5.44% → 1.54% | **72%** |
| 05 | [Welfare](#05--benefits-denial--welfare-eligibility-bias) | Sex, Race, Origin, Age | Relationship, Marital Status, Hours, Occupation | Sex: 18.00% → 8.52% | **53%** |
| ↳  | | | | Race: 12.75% → 6.90% | **46%** |
| ↳  | | | | Origin: 4.40% → 0.52% | **88%** |

---

## Repository Structure

```
Fair-Code/
│
├── .github/
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── dependabot.yml
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml
│   │   ├── new_audit.yml
│   │   └── new_explainer.yml
│   └── workflows/
│       └── audits.yml                   # CI: runs all audit scripts on every push/PR
│
├── COMPAS/                              # each audit folder has the same structure:
│   ├── unfair.py                        #   biased model
│   ├── fair.py                          #   mitigated model
│   ├── *.csv                            #   dataset
│   ├── unfair.png                       #   terminal output — biased results
│   └── fair.png                         #   terminal output — mitigated results
├── AI Fair Recruitment/
├── German Credit Lending/
├── Insurance Denial/
├── Benefits Denial/
│
├── notebooks/
│   ├── 01_compas_bias_audit.ipynb
│   ├── 02_hiring_bias_audit.ipynb
│   ├── 03_german_credit_bias_audit.ipynb
│   ├── 04_insurance_denial_bias_audit.ipynb
│   └── 05_benefits_denial_bias_audit.ipynb
│
├── explainers/
│   ├── proxy-variables.md
│   ├── equalized-odds.md
│   ├── sampling-bias.md
│   ├── shap-values.md
│   ├── disparate-impact.md
│   ├── disparate-treatment.md
│   ├── fairness-metric-conflicts.md
│   ├── calibration.md
│   ├── demographic-parity.md
│   ├── feedback-loop-bias.md
│   ├── label-bias.md
│   ├── individual-fairness.md
│   ├── counterfactual-fairness.md
│   └── neural-networks.md
│
├── CHANGELOG.md
├── CITATION.cff
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE
├── SECURITY.md
├── index.html                           # live at fair-code-five.vercel.app
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
|-------|:-------------------:|
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
    # CustodyStatus removed ✓  (proxy for race via over-policing)
]])
```

| Group | High-Risk Flag Rate |
|-------|:-------------------:|
| Black Defendants | 84.71% |
| White Defendants | 69.02% |
| **New Fairness Gap** | **15.69%** |

**Result: 71% reduction in the fairness gap.**

> **Key insight:** Removing race alone isn't enough. Proxy variables like custody status carry the same racial signal because of historical over-policing of Black communities. Both the protected attribute *and* its proxies must be removed.

📓 **[Full notebook walkthrough →](notebooks/01_compas_bias_audit.ipynb)**

---

### 02 · AI Fair Recruitment — Hiring Bias

> *"Women were hired 20.9% less than equally qualified men. The algorithm wasn't told to discriminate. It learned to."*

**Dataset:** `AI_Fair_Recruitment_Dataset.csv` — Recruitment dataset with gender, age, experience, and technical test scores

#### The Problem — `unfair.py`

Biased model trained with gender and age alongside merit-based inputs.

| Group | Hire Rate |
|-------|:---------:|
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
|-------|:---------:|
| Men | 11.48% |
| Women | 11.35% |
| **New Fairness Gap** | **0.12%** |

**Result: 97.3% reduction in the fairness gap.**

> **Key insight:** The model was never explicitly told to discriminate by gender. It inferred a gender penalty from historical hiring patterns in the training data — patterns reflecting human bias, not merit. Restricting inputs to demonstrated ability eliminates the channel through which that bias flows.

📓 **[Full notebook walkthrough →](notebooks/02_hiring_bias_audit.ipynb)**

---

### 03 · German Credit Lending — Lending Bias

> *"A credit scoring model rates young applicants as bad credit risks at 6.39 percentage points higher than older applicants with identical financial profiles. It learned age from job tenure."*

**Dataset:** `credit_customers.csv` — UCI Statlog German Credit dataset (1,000 records) · [Kaggle source](https://www.kaggle.com/datasets/ppb00x/credit-risk-customers)

Age discrimination in lending is documented across financial systems worldwide. Young borrowers face higher rejection rates not because of creditworthiness, but because the features used to measure it — employment tenure, account history, savings — are structurally correlated with age.

#### The Problem — `unfair.py`

Biased model trained with `age` and `employment` (tenure) as features.

| Group | Good Credit Rate |
|-------|:----------------:|
| Older Applicants (30+) | 83.97% |
| Young Applicants (<30) | 76.81% |
| **Fairness Gap** | **7.16%** |

#### Proxy Variable: `employment` (tenure)

```python
print(pd.crosstab(df['employment'], df['is_young'], normalize='columns').round(3))

# Result:
# is_young          0      1
# employment
# <1yr           0.113  0.272   ← young applicants over-represented
# 1-4yr          0.294  0.455
# 4-7yr          0.253  0.200
# >=7yr          0.359  0.073   ← older applicants over-represented
```

#### The Fix — `fair.py`

Dropped `age` and `employment`. Retained only objective financial signals.

| Group | Good Credit Rate |
|-------|:----------------:|
| Older Applicants (30+) | 80.15% |
| Young Applicants (<30) | 78.26% |
| **New Fairness Gap** | **1.89%** |

**Result: 73.6% reduction in the fairness gap.**

> **Key insight:** Employment tenure looks like a legitimate financial signal, and in isolation it is. But it's also a near-perfect proxy for age. A model that penalizes short tenure is partially penalizing youth, regardless of whether "age" appears anywhere in the feature list.

📓 **[Full notebook walkthrough →](notebooks/03_german_credit_bias_audit.ipynb)**

---

### 04 · Insurance Denial — Healthcare Bias

> *"An insurance AI flags older patients for high-cost claims at 7.93 percentage points higher than younger patients — using BMI, smoking status, and diabetic status as proxies for race and class."*

**Dataset:** `insurance.csv` — [Kaggle: Insurance Claim Analysis](https://www.kaggle.com/datasets/thedevastator/insurance-claim-analysis-demographic-and-health) (1,340 records)

#### The Problem — `unfair.py`

| Group | High-Cost Claim Flag Rate |
|-------|:-------------------------:|
| Older (35+) | 44.59% |
| Young (<35) | 36.67% |
| **Fairness Gap (Age)** | **7.93%** |

| Group | High-Cost Claim Flag Rate |
|-------|:-------------------------:|
| Female | 43.85% |
| Male | 38.41% |
| **Fairness Gap (Gender)** | **5.44%** |

#### The Fix — `fair.py`

Dropped `age`, `gender`, `bmi`, `smoker`, and `diabetic`. Retained only objective policy-level signals: `bloodpressure`, `children`, `region`.

| Group | High-Cost Claim Flag Rate |
|-------|:-------------------------:|
| Older (35+) | 50.68% |
| Young (<35) | 47.50% |
| **New Fairness Gap (Age)** | **3.18%** |

| Group | High-Cost Claim Flag Rate |
|-------|:-------------------------:|
| Female | 48.46% |
| Male | 50.00% |
| **New Fairness Gap (Gender)** | **1.54%** |

**Result: 60% reduction in age gap. 72% reduction in gender gap.**

> **Key insight:** Insurance AI models don't need to name race to discriminate by race. BMI, smoking, and diabetic status are the `CustodyStatus` of health insurance — clinical-sounding features that carry protected-class signal because of structural inequalities baked into American healthcare.

📓 **[Full notebook walkthrough →](notebooks/04_insurance_denial_bias_audit.ipynb)**

---

### 05 · Benefits Denial — Welfare Eligibility Bias

> *"An automated means-test flags male applicants as ineligible at 18 percentage points higher than female applicants — not because of what they earn, but because of who they're married to."*

**Dataset:** `adult.csv` — UCI Adult Census Income dataset (48,842 records) · [Kaggle source](https://www.kaggle.com/datasets/wenruliu/adult-income-dataset)

Automated welfare and benefits systems use income-prediction models to screen applicants for housing assistance, food support, and healthcare subsidies. This audit replicates that logic: the model predicts whether an applicant earns above a means-test threshold ($50K) and flags them as ineligible.

#### The Problem — `unfair.py`

Trained with sex, race, age, and national origin directly, plus four proxy variables that reconstruct those attributes even after the protected columns are removed.

| Group | Ineligibility Flag Rate |
|-------|:-----------------------:|
| Male applicants | 25.71% |
| Female applicants | 7.71% |
| **Fairness Gap (Sex)** | **18.00%** |

| Group | Ineligibility Flag Rate |
|-------|:-----------------------:|
| White/Asian-PI | 21.22% |
| Other minorities | 8.47% |
| **Fairness Gap (Race)** | **12.75%** |

| Group | Ineligibility Flag Rate |
|-------|:-----------------------:|
| US-born | 20.20% |
| Foreign-born | 15.81% |
| **Fairness Gap (Origin)** | **4.40%** |

#### The Fix — `fair.py`

Dropped all four protected attributes and all four proxy variables. Retained only the features a means-tested programme can legitimately consult under equality law.

```python
# THE FIX: Policy-defined economic signals only
features = [
    'workclass',       # employment sector
    'education',       # education level
    'education.num',   # education years
    'capital.gain',    # financial assets
    'capital.loss',    # financial assets
    # age            removed ✓  (protected attribute)
    # sex            removed ✓  (protected attribute)
    # race           removed ✓  (protected attribute)
    # native.country removed ✓  (protected attribute)
    # relationship   removed ✓  (proxy: Husband=0% female, Wife=0% male)
    # marital.status removed ✓  (proxy: encodes sex via spousal status)
    # hours.per.week removed ✓  (proxy: encodes sex via caregiving gap)
    # occupation     removed ✓  (proxy: encodes race via occupational segregation)
]
```

| Gap | Before | After | Reduction |
|-----|:------:|:-----:|:---------:|
| Sex | 18.00% | 8.52% | **53%** |
| Race | 12.75% | 6.90% | **46%** |
| Origin | 4.40% | 0.52% | **88%** |

**Result: 53% reduction in sex gap. 46% reduction in race gap. 88% reduction in national-origin gap.**

> **Key insight:** `relationship`, `marital.status`, `hours.per.week`, and `occupation` all sound purely economic — but each carries protected-class signal because of how work, caregiving, and labour markets are structurally organised. The fix is to ask only what the law actually permits: education, employment sector, and capital assets.

📓 **[Full notebook walkthrough →](notebooks/05_benefits_denial_bias_audit.ipynb)**

---

## Explainers

| Explainer | What it covers |
|-----------|----------------|
| [What is a Proxy Variable?](explainers/proxy-variables.md) | Why AI stays biased even after you remove protected attributes from the data |
| [What is Equalized Odds?](explainers/equalized-odds.md) | The fairness metric that catches a model treating two groups differently — even when overall accuracy looks fine |
| [What is Sampling Bias?](explainers/sampling-bias.md) | Why your AI works great in the lab and fails on the people who need it most |
| [What Are SHAP Values?](explainers/shap-values.md) | How to see exactly what drove an AI decision — and use that to catch bias |
| [What is Disparate Impact?](explainers/disparate-impact.md) | The 80% rule — the legal threshold under US employment law that flags an AI decision as discriminatory |
| [What is Disparate Treatment?](explainers/disparate-treatment.md) | Intentional discrimination — when a protected attribute or its proxy is a direct input to the model |
| [Why Fairness Metrics Conflict](explainers/fairness-metric-conflicts.md) | The proven mathematical impossibility of satisfying demographic parity, equalized odds, and predictive parity simultaneously |
| [What is Calibration?](explainers/calibration.md) | Why a model can be equally accurate for everyone and still treat them unequally |
| [What is Demographic Parity?](explainers/demographic-parity.md) | The foundational fairness metric that requires equal positive prediction rates across groups |
| [What is Feedback Loop Bias?](explainers/feedback-loop-bias.md) | Why AI systems don't just reflect historical bias — they actively amplify it across retraining cycles |
| [What is Label Bias?](explainers/label-bias.md) | Why a model trained on historical decisions inherits the prejudice of the humans who made them — even when the features look clean |
| [What is Individual Fairness?](explainers/individual-fairness.md) | Why treating groups equally in aggregate is not enough — and what it means to treat similar people similarly |
| [What is Counterfactual Fairness?](explainers/counterfactual-fairness.md) | Why removing a protected attribute isn't enough — and what it means for a model's decision to be causally free of demographic influence |
| [What Happens Inside a Neural Network?](explainers/neural-networks.md) | How networks learn from data, why that makes bias inevitable without auditing, and how to inspect what a model actually learned |
| [Why AI Hallucinates?](explainers/ai-hallucinations.md) | Confident predictions in sparse areas of the feature space — from tabular denial scores to ChatGPT's fake court citations |

---

## Methodology

All projects use the same pipeline:

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

| Component | Details |
|-----------|---------|
| **Model** | Random Forest Classifier (`sklearn.ensemble.RandomForestClassifier`, `n_estimators=100`) — chosen for resistance to overfitting, feature importance interpretability, and SHAP compatibility |
| **Split** | 80/20 train/test, `random_state=42` |
| **Primary metric** | Demographic Parity — difference in positive prediction rates across demographic groups |
| **Secondary metrics** | Equalized Odds (TPR + FPR parity), Disparate Impact Ratio (Four-Fifths Rule), SHAP feature attribution |
| **Mitigation** | Pre-processing attribute removal — protected attributes and identified proxies are dropped before training |
| **Proxy detection** | Chi-squared test (`scipy.stats.chi2_contingency`) — features with `p < 0.05` flagged as proxies. See [explainers/proxy-variables.md](explainers/proxy-variables.md) |

---

## Why This Matters

- **87%** of companies use AI to screen job applicants before a human sees a resume
- **46** US states have used algorithmic risk tools in criminal sentencing
- **1M+** people assessed by COMPAS-style tools annually
- **0** states require the algorithm to be audited for bias

These aren't edge cases or hypotheticals. Algorithms like COMPAS are deployed in courtrooms today. Hiring AIs filter your resume before a human ever reads it. Credit scoring models penalize young borrowers for not having lived long enough to build tenure. The bias in these systems is documented, measurable — and fixable.

---

## Getting Started

```bash
git clone https://github.com/yakew7/Fair-Code.git
cd Fair-Code
pip install -r requirements.txt
```

Run any audit from the repository root:

```bash
python COMPAS/unfair.py   # see the bias
python COMPAS/fair.py     # see the fix
```

Each script resolves its dataset relative to its own location, so it runs from anywhere — `cd COMPAS && python unfair.py` works too.

The same pattern applies to all five projects — swap `COMPAS` for `"AI Fair Recruitment"`, `"German Credit Lending"`, `"Insurance Denial"`, or `"Benefits Denial"`.

Run the notebooks:

```bash
pip install jupyter
jupyter notebook notebooks/
```

Or open any `.ipynb` directly in VS Code, JupyterLab, or Google Colab.

---

## Tech Stack

| Component | Details |
|-----------|---------|
| Language | Python 3 |
| Libraries | `pandas`, `scikit-learn`, `fairlearn`, `shap`, `matplotlib`, `scipy` |
| Notebooks | Jupyter (`.ipynb`) — one per audit, in `notebooks/` |
| Datasets | ProPublica COMPAS (public domain), AI Fair Recruitment (Kaggle), UCI German Credit / Statlog (Kaggle), Insurance Claims (Kaggle), UCI Adult Census Income (Kaggle) |

---

## What's Next

- [x] COMPAS Criminal Justice Bias
- [x] AI Fair Recruitment Bias
- [x] German Credit Lending Bias
- [x] Insurance Denial — Healthcare Bias
- [x] Benefits Denial — Welfare Eligibility Bias
- [x] Jupyter notebook walkthroughs for all five audits
- [x] CI pipeline — all audit scripts run automatically on every push and PR
- [x] Explainer: Proxy Variables
- [x] Explainer: Equalized Odds
- [x] Explainer: Sampling Bias
- [x] Explainer: SHAP Values
- [x] Explainer: Disparate Impact (The 80% Rule)
- [x] Explainer: Disparate Treatment
- [x] Explainer: Why Fairness Metrics Conflict
- [x] Explainer: Calibration
- [x] Explainer: Demographic Parity
- [x] Explainer: Feedback Loop Bias
- [x] Explainer: Label Bias
- [x] Explainer: Individual Fairness
- [x] Explainer: Counterfactual Fairness
- [x] Explainer: What Happens Inside a Neural Network
- [x] Explainer: Why AI Hallucinates
- [ ] Facial recognition accuracy gaps (MIT Gender Shades methodology)
- [ ] HMDA mortgage lending bias
- [ ] LLM bias audit
- [ ] Fairness audit web dashboard

Want to contribute an audit or explainer? See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Website

The full project is at **[fair-code-five.vercel.app](https://fair-code-five.vercel.app)** — everything in this repo presented visually, with before/after terminal outputs, bias bar charts, search and filter across all audits and explainers, copy buttons on every code block, share links per audit, and light/dark mode.

Built as a single `index.html` — no framework, no build step.

---

## Connect

Follow the project on Instagram: **[@thefaircodeproject](https://instagram.com/thefaircodeproject)**
Data. Code. Accountability. One post at a time.

---

*All datasets used in this project are publicly available. Fair Code is for educational and awareness purposes.*
