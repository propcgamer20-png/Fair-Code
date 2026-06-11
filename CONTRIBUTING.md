# Contributing to Fair Code

<div align="center">

**Bias audits. Clear explainers. Reproducible results.**

[Issue templates](.github/ISSUE_TEMPLATE/) are the preferred way to claim work before you start.

</div>

Thanks for contributing. Fair Code accepts two kinds of additions:

- **Audits** - a real dataset, a biased model, a fair model, proxy analysis, and before/after results
- **Explainers** - a clear explanation of a fairness concept, with examples and runnable code

Consistency matters here. It is what makes the repo credible and easy to review.

---

## Quick path

1. Check the roadmap in [README.md](README.md#whats-next).
2. Open an issue using the matching template.
3. Build your audit or explainer to match the structure below.
4. Open a PR and include the requested proof.

If you are unsure whether an idea fits, open an issue first and ask.

---

## 1. Before you start

- Read the relevant section in this guide before writing code.
- Claim the work in an issue before you begin.
- Keep the scope focused: one audit or one explainer per PR.
- Do not start on a duplicate topic if someone else is already working on it.

Example issue text:

> Taking on HMDA mortgage lending bias - starting with the federal HMDA dataset.

or

> Writing an explainer on predictive parity.

---

## 2. Audit contributions

An audit proves bias exists, shows where it comes from, and demonstrates a mitigation.

### Folder layout

Each audit lives in its own top-level folder named after the domain, not the dataset.

```text
Fair-Code/
├── Your-Domain-Here/
│   ├── unfair.py
│   ├── fair.py
│   ├── your-dataset.csv
│   ├── unfair.png
│   └── fair.png
└── notebooks/
    └── 06_your_domain_bias_audit.ipynb
```

Rules:

- Keep the audit folder flat.
- Do not add extra subfolders.
- Use the existing naming style for the folder and files.
- Add a notebook only if you can make it useful and complete.

### The two required scripts

Every audit must include exactly two scripts.

#### `unfair.py`

This is the biased baseline. It must:

- load the dataset
- train a Random Forest Classifier
- include protected attributes in the model
- use `random_state=42`
- use an 80/20 train/test split
- print results in this format:

```text
--- BIASED MODEL RESULTS ---

[Group A] [Outcome] Rate: XX.XX%
[Group B] [Outcome] Rate: XX.XX%

Fairness Gap: XX.XX%
```

#### `fair.py`

This is the mitigated version. It must:

- drop the protected attribute(s)
- drop any proxy variables you identified
- retrain on the remaining features
- print results in this format:

```text
--- MITIGATED (UNBIASED) RESULTS ---

[Group A] [Outcome] Rate: XX.XX%
[Group B] [Outcome] Rate: XX.XX%

New Fairness Gap: XX.XX%
```

### Notebook expectations

Notebooks are optional, but strongly encouraged.

Use the next sequential filename:

```text
notebooks/06_your_domain_bias_audit.ipynb
```

Recommended structure:

| # | Section | What it should do |
|:-:|---------|-------------------|
| 1 | Title | Audit number, domain, and a one-line hook |
| 2 | Setup | Imports and the shared plot styling |
| 3 | Load and explore | Load the CSV, inspect shape/columns, and show the raw disparity |
| 4 | Proxy analysis | Use chi-squared for categorical features or Pearson correlation for continuous ones |
| 5 | Train biased model | Match `unfair.py` exactly |
| 6 | Train fair model | Match `fair.py` exactly |
| 7 | Compare results | Before/after bar charts and reduction summary |
| 8 | Key insight | One short markdown paragraph in plain language |

The proxy analysis section is required. Do not skip it.

---

## 3. Proxy variables

Removing the protected attribute alone is rarely enough.

A proxy variable is a feature that carries the same signal as the protected attribute, even after the protected column is removed.

| Audit | Protected attribute | Proxy variable(s) | Why it matters |
|-------|---------------------|-------------------|----------------|
| COMPAS | Race | `CustodyStatus` | Historical over-policing can leak race back into the model |
| German Credit Lending | Age | `employment` (tenure) | Young applicants cannot have long work histories |
| Insurance Denial | Race, class | `bmi`, `smoker`, `diabetic` | Structural disparities show up in health-related features |
| Benefits Denial | Sex | `relationship`, `marital.status`, `hours.per.week` | Family roles and caregiving patterns encode sex |
| Benefits Denial | Race | `occupation` | Occupational segregation can reconstruct race |
| Healthcare Readmission | Race, income | `payer_code`, `discharge_disposition_id`, `number_inpatient` | Insurance type encodes race; discharge destination and prior hospitalisation count encode access gaps, not clinical severity |

How to check likely proxies:

```python
import pandas as pd

df = pd.read_csv("your-dataset.csv")

# Continuous features
print(df[["potential_proxy", "protected_attribute"]].corr())

# Categorical features
print(pd.crosstab(df["potential_proxy"], df["protected_attribute"], normalize="columns").round(3))
```

If you keep a feature that correlates strongly with a protected attribute, explain why it is a legitimate signal and not a proxy.

---

## 4. Screenshots

After running both scripts, save terminal screenshots as PNG files:

| File | Content |
|------|---------|
| `unfair.png` | Output from `unfair.py` |
| `fair.png` | Output from `fair.py` |

Requirements:

- PNG only
- place both files in the audit folder
- make sure the output is readable

---

## 5. Dataset requirements

Datasets must be:

- public
- real
- easy to access

Good sources include Kaggle, government data, ProPublica, and academic releases.

If the dataset is under about 50 MB, commit it with the audit. If it is larger, add a `DATA.md` file with a direct download link and setup steps.

---

## 6. Update the README

Add your audit to the results table in `README.md`:

```markdown
| 06 | [Your Domain](#link-to-section) | Protected Attribute | Proxies Removed | Gap Before -> After | Reduction |
```

Then add a full project section using the same pattern as the existing audits:

1. Opening quote
2. Dataset description and context
3. The problem section with biased results
4. Code showing what you removed and why
5. The fix section with mitigated results
6. A short key insight paragraph
7. Notebook link, if applicable

The key insight paragraph is required. Keep it short, concrete, and jargon-free.

---

## 7. Fairness metric

All audits use **Demographic Parity** by default: the difference in positive prediction rates between groups.

If your domain truly needs another metric, open an issue first and explain why. See [Equalized Odds](explainers/equalized-odds.md) for a good example of when a different metric is appropriate.

---

## 8. Explainer contributions

Explainers live in `explainers/` and should make one fairness concept easy to understand.

### Existing explainers

| File | Concept |
|------|---------|
| `proxy-variables.md` | Why AI stays biased after protected attributes are removed |
| `equalized-odds.md` | Error-rate parity across groups |
| `sampling-bias.md` | Why training data can misrepresent the real world |
| `shap-values.md` | How to explain a model decision and catch bias |
| `disparate-impact.md` | The 80% rule in hiring, lending, and insurance |
| `disparate-treatment.md` | Intentional discrimination via direct inputs or proxies |
| `fairness-metric-conflicts.md` | Why major fairness metrics cannot all be satisfied at once |
| `calibration.md` | Why equal accuracy does not guarantee equal treatment |
| `demographic-parity.md` | Equal positive prediction rates across groups |
| `feedback-loop-bias.md` | How retraining can amplify bias |
| `label-bias.md` | How historical labels inherit human prejudice |
| `individual-fairness.md` | Treating similar people similarly |
| `counterfactual-fairness.md` | Decisions that stay stable under demographic changes |
| `neural-networks.md` | How networks learn bias from data |
| `ai-hallucinations.md` | Why confident predictions can still be wrong |
| `reinforcement-learning.md` | How RL agents learn from reward signals — and why that makes bias hard to see and harder to fix |
| `proxy-entanglement.md` | Why removing proxies one at a time fails when multiple features encode the same protected signal through correlated, redundant channels |
| `ml-bias.md` | The four entry points — training data, labels, proxies, and feedback loops — that let bias enter a model, with detection code and real examples |
| `data-leakage.md` | Why a model that scores 99% on every internal test can still fail at deployment — target leakage, train-test contamination, and detection code |

### A good explainer should include

| # | Section | What to include |
|:-:|---------|-----------------|
| 1 | Definition | Plain-language definition, no jargon |
| 2 | Why it matters | One short paragraph on the real-world impact |
| 3 | Concrete example | A real case from this repo or a documented real-world example |
| 4 | Detection code | Runnable Python using `pandas` and `scikit-learn` where possible |
| 5 | Limitations | Honest trade-offs and edge cases |
| 6 | Related concepts | Links to other explainers or audits |
| 7 | Further reading | 2-3 primary sources, not link farms |

File naming:

```text
explainers/your-concept-name.md
```

Use lowercase and hyphens only.

When you add an explainer, update the Explainers table in `README.md`:

```markdown
| [Your Concept](explainers/your-concept-name.md) | One-line description |
```

---

## 9. CI and branch rules

Every push and pull request runs the audit scripts in `.github/workflows/audits.yml`.

What this means:

- scripts must run from the repository root
- dataset paths must be resolved relative to the script file, not the current working directory
- failing CI blocks merge

Recommended pattern:

```python
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(BASE_DIR, "your-dataset.csv"))
```

Branch rules on `main`:

- PRs are required
- CI must pass
- force pushes are blocked
- the branch cannot be deleted

If CI fails, push a new commit to your branch and let the check rerun.

---

## 10. How to submit

### Audit PRs

1. Fork the repo.
2. Create a branch: `git checkout -b audit/your-domain`.
3. Add the folder, scripts, dataset, and screenshots.
4. Add a notebook if you wrote one.
5. Update `README.md`.
6. Open a PR titled like: `Audit: HMDA Mortgage Lending Bias`.
7. Confirm the `run-audits` check passes.

Include in the PR description:

- dataset source
- bias type
- before/after fairness gap numbers
- proxy variables found and why you dropped them
- whether you included a notebook

### Explainer PRs

1. Fork the repo.
2. Create a branch: `git checkout -b explainer/your-concept`.
3. Add your markdown file to `explainers/`.
4. Update the Explainers table in `README.md`.
5. Open a PR titled like: `Explainer: Predictive Parity`.
6. Confirm the `run-audits` check passes.

Include in the PR description:

- the concept you are explaining
- why it belongs in this repo

---

## 11. What will not be merged

### Audits

- synthetic or toy datasets
- missing `random_state=42`
- inconsistent train/test splitting
- fair models that only work by collapsing accuracy
- no proxy analysis
- `.jpg` or `.jpeg` screenshots
- datasets that require login or payment

### Notebooks

- proxy analysis skipped
- inconsistent styling or color palette
- numbering that does not follow the existing sequence

### Explainers

- concept defined but not demonstrated
- no limitations or trade-offs
- toy examples as the main evidence
- topics already covered in the repo

---

All datasets used in this project are publicly available. Fair Code is for educational and awareness purposes.