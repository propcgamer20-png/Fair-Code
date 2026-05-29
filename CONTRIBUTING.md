# Contributing to Fair Code

Thanks for wanting to add to this. There are two ways to contribute: **audits** and **explainers**.

An **audit** finds a real dataset where an AI system produces measurably biased outcomes, proves it with code, fixes it, and proves that too. An **explainer** takes a concept in algorithmic fairness and makes it concrete — with a clear definition, real examples, and runnable detection code.

Both follow strict structure requirements. Consistency is what makes the repo credible.

---

## Before You Start

Check the [roadmap in the README](README.md#whats-next) and open an Issue before doing any work. If two people are working on the same thing at the same time, that's wasted effort. The Issue is just a one-liner:

> *"Taking on HMDA mortgage lending bias — starting with the federal HMDA dataset."*

or

> *"Writing an explainer on demographic parity."*

---

## Folder Structure

Every audit lives in its own top-level folder. Name it after the domain, not the dataset. Each audit also has a corresponding notebook in `notebooks/`.

```
Fair-Code/
├── .github/
│   ├── PULL_REQUEST_TEMPLATE.md         ← fill this out when opening a PR
│   └── ISSUE_TEMPLATE/
│       ├── bug_report.yml               ← report a broken script or wrong result
│       ├── new_audit.yml                ← claim a new audit before you start
│       └── new_explainer.yml            ← claim a new explainer before you start
├── COMPAS/                          ← existing
├── AI Fair Recruitment/             ← existing
├── German Credit Lending/           ← existing
├── Insurance Denial/                ← existing
├── Benefits Denial/                 ← existing
├── Your-Domain-Here/                ← your new audit
│   ├── unfair.py
│   ├── fair.py
│   ├── your-dataset.csv
│   ├── unfair.png
│   └── fair.png
├── notebooks/
│   ├── 01_compas_bias_audit.ipynb           ← existing
│   ├── 02_hiring_bias_audit.ipynb           ← existing
│   ├── 03_german_credit_bias_audit.ipynb    ← existing
│   ├── 04_insurance_denial_bias_audit.ipynb ← existing
│   ├── 05_benefits_denial_bias_audit.ipynb  ← existing
│   └── 06_your_domain_bias_audit.ipynb      ← your new notebook (optional but appreciated)
├── explainers/
│   ├── proxy-variables.md           ← existing
│   ├── equalized-odds.md            ← existing
│   ├── sampling-bias.md             ← existing
│   ├── shap-values.md               ← existing
│   ├── disparate-impact.md          ← existing
│   ├── disparate-treatment.md       ← existing
│   ├── fairness-metric-conflicts.md ← existing
│   ├── calibration.md               ← existing
│   ├── demographic-parity.md        ← existing
│   ├── feedback-loop-bias.md        ← existing
│   └── your-concept-name.md         ← your new explainer
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── SECURITY.md
├── CITATION.cff
├── index.html
└── requirements.txt
```

No subfolders within audit folders, no extra files. Keep it flat.

---

## The Two Scripts

Every audit has exactly two scripts. Nothing more.

### `unfair.py` — the biased model

This script demonstrates the bias. It must:

- Load the dataset
- Train a Random Forest Classifier with protected attributes included (race, gender, age, or whatever applies)
- Print results in this exact format:

```
--- BIASED MODEL RESULTS ---

[Group A] [Outcome] Rate: XX.XX%
[Group B] [Outcome] Rate: XX.XX%

Fairness Gap: XX.XX%
```

Use `random_state=42` and an 80/20 train/test split. Both are non-negotiable — they make results reproducible.

### `fair.py` — the mitigated model

This script fixes the bias. It must:

- Drop the protected attribute(s)
- Drop any identified proxy variables (see below)
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

If you can, add a Jupyter notebook to the `notebooks/` folder that walks through your full audit step by step. It's not required to get your PR merged, but it makes the audit significantly more useful for people who want to understand the reasoning, not just run the scripts.

Number it sequentially after the existing ones: `06_your_domain_bias_audit.ipynb`.

### What a good audit notebook contains

Follow the structure of the existing notebooks:

**1. Title cell** — audit number, domain, and the one-sentence hook (the stat that makes it real).

**2. Setup** — imports and consistent plot styling. Copy the `plt.rcParams` block from an existing notebook — all notebooks use the same colour palette (`ACCENT`, `DANGER`, `SAFE`, `MUTED`) so the repo looks coherent.

**3. Load and explore the dataset** — load the CSV, print shape and columns, show the raw disparity with a plot before any model is trained.

**4. Proxy variable identification** — run the chi-squared test (for categorical features) or Pearson correlation (for continuous) and show the cross-tabulation that proves the correlation. This is the most important section. Don't skip it.

**5. Train the biased model** — use the same `random_state=42` and 80/20 split as the scripts. Print the same output format as `unfair.py`.

**6. Train the fair model** — remove the protected attribute(s) and proxy variable(s). Print the same output format as `fair.py`.

**7. Compare results** — side-by-side bar charts using the project colour palette. Print the before/after summary with reduction percentage.

**8. Key Insight cell** — a markdown cell, not code. One short paragraph answering: *why did the bias exist, and why does the fix work?* Plain language. No jargon.

### Notebook file naming

```
notebooks/06_your_domain_bias_audit.ipynb
```

Lowercase, underscores, sequential number prefix. Match the existing naming convention exactly.

---

## Proxy Variables

This is the most important part of the audit. Removing the protected attribute alone is rarely enough.

A proxy variable is a feature that correlates with the protected attribute strongly enough to smuggle the bias back through the model — even after you've dropped race or gender directly. In the COMPAS audit, `CustodyStatus` was a proxy for race because of historical over-policing patterns. In the German Credit Lending audit, `employment` (tenure) was a proxy for age because a 24-year-old structurally cannot have 10 years of work history. In the Insurance Denial audit, `bmi`, `smoker`, and `diabetic` were proxies for race and class because of structural disparities in American healthcare. In the Benefits Denial audit, `relationship` (Husband/Wife), `marital.status`, `hours.per.week`, and `occupation` were all proxies for sex or race — family roles encode sex perfectly, the spousal rate reconstructs sex through marriage patterns, the hours gap reflects caregiving burdens not work capacity, and occupational segregation encodes race through labour market history.

You must identify and document your proxy variables. To find them:

```python
import pandas as pd

df = pd.read_csv('your-dataset.csv')

# For continuous variables: Pearson correlation
print(df[['potential_proxy_column', 'protected_attribute']].corr())

# For categorical variables: cross-tabulation
print(pd.crosstab(df['potential_proxy'], df['protected_attribute'], normalize='columns').round(3))
```

If a feature shows strong correlation with the protected attribute and you include it in the fair model, explain why (i.e. it's a genuine merit signal, not a proxy). If you drop it, document it.

---

## The Output Screenshots

After running both scripts, take a terminal screenshot and save it as a `.png`:

- `unfair.png` — terminal output of `unfair.py`
- `fair.png` — terminal output of `fair.py`

These go in your audit folder alongside the scripts. They're the visual proof. **PNG only — not JPG or JPEG.**

---

## Dataset Requirements

- Must be **publicly available** with a clear source (Kaggle, government data, ProPublica, academic release, etc.)
- Must contain **real demographic data** — synthetic datasets don't demonstrate real-world bias
- Include the dataset file in your folder if it's under ~50MB. If it's larger, add a `DATA.md` with a direct download link and instructions

Do not include datasets that require login, payment, or a data use agreement to access.

---

## Updating the README

Add your audit to the results table at the top of `README.md`:

```markdown
| [Your Domain](#link-to-section) | Bias Type | Protected Attribute | Gap Before | Gap After | Reduction |
```

Then add a full section below the existing projects following the same pattern:

1. The opening quote
2. Dataset description and real-world context
3. **The Problem** — biased results table + what features caused it
4. Code snippet showing what you dropped and why
5. **The Fix** — mitigated results table
6. **Key Insight** paragraph (required — see below)
7. A link to your notebook: `📓 **[Full notebook walkthrough →](notebooks/05_your_domain_bias_audit.ipynb)**` (if you wrote one)

**The Key Insight paragraph is required.** It must answer: *why did the bias exist, and why does the fix work?* One short paragraph, plain language, no jargon.

---

## Fairness Metric

All audits use **Demographic Parity** as the primary metric: the difference in positive prediction rates between demographic groups.

If your domain genuinely requires a different metric (equalized odds, predictive parity, etc.), open an Issue to discuss it first before submitting. See the [Equalized Odds explainer](explainers/equalized-odds.md) for a full breakdown of when and why that metric applies.

---

## Contributing an Explainer

You don't have to audit a dataset to contribute. If you can explain a concept in algorithmic fairness clearly — with real examples and runnable code — an explainer belongs here too.

Explainers live in the `explainers/` folder at the repo root. The existing ones are:

- `proxy-variables.md` — why AI stays biased even after you remove protected attributes
- `equalized-odds.md` — the fairness metric that checks both types of errors across demographic groups
- `sampling-bias.md` — why your training data may not represent the people your model affects
- `shap-values.md` — how to explain individual AI decisions and use that to catch bias
- `disparate-impact.md` — the legal 80% rule that flags discriminatory selection in hiring, lending, and insurance
- `disparate-treatment.md` — intentional discrimination: when a protected attribute or its proxy is a direct model input, and the two-stage audit (treatment → impact) to detect and remove it
- `fairness-metric-conflicts.md` — the proven mathematical impossibility of satisfying demographic parity, equalized odds, and predictive parity simultaneously
- `calibration.md` — why a model can be equally accurate for all groups and still treat them unequally, including differential calibration and the Chouldechova impossibility result
- `demographic-parity.md` — the foundational fairness metric: equal positive prediction rates across groups, when it applies, and what it misses
- `feedback-loop-bias.md` — why AI systems amplify bias across retraining cycles by treating their own predictions as ground truth, and how to detect and break the loop

Future ones might cover predictive parity.

### File structure

```
Fair-Code/
└── explainers/
    ├── proxy-variables.md           ← existing
    ├── equalized-odds.md            ← existing
    ├── sampling-bias.md             ← existing
    ├── shap-values.md               ← existing
    ├── disparate-impact.md          ← existing
    ├── disparate-treatment.md       ← existing
    ├── fairness-metric-conflicts.md ← existing
    ├── calibration.md               ← existing
    ├── demographic-parity.md        ← existing
    └── your-concept-name.md         ← your new explainer
```

One file per concept. Name it after the concept in lowercase with hyphens: `demographic-parity.md`, `predictive-parity.md`, etc.

### What a good explainer contains

Follow the structure of the existing explainers:

**1. One-sentence definition** — what is the concept, stated as plainly as possible. No jargon in the definition itself.

**2. Why it matters** — the real-world consequence if you ignore it. One short paragraph.

**3. Concrete example** — ideally drawn from one of the audits in this repo (COMPAS, AI Fair Recruitment, German Credit Lending, Insurance Denial), or from a well-documented real-world case. The example should show the concept in action, not just describe it abstractly.

**4. Detection or measurement code** — a runnable Python snippet demonstrating how to actually apply the concept. Use `pandas` and `scikit-learn` where possible to stay consistent with the rest of the repo.

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

**5. Limitations or trade-offs** — every fairness metric has limitations or conflicts with other metrics. Acknowledge them honestly. This is what separates a good explainer from a shallow one.

**6. Related concepts** — link to other explainers in the folder and to relevant projects in the repo.

**7. Further reading** — 2–3 links to primary sources (papers, journalism, documentation). No link farms.

### The standard to hit

The existing explainers are the bar. They define the concept clearly, prove it with real numbers or runnable simulations, give you code to detect or apply it yourself, and explain why it exists structurally. Your explainer should do the same for its concept.

If you can't show the concept with real data from one of the existing audits, use a well-documented external case with a source link. Do not use invented toy examples as the primary illustration.

### Updating the README

Add your explainer to the Explainers table in `README.md`:

```markdown
| [Your Concept](explainers/your-concept-name.md) | One-line description of what it explains |
```

### Submitting an explainer

1. Fork the repo
2. Create a branch: `git checkout -b explainer/your-concept`
3. Add your `.md` file to `explainers/`
4. Update the Explainers table in `README.md`
5. Open a Pull Request titled: `Explainer: Demographic Parity`

In the PR description, briefly state what concept you're explaining and why it's worth adding to the repo.

---

## Submitting an Audit

1. Fork the repo
2. Create a branch: `git checkout -b audit/your-domain`
3. Add your folder with both scripts, the dataset, and both screenshots
4. If you wrote a notebook, add it to `notebooks/` as `06_your_domain_bias_audit.ipynb`
5. Update `README.md`
6. Open a Pull Request titled: `Audit: HMDA Mortgage Lending Bias`

In the PR description, include:

- What dataset you used and where it's from
- What the bias type is
- The before and after fairness gap numbers
- What proxy variables you found and why you dropped them
- Whether you included a notebook walkthrough

---

## What Won't Be Merged

**Audits:**
- Audits on synthetic or toy datasets
- Scripts that don't produce reproducible results (missing `random_state=42` or inconsistent split)
- Fair models that achieve parity by tanking overall accuracy to near-random
- Audits without identified proxy variables (unless you document why none exist)
- Screenshots saved as `.jpg` or `.jpeg` — use `.png`
- Any dataset that isn't publicly accessible without login or payment

**Notebooks:**
- Notebooks that skip the proxy variable identification section
- Notebooks that use a different colour palette or styling from the rest of the repo
- Notebooks that don't follow the sequential numbering convention

**Explainers:**
- Explainers that only define a concept without demonstrating it with real data or code
- Explainers that don't acknowledge the limitations or trade-offs of the metric/concept
- Toy or invented examples as the primary illustration — use real data
- Explainers on concepts already covered in the folder (check before starting — proxy variables, equalized odds, sampling bias, SHAP values, disparate impact, disparate treatment, fairness metric conflicts, calibration, demographic parity, and feedback loop bias are done)

---

*All datasets used in this project are publicly available. Fair Code is for educational and awareness purposes.*
