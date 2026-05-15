# Fair Code — Algorithmic Bias Detection & Mitigation

> *AI systems are making decisions about your freedom, your job, and your healthcare. This project proves the bias is real — and shows exactly how to fix it.*

**by Yash Kewlani · [@thefaircodeproject](https://instagram.com/thefaircodeproject)**

---

## What This Is

Fair Code is a two-part research and engineering project that exposes bias in real-world AI systems and demonstrates concrete mitigation strategies. Both projects follow the same structure: **train a biased model → measure the fairness gap → engineer a fair model → measure again.**

No theory. Just data, code, and results.

---

## Projects

### 01 · COMPAS — Criminal Justice Bias

> *"A real algorithm used in US courtrooms flags Black defendants as high-risk at 87%. White defendants? 0.4%."*

**Dataset:** `compas-scores-raw.csv` — ProPublica's public COMPAS dataset (70,000+ records)

**The Problem (`unfair.py`)**

The biased model is trained with race and custody status as features — inputs COMPAS-style systems actually use in production. The results:

| Group | High-Risk Flag Rate |
|---|---|
| Black Defendants | 87.16% |
| White Defendants | 0.40% |
| **Fairness Gap** | **86.77%** |

**The Fix (`fair.py`)**

Dropped race directly, and custody status as a known proxy variable — a correlated feature that smuggles race back in even when the column is removed.

| Group | High-Risk Flag Rate |
|---|---|
| Black Defendants | 84.71% |
| White Defendants | 69.02% |
| **New Fairness Gap** | **15.69%** |

**Result: 71% reduction in the fairness gap.**

**Key Insight:** Removing race alone isn't enough. Proxy variables like custody status carry the same racial signal through the model. Both must go.

---

### 02 · AI Recruitment — Hiring Bias

> *"Women were hired 20.9% less than equally qualified men. The algorithm wasn't told to discriminate. It learned to."*

**Dataset:** `AI_Fair_Recruitment_Dataset.csv` — Real recruitment dataset with gender, age, experience, and technical test scores

**The Problem (`unfair.py`)**

Biased model trained with gender and age included as features alongside merit-based inputs:

| Group | Hire Rate |
|---|---|
| Men | 21.62% |
| Women | 17.10% |
| **Fairness Gap** | **4.51%** |

Women were hired **~21% less** than men with identical experience and test scores.

**The Fix (`fair.py`)**

Dropped gender and age entirely. Retained only merit-based features: experience years and technical test score.

| Group | Hire Rate |
|---|---|
| Men | 11.48% |
| Women | 11.35% |
| **New Fairness Gap** | **0.12%** |

**Result: 97.3% reduction in the fairness gap.**

---

## Repository Structure

```
Fair-Code/
│
├── COMPAS/
│   ├── unfair.py              # Biased model (race + custody status included)
│   ├── fair.py                # Mitigated model (race + proxy removed)
│   ├── compas-scores-raw.csv  # ProPublica COMPAS dataset
│   ├── unfair.jpg             # Terminal output — biased results
│   └── fair.jpg               # Terminal output — mitigated results
│
├── Ai Fair recrutment Dataset/
│   ├── unfair.py              # Biased model (gender + age included)
│   ├── fair.py                # Mitigated model (merit only)
│   ├── AI_Fair_Recruitment_Dataset.csv
│   ├── unfair.jpg             # Terminal output — biased results
│   └── fair.jpg               # Terminal output — mitigated results
│
└── README.md
```

---

## Methodology

Both projects use the same bias detection and mitigation pipeline:

```
1. Load dataset
2. Train biased model (protected attributes included)
3. Measure fairness gap across demographic groups
4. Remove protected attributes + known proxy variables
5. Retrain fair model (merit features only)
6. Measure fairness gap again
7. Compare
```

**Model:** Random Forest Classifier (`sklearn.ensemble.RandomForestClassifier`)  
**Split:** 80/20 train/test, `random_state=42`  
**Fairness Metric:** Demographic Parity — difference in positive prediction rates across groups  
**Mitigation Strategy:** Pre-processing attribute dropping (protected attributes + proxy variables)

---

## Results Summary

| Project | Before | After | Reduction |
|---|---|---|---|
| COMPAS (racial bias) | 86.77% gap | 15.69% gap | **71%** |
| Hiring AI (gender bias) | 4.51% gap | 0.12% gap | **97.3%** |

---

## Why This Matters

- **87%** of companies use AI to screen job applicants before a human sees a resume *(Forbes, 2024)*
- **46** US states have used algorithmic risk tools in criminal sentencing
- **0** federal laws currently require hiring AIs to be audited for gender or racial bias

These aren't edge cases or hypotheticals. Algorithms like COMPAS are deployed in courtrooms. Hiring AIs filter your resume before a human ever reads it. The bias in these systems is documented, measurable — and fixable.

---

## Tech Stack

- **Language:** Python 3
- **Libraries:** `pandas`, `scikit-learn`
- **Datasets:** ProPublica COMPAS (public), AI Fair Recruitment Dataset (Kaggle)

---

## Getting Started

```bash
git clone https://github.com/yakew7/Fair-Code.git
cd Fair-Code
pip install pandas scikit-learn
```

**Run the COMPAS project:**
```bash
cd COMPAS
python unfair.py   # See the bias
python fair.py     # See the fix
```

**Run the recruitment project:**
```bash
cd "Ai Fair recrutment Dataset"
python unfair.py   # See the bias
python fair.py     # See the fix
```

---

## What's Next

- [ ] Healthcare AI bias (Optum dataset)
- [ ] Facial recognition accuracy gaps (MIT Gender Shades)
- [ ] HMDA mortgage lending bias
- [ ] Fairness dashboard web app

---

## Connect

Follow the project on Instagram: **[@thefaircodeproject](https://instagram.com/thefaircodeproject)**  
Data. Code. Accountability. One post at a time.

---

*All datasets used are publicly available. This project is for educational and awareness purposes.*