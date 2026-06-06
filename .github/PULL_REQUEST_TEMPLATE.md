## Summary

<!-- One sentence: e.g. "Adds HMDA mortgage lending bias audit" or "Adds demographic parity explainer" -->

## Type

- [ ] Audit
- [ ] Explainer
- [ ] Bug fix
- [ ] Other

---

## Audit checklist

<!-- Skip this section if you're submitting an explainer or bug fix -->

- [ ] I opened or linked a corresponding issue first
- [ ] The folder is named after the domain, not the dataset
- [ ] `unfair.py` includes protected attributes and prints the required output format
- [ ] `fair.py` removes protected attributes and identified proxy variables
- [ ] Both scripts use `random_state=42` and an 80/20 train/test split
- [ ] Proxy variables were actually tested, not just guessed
- [ ] `unfair.png` and `fair.png` are included as PNG screenshots
- [ ] The dataset is public and accessible without login or payment
- [ ] The dataset file is included, or `DATA.md` is included if the file is too large
- [ ] `README.md` includes the new results row and audit section
- [ ] A notebook was added if the audit benefits from one

**Before fairness gap:** <!-- e.g. 86.77% -->

**After fairness gap:** <!-- e.g. 15.69% -->

**Reduction:** <!-- e.g. 71% -->

**Protected attribute(s):** <!-- e.g. Race -->

**Proxy variables dropped:** <!-- e.g. CustodyStatus -->

---

## Explainer checklist

<!-- Skip this section if you're submitting an audit or bug fix -->

- [ ] The file is in `explainers/` and uses lowercase hyphenated naming
- [ ] It includes a plain-language definition
- [ ] It uses a real example from this repo or a documented real-world case
- [ ] It includes runnable Python detection or measurement code
- [ ] It acknowledges limitations or trade-offs
- [ ] It links to related explainers or repo projects
- [ ] It includes 2-3 primary sources
- [ ] The Explainers table in `README.md` was updated

---

## Linked issue

<!-- Every PR should have a corresponding issue. Example: "Closes #12" -->

Closes #
