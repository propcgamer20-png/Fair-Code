## What does this PR do?

<!-- One sentence. e.g. "Adds HMDA mortgage lending bias audit" or "Adds demographic parity explainer" -->

## Type

- [ ] Audit
- [ ] Explainer
- [ ] Bug fix
- [ ] Other (describe below)

---

## Audit checklist

<!-- Skip this section if you're submitting an explainer or bug fix -->

- [ ] Folder is named after the domain, not the dataset (e.g. `HMDA Mortgage Lending/`, not `hmda_2022/`)
- [ ] `unfair.py` trains with protected attribute(s) included and prints results in the exact required format
- [ ] `fair.py` drops protected attribute(s) and all identified proxy variables, and prints results in the exact required format
- [ ] Both scripts use `random_state=42` and an 80/20 train/test split
- [ ] Proxy variables are identified via chi-squared or Pearson correlation — not just assumed
- [ ] Both `unfair.png` and `fair.png` terminal screenshots are included as `.png` (not `.jpg`)
- [ ] Dataset is publicly accessible without login or payment
- [ ] Dataset file is included (if under ~50MB), or a `DATA.md` with download instructions is included (if larger)
- [ ] README results table is updated with before/after numbers and reduction percentage
- [ ] README audit section is added with: opening quote, dataset context, The Problem, code snippet, The Fix, and Key Insight paragraph
- [ ] Jupyter notebook added to `notebooks/` with sequential number prefix *(optional but appreciated)*

**Before fairness gap:** <!-- e.g. 86.77% -->
**After fairness gap:** <!-- e.g. 15.69% -->
**Reduction:** <!-- e.g. 71% -->
**Protected attribute(s):** <!-- e.g. Race -->
**Proxy variables dropped:** <!-- e.g. CustodyStatus — correlates with race due to over-policing patterns -->

---

## Explainer checklist

<!-- Skip this section if you're submitting an audit or bug fix -->

- [ ] File is in `explainers/` and named in lowercase with hyphens (e.g. `demographic-parity.md`)
- [ ] Includes a one-sentence definition with no jargon
- [ ] Illustrated with real data from an existing audit or a documented external case — not a toy example
- [ ] Includes a runnable Python detection or measurement snippet using pandas/scikit-learn
- [ ] Acknowledges the limitations and trade-offs of the concept
- [ ] Links to related explainers and repo projects
- [ ] Includes 2–3 primary source links (no link farms)
- [ ] README explainers table is updated

---

## Linked issue

<!-- Every PR should have a corresponding issue. e.g. "Closes #12" -->

Closes #
