# Fair Code — Public Roadmap

This is the public roadmap for Fair Code. It tracks what has been built, what is actively in progress, and what comes next.

Last updated: June 2026

---

## Where We Are

Fair Code is an open-source responsible AI platform explaining algorithmic bias, fairness, and AI accountability through code audits, explainers, healthcare-bias case studies, and contributor-led GitHub documentation.

**Current traction (June 2026):**
- 27+ GitHub stars
- 7+ external contributors
- 8+ forks
- 10K+ combined social reach (Instagram + LinkedIn)
- 6 published code audits
- 22 published explainers
- CI pipeline running on every push and PR

---

## Phase 1 — Bias Glossary and Beginner Explainers ✅

**Status: Complete**

Build the foundational vocabulary and explain core fairness concepts clearly enough for a non-technical reader.

- [x] Proxy Variables
- [x] Equalized Odds
- [x] Sampling Bias
- [x] SHAP Values
- [x] Disparate Impact (The 80% Rule)
- [x] Disparate Treatment
- [x] Why Fairness Metrics Conflict
- [x] Calibration
- [x] Demographic Parity
- [x] Feedback Loop Bias
- [x] Label Bias
- [x] Individual Fairness
- [x] Counterfactual Fairness
- [x] What Happens Inside a Neural Network
- [x] Why AI Hallucinates
- [x] What Is Reinforcement Learning
- [x] Proxy Entanglement
- [x] What Is Machine Learning Bias
- [x] What Is Data Leakage
- [x] How AI Detects Patterns
- [x] What Is Distribution Shift
- [x] The Biggest Myth About AI Objectivity

---

## Phase 2 — Healthcare AI Bias Examples ✅ / 🔄 In Progress

**Status: Audits complete — explainers expanding**

Publish healthcare-specific bias audits and explainers that show how AI discrimination shows up in clinical and insurance contexts.

- [x] Insurance Denial bias audit
- [x] Benefits Denial bias audit
- [x] Healthcare Readmission bias audit
- [x] Jupyter notebooks for all three healthcare audits
- [ ] Explainer: Why Accuracy Is Not Enough in Healthcare AI
- [ ] Explainer: False Positives and False Negatives in Medical Risk Models
- [ ] Case study write-up: Insurance Denial Bias (standalone explainer page)
- [ ] Case study write-up: Benefits Denial Bias (standalone explainer page)
- [ ] Case study write-up: Healthcare Readmission Bias (standalone explainer page)

---

## Phase 3 — Code Audits 🔄 In Progress

**Status: 6 of 8 planned audits published**

Each audit follows the same pipeline: train a biased model → measure the fairness gap → remove proxies → retrain → measure again.

- [x] COMPAS — Criminal Justice Bias
- [x] AI Fair Recruitment — Hiring Bias
- [x] German Credit Lending — Lending Bias
- [x] Insurance Denial — Healthcare Bias
- [x] Benefits Denial — Welfare Eligibility Bias
- [x] Healthcare Readmission — Clinical Bias
- [ ] HMDA Mortgage Lending Bias
- [ ] Facial Recognition Accuracy Gaps (MIT Gender Shades methodology)
- [ ] LLM bias audit

---

## Phase 4 — Contributor Expansion 🔄 In Progress

**Status: Active — 7 external contributors**

Goal: grow to 10+ contributors with quality-controlled contributions.

- [x] CONTRIBUTING.md
- [x] Issue templates (bug report, new audit, new explainer)
- [x] PR template
- [x] CODE_OF_CONDUCT.md
- [x] CI pipeline (all audit scripts run on push/PR)
- [x] Good-first-issue and help-wanted labels
- [x] First-interaction workflow (greets new contributors)
- [ ] 10–15 labelled issues open at all times
- [ ] Contributor list in README
- [ ] METRICS.md tracking contributor growth weekly

---

## Phase 5 — Fairness Metrics and Notebooks ⏳ Planned

**Status: Planned**

Go deeper on measurement — fairness dashboards, interactive notebooks, and statistical tools for auditors.

- [ ] Fairness audit web dashboard
- [ ] AIF360 / Fairlearn integration examples
- [ ] Intersectional bias notebook (auditing across multiple protected attributes simultaneously)
- [ ] Statistical significance testing for fairness gaps
- [ ] Bias detection utility library (`faircode/` module)

---

## Content Schedule

**During school:**
- Monday: AI bias explainer
- Wednesday: Healthcare AI / fairness example
- Friday: Code audit or project update

**During holidays:**
- Monday–Friday posting acceptable if sustainable

---

## How to Contribute

See [CONTRIBUTING.md](CONTRIBUTING.md) to claim an open issue or propose a new audit or explainer.

If you want to take on a Phase 3 audit (HMDA, facial recognition, or LLM bias), open an issue first with a brief description of your approach and the dataset you plan to use.

---

*Fair Code is maintained by [Yash Kewlani](https://github.com/yakew7). Follow the project at [@thefaircodeproject](https://instagram.com/thefaircodeproject).*
