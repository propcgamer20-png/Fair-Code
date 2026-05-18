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

Every audit lives in its own top-level folder. Name it after the domain, not the dataset.

```
Fair-Code/
├── COMPAS/                        ← existing
├── Ai Fair recrutment Dataset/    ← existing
├── German Credit Lending/         ← existing
├── Your-Domain-Here/              ← your new audit
│   ├── unfair.py
│   ├── fair.py
│   ├── your-dataset.csv
│   ├── unfair.png
│   └── fair.png
├── explainers/
│   ├── proxy-variables.md         ← existing
│   ├── sampling-bias.md           ← existing
│   └── your-concept-name.md       ← your new explainer
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

## Proxy Variables

This is the most important part of the audit. Removing the protected attribute alone is rarely enough.

A proxy variable is a feature that correlates with the protected attribute strongly enough to smuggle the bias back through the model — even after you've dropped race or gender directly. In the COMPAS audit, `CustodyStatus` was a proxy for race because of historical over-policing patterns. In the German Credit audit, `employment` (tenure) was a proxy for age because a 24-year-old structurally cannot have 10 years of work history.

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

**The Key Insight paragraph is required.** It must answer: *why did the bias exist, and why does the fix work?* One short paragraph, plain language, no jargon.

---

## Fairness Metric

All audits use **Demographic Parity** as the primary metric: the difference in positive prediction rates between demographic groups.

If your domain genuinely requires a different metric (equalized odds, predictive parity, etc.), open an Issue to discuss it first before submitting.

---

## Contributing an Explainer

You don't have to audit a dataset to contribute. If you can explain a concept in algorithmic fairness clearly — with real examples and runnable code — an explainer belongs here too.

Explainers live in the `explainers/` folder at the repo root. The existing ones are `proxy-variables.md` and `sampling-bias.md`. Future ones might cover demographic parity, equalized odds, predictive parity, disparate impact, or fairness metric trade-offs.

### File structure

```
Fair-Code/
└── explainers/
    ├── proxy-variables.md          ← existing
    ├── sampling-bias.md            ← existing
    └── your-concept-name.md        ← your new explainer
```

One file per concept. Name it after the concept in lowercase with hyphens: `demographic-parity.md`, `equalized-odds.md`, etc.

### What a good explainer contains

Follow the structure of `proxy-variables.md` and `sampling-bias.md`:

**1. One-sentence definition** — what is the concept, stated as plainly as possible. No jargon in the definition itself.

**2. Why it matters** — the real-world consequence if you ignore it. One short paragraph.

**3. Concrete example** — ideally drawn from one of the audits in this repo (COMPAS, hiring, German Credit), or from a well-documented real-world case. The example should show the concept in action, not just describe it abstractly.

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

The proxy variables and sampling bias explainers are the bar. They define the concept clearly, prove it with real numbers or runnable simulations, give you code to detect it yourself, and explain why it exists structurally. Your explainer should do the same for its concept.

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
4. Update `README.md`
5. Open a Pull Request titled: `Audit: HMDA Mortgage Lending Bias`

In the PR description, include:

- What dataset you used and where it's from
- What the bias type is
- The before and after fairness gap numbers
- What proxy variables you found and why you dropped them

---

## What Won't Be Merged

**Audits:**
- Audits on synthetic or toy datasets
- Scripts that don't produce reproducible results (missing `random_state=42` or inconsistent split)
- Fair models that achieve parity by tanking overall accuracy to near-random
- Audits without identified proxy variables (unless you document why none exist)
- Screenshots saved as `.jpg` or `.jpeg` — use `.png`
- Any dataset that isn't publicly accessible without login or payment

**Explainers:**
- Explainers that only define a concept without demonstrating it with real data or code
- Explainers that don't acknowledge the limitations or trade-offs of the metric/concept
- Toy or invented examples as the primary illustration — use real data
- Explainers on concepts already covered in the folder (check before starting)

---

*All datasets used in this project are publicly available. Fair Code is for educational and awareness purposes.*
