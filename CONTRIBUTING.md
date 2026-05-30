# Contributing to Fair Code

Thanks for wanting to add to this. There are two ways to contribute: **audits** and **explainers**.

An **audit** finds a real dataset where an AI system produces measurably biased outcomes, proves it with code, fixes it, and proves that too. An **explainer** takes a concept in algorithmic fairness and makes it concrete — with a clear definition, real examples, and runnable detection code.

Both follow strict structure requirements. Consistency is what makes the repo credible.

---

## Before You Start

Check the [roadmap in the README](README.md#whats-next) and open an Issue before doing any work. If two people are working on the same thing at the same time, that's wasted effort. The Issue is just a one-liner:

> *"Taking on HMDA mortgage lending bias — starting with the federal HMDA dataset."*

or

> *"Writing an explainer on predictive parity."*

---

## Folder Structure

Every audit lives in its own top-level folder named after the domain, not the dataset. Each audit also has a corresponding notebook in `notebooks/`.

```
Fair-Code/
├── .github/
│   ├── PULL_REQUEST_TEMPLATE.md         ← fill this out when opening a PR
│   └── ISSUE_TEMPLATE/
│       ├── bug_report.yml               ← report a broken script or wrong result
│       ├── new_audit.yml                ← claim a new audit before you start
│       └── new_explainer.yml            ← claim a new explainer before you start
│
├── COMPAS/                              ← existing
├── AI Fair Recruitment/                 ← existing
├── German Credit Lending/               ← existing
├── Insurance Denial/                    ← existing
├── Benefits Denial/                     ← existing
├── Your-Domain-Here/                    ← your new audit
│   ├── unfair.py
│   ├── fair.py
│   ├── your-dataset.csv
│   ├── unfair.png
│   └── fair.png
│
├── notebooks/
│   ├── 01_compas_bias_audit.ipynb       ← existing
│   ├── ...
│   └── 06_your_domain_bias_audit.ipynb  ← your new notebook (optional but appreciated)
│
├── explainers/
│   ├── proxy-variables.md               ← existing
│   ├── ...
│   └── your-concept-name.md             ← your new explainer
│
└── ...
```

No subfolders within audit folders, no extra files. Keep it flat.

---

## The Two Scripts

Every audit has exactly two scripts. Nothing more.

### `unfair.py` — the biased model

Demonstrates the bias. Must:

- Load the dataset
- Train a Random Forest Classifier with protected attributes included
- Use `random_state=42` and an 80/20 train/test split (non-negotiable — required for reproducibility)
- Print results in this exact format:

```
--- BIASED MODEL RESULTS ---

[Group A] [Outcome] Rate: XX.XX%
[Group B] [Outcome] Rate: XX.XX%

Fairness Gap: XX.XX%
```

### `fair.py` — the mitigated model

Fixes the bias. Must:

- Drop the protected attribute(s)
- Drop any identified proxy variables (see [Proxy Variables](#proxy-variables) below)
- Retrain on the remaining features
- Print results in this exact format:

```
--- MITIGATED (UNBIASED) RESULTS ---

[Group A] [Outcome] Rate: XX.XX%
[Group B] [Outcome] Rate: XX.XX%

New Fairness Gap: XX.XX%
```

---

## The Notebook (Optional but Appreciated)

Add a Jupyter notebook to `notebooks/` that walks through your full audit step by step. It's not required to get your PR merged, but it makes the audit significantly more useful for anyone who wants to understand the reasoning, not just run the scripts.

Number it sequentially after the existing ones: `06_your_domain_bias_audit.ipynb`.

### Required sections

Follow the structure of the existing notebooks:

| # | Section | Notes |
|:-:|---------|-------|
| 1 | **Title cell** | Audit number, domain, and the one-sentence hook |
| 2 | **Setup** | Imports + consistent plot styling. Copy the `plt.rcParams` block from an existing notebook — all notebooks use the same colour palette (`ACCENT`, `DANGER`, `SAFE`, `MUTED`) |
| 3 | **Load & explore** | Load the CSV, print shape and columns, show the raw disparity with a plot before any model is trained |
| 4 | **Proxy variable identification** | Run the chi-squared test (categorical) or Pearson correlation (continuous) and show the cross-tabulation. **This is the most important section — don't skip it.** |
| 5 | **Train biased model** | Same `random_state=42` and 80/20 split as the scripts. Same output format as `unfair.py`. |
| 6 | **Train fair model** | Remove protected attributes and proxies. Same output format as `fair.py`. |
| 7 | **Compare results** | Side-by-side bar charts using the project colour palette. Print before/after summary with reduction percentage. |
| 8 | **Key Insight** | A markdown cell, not code. One short paragraph: *why did the bias exist, and why does the fix work?* Plain language, no jargon. |

**File naming:** `notebooks/06_your_domain_bias_audit.ipynb` — lowercase, underscores, sequential number prefix.

---

## Proxy Variables

This is the most important part of the audit. Removing the protected attribute alone is rarely enough.

A proxy variable is a feature that correlates with the protected attribute strongly enough to smuggle the bias back through the model — even after you've dropped race or gender directly.

| Audit | Protected Attribute | Proxy Variable | Why |
|-------|--------------------|-----------------|----|
| COMPAS | Race | `CustodyStatus` | Historical over-policing of Black communities |
| German Credit Lending | Age | `employment` (tenure) | A 24-year-old structurally cannot have 10 years of work history |
| Insurance Denial | Race, class | `bmi`, `smoker`, `diabetic` | Structural disparities in American healthcare |
| Benefits Denial | Sex | `relationship`, `marital.status`, `hours.per.week` | Family roles encode sex; the spousal rate reconstructs it through marriage patterns; the hours gap reflects caregiving burdens |
| Benefits Denial | Race | `occupation` | Occupational segregation encodes race via labour market history |

You must identify and document your proxy variables. To find them:

```python
import pandas as pd

df = pd.read_csv('your-dataset.csv')

# For continuous variables: Pearson correlation
print(df[['potential_proxy_column', 'protected_attribute']].corr())

# For categorical variables: cross-tabulation
print(pd.crosstab(df['potential_proxy'], df['protected_attribute'], normalize='columns').round(3))
```

If a feature shows strong correlation with the protected attribute and you keep it in the fair model, explain why (i.e. it's a genuine merit signal, not a proxy). If you drop it, document it.

---

## Output Screenshots

After running both scripts, take a terminal screenshot and save as `.png`:

| File | Content |
|------|---------|
| `unfair.png` | Terminal output of `unfair.py` |
| `fair.png` | Terminal output of `fair.py` |

These go in your audit folder alongside the scripts. They're the visual proof. **PNG only — not JPG or JPEG.**

---

## Dataset Requirements

Datasets must be:

- **Publicly available** with a clear source (Kaggle, government data, ProPublica, academic release, etc.)
- **Real** — synthetic datasets don't demonstrate real-world bias
- **Accessible** — no login, payment, or data use agreement required to download

Include the dataset file in your folder if it's under ~50MB. If it's larger, add a `DATA.md` with a direct download link and instructions.

---

## Updating the README

Add your audit to the results table at the top of `README.md`:

```markdown
| 06 | [Your Domain](#link-to-section) | Protected Attribute | Proxies Removed | Gap Before → After | Reduction |
```

Then add a full project section following the existing pattern:

1. The opening quote
2. Dataset description and real-world context
3. **The Problem** — biased results table + what features caused it
4. Code snippet showing what you dropped and why
5. **The Fix** — mitigated results table
6. **Key Insight** paragraph (required — see below)
7. Link to your notebook (if you wrote one)

**The Key Insight paragraph is required.** One short paragraph answering: *why did the bias exist, and why does the fix work?* Plain language, no jargon.

---

## Fairness Metric

All audits use **Demographic Parity** as the primary metric: the difference in positive prediction rates between demographic groups.

If your domain genuinely requires a different metric (equalized odds, predictive parity, etc.), open an Issue to discuss it before submitting. See the [Equalized Odds explainer](explainers/equalized-odds.md) for a full breakdown of when that metric applies.

---

## Contributing an Explainer

You don't have to audit a dataset to contribute. If you can explain a concept in algorithmic fairness clearly — with real examples and runnable code — an explainer belongs here.

Explainers live in `explainers/`. The existing ones:

| File | Concept |
|------|---------|
| `proxy-variables.md` | Why AI stays biased even after you remove protected attributes |
| `equalized-odds.md` | The fairness metric that checks both error types across demographic groups |
| `sampling-bias.md` | Why your training data may not represent the people your model affects |
| `shap-values.md` | How to explain individual AI decisions and use that to catch bias |
| `disparate-impact.md` | The legal 80% rule that flags discriminatory selection in hiring, lending, and insurance |
| `disparate-treatment.md` | Intentional discrimination: when a protected attribute or proxy is a direct model input |
| `fairness-metric-conflicts.md` | The proven impossibility of satisfying demographic parity, equalized odds, and predictive parity simultaneously |
| `calibration.md` | Why a model can be equally accurate for all groups and still treat them unequally |
| `demographic-parity.md` | Equal positive prediction rates across groups — when it applies and what it misses |
| `feedback-loop-bias.md` | Why AI systems amplify bias across retraining cycles by treating their own predictions as ground truth |

### What a good explainer contains

Follow the structure of the existing explainers:

| # | Section | Notes |
|:-:|---------|-------|
| 1 | **One-sentence definition** | State the concept as plainly as possible. No jargon in the definition itself. |
| 2 | **Why it matters** | The real-world consequence if you ignore it. One short paragraph. |
| 3 | **Concrete example** | Drawn from one of the audits in this repo, or from a well-documented real-world case. Show the concept in action — don't just describe it abstractly. |
| 4 | **Detection/measurement code** | A runnable Python snippet. Use `pandas` and `scikit-learn` where possible. |
| 5 | **Limitations or trade-offs** | Every fairness metric has conflicts with other metrics. Acknowledge them honestly. This is what separates a good explainer from a shallow one. |
| 6 | **Related concepts** | Link to other explainers in the folder and relevant projects in the repo. |
| 7 | **Further reading** | 2–3 links to primary sources (papers, journalism, documentation). No link farms. |

```python
# Example structure for a detection snippet
import pandas as pd
from sklearn.metrics import ...

def measure_concept(df, prediction_col, group_col):
    """
    Brief docstring explaining what this returns.
    """
    # your code here
    return result
```

**File naming:** `explainers/your-concept-name.md` — lowercase, hyphens, one file per concept.

The existing explainers are the bar. They define the concept clearly, prove it with real numbers or runnable simulations, give you code to detect or apply it yourself, and explain why it exists structurally. Your explainer should do the same.

### Updating the README

Add your explainer to the Explainers table in `README.md`:

```markdown
| [Your Concept](explainers/your-concept-name.md) | One-line description of what it explains |
```

---

## Submitting

### An audit

1. Fork the repo
2. Create a branch: `git checkout -b audit/your-domain`
3. Add your folder with both scripts, the dataset, and both screenshots
4. Add your notebook to `notebooks/` (if you wrote one)
5. Update `README.md`
6. Open a PR titled: `Audit: HMDA Mortgage Lending Bias`

Include in the PR description: dataset source, bias type, before/after fairness gap numbers, proxy variables found and why you dropped them, and whether you included a notebook.

### An explainer

1. Fork the repo
2. Create a branch: `git checkout -b explainer/your-concept`
3. Add your `.md` file to `explainers/`
4. Update the Explainers table in `README.md`
5. Open a PR titled: `Explainer: Predictive Parity`

Include in the PR description: what concept you're explaining and why it's worth adding.

---

## What Won't Be Merged

**Audits**
- Synthetic or toy datasets — real data only
- Missing `random_state=42` or inconsistent train/test split
- Fair models that achieve parity by tanking accuracy to near-random
- No proxy variable analysis (unless you document why none exist)
- Screenshots saved as `.jpg` or `.jpeg` — PNG only
- Datasets requiring login or payment to access

**Notebooks**
- Proxy variable section skipped
- Different colour palette or styling from the rest of the repo
- Sequential numbering convention not followed

**Explainers**
- Concept defined but not demonstrated with real data or code
- No acknowledgment of limitations or trade-offs
- Toy or invented examples as the primary illustration
- Concepts already covered: proxy variables, equalized odds, sampling bias, SHAP values, disparate impact, disparate treatment, fairness metric conflicts, calibration, demographic parity, feedback loop bias

---

*All datasets used in this project are publicly available. Fair Code is for educational and awareness purposes.*
