# Changelog

All notable changes to Fair Code are documented here.

---

## [1.1.6] — 27 Jun 2026
### Added
- Explainer: What Is a Confounding Variable? — `confounding-variable.md` created, added to `index.html`, `README.md`, and `CONTRIBUTING.md`
  - Full explainer covering how a third variable that independently causes both an input feature and an outcome creates spurious statistical associations that survive protected-attribute removal — and how to distinguish confounders from proxy variables and colliders
  - Proxy vs. confounder distinction table showing the difference in mechanism, causal direction, and correct mitigation strategy
  - Real-world proof anchored to Audit 01 (COMPAS): dropping `race` alone leaves the Black/White fairness gap at ~84%; removing both `race` and the confounder `CustodyStatus` reduces the gap from 86.77% to 15.69% (71% reduction)
  - Detection code: `check_confounding()` — chi-squared marginal association test, stratified analysis within confounder levels, and optional confounder-vs-protected-attribute association test using `scipy.stats.chi2_contingency`
  - Five numbered limitations: effect modification vs. confounding, unmeasured confounders, collider bias from over-adjustment, residual bias after removal, and variance amplification from propensity adjustment
  - Cross-links to proxy-variables, counterfactual-fairness, disparate-impact, and feedback-loop-bias explainers; related project links to COMPAS, Benefits Denial, and Healthcare Readmission audit folders
  - Further reading: Pearl *Causality* (2009, Cambridge), Obermeyer et al. *Science* (2019), VanderWeele & Shpitser *Annals of Statistics* (2013)
  - Roadmap updated on website
### Changed
- `README.md`: `confounding-variable.md` added to explainers table, repository structure tree, and What's Next checklist; explainer count updated 22 → 23
- `CONTRIBUTING.md`: `confounding-variable.md` added to existing explainers table

---

## [1.1.5] — 14 Jun 2026
### Added
- Explainer: The Biggest Myth About AI Objectivity — `ai-objectivity-myth.md` created, added to `index.html`, `README.md`, and `CONTRIBUTING.md`
  - Full explainer covering the false belief that statistical models are inherently neutral because they aren't human, and why "it's just math" fails as a defense once a model is trained on historically biased data
  - Three load-bearing assumptions broken down: "statistics don't have opinions," "removing the protected attribute removes the bias," and "high accuracy means the model is correct"
  - Real-world proof anchored to Audit 01 (COMPAS): an 86.77% fairness gap in a tool marketed as a neutral, statistically validated risk score used in court decisions for over a million people a year, reduced to 15.69% (71% reduction) only after removing both `race` and the proxy `CustodyStatus`
  - Detection code: `audit_objectivity_claim()` — computes per-group positive prediction rates and the resulting fairness gap against a configurable threshold; `find_features_explaining_gap()` — chi-squared and Pearson correlation proxy screen against a protected attribute
  - Four numbered limitations: audits as snapshots not guarantees, objectivity vs. explainability, the myth surviving relocation to fairness-metric choice, and the myth re-forming around the next model after one audit
  - Cross-links to ml-bias, proxy-variables, label-bias, and how-ai-detects-patterns explainers; related project links to COMPAS, Benefits Denial, and Healthcare Readmission audit folders
  - Further reading: O'Neil *Weapons of Math Destruction* (2016), Angwin et al. ProPublica *Machine Bias* (2016), Barocas, Hardt & Narayanan (fairmlbook.org)
  - Nav dropdown (desktop + mobile), ticker strips, and roadmap updated on website
### Changed
- `README.md`: `ai-objectivity-myth.md` added to explainers table, repository structure tree, and What's Next checklist
- `CONTRIBUTING.md`: `ai-objectivity-myth.md` added to existing explainers table

---

## [1.1.4] — 13 Jun 2026
### Added
- Explainer: What Is Distribution Shift? — `distribution-shift.md` created, added to `index.html`, `README.md`, and `CONTRIBUTING.md`
  - Full explainer covering how a model's learned patterns stop matching reality once production data diverges from training data, breaking the assumption that a fairness audit done once stays valid
  - Three-part taxonomy: covariate shift (P(X) changes), label shift (P(Y) changes), and concept drift (P(Y|X) changes)
  - Real-world proof anchored to Audit 06 (Healthcare Readmission): the 1999-2008 pooled dataset spans payer mix and discharge practice changes that can shift `payer_code` distributions enough to alter the race-related fairness gap without any model retraining
  - Detection code: `detect_covariate_shift()` — KS test for continuous features and chi-squared for categorical features, comparing reference vs. current distributions; `detect_label_shift()` — chi-squared comparison of outcome rate distributions across time periods
  - Five numbered limitations: statistical vs. practical significance, drift direction vs. fairness direction, concept drift's invisibility to input tests, arbitrary reference window choice, and small-subgroup statistical instability
  - Cross-links to sampling-bias, feedback-loop-bias, data-leakage, and ml-bias explainers; related project links to Healthcare Readmission and German Credit Lending audit folders
  - Further reading: Quiñonero-Candela et al. (2009, MIT Press), Lipton et al. *ICML* (2018), Rabanser et al. *NeurIPS* (2019)
  - Nav dropdown (desktop + mobile), ticker strips, and roadmap updated on website
### Changed
- `README.md`: `distribution-shift.md` added to explainers table, repository structure tree, and What's Next checklist
- `CONTRIBUTING.md`: `distribution-shift.md` added to existing explainers table

---

## [1.1.3] — 12 Jun 2026
### Added
- Explainer: How AI Detects Patterns — `how-ai-detects-patterns.md` created, added to `index.html`, `README.md`, and `CONTRIBUTING.md`
  - Full explainer covering how a Random Forest Classifier detects patterns through three mechanisms: feature-threshold splitting, aggregation across trees, and feature importance ranking
  - Three-part mechanism breakdown showing why the model has no built-in distinction between a causal pattern and a discriminatory one
  - Real-world proof anchored to Audit 01 (COMPAS): `race` (0.18 importance) and `CustodyStatus` (0.31 importance) both score highly because both correlate with the recidivism label; removing both reduces the Black/White fairness gap from 86.77% to 15.69% (71% reduction)
  - Detection code: `get_pattern_reliance()` — extracts and ranks `feature_importances_` from a fitted RandomForestClassifier; `flag_correlated_patterns()` — chi-squared for categorical features and Pearson correlation for continuous ones, flags features correlated with a protected attribute at p < 0.05
  - Four numbered limitations: importance vs. causation, pattern redistribution after feature removal, small-subgroup instability, and the inability of pattern detection to judge legitimacy
  - Cross-links to proxy-variables, neural-networks, shap-values, and proxy-entanglement explainers; related project links to COMPAS, Healthcare Readmission, and AI Fair Recruitment audit folders
  - Further reading: Breiman *Machine Learning* (2001), Lundberg & Lee *NeurIPS* (2017), Barocas, Hardt & Narayanan (fairmlbook.org)
  - Nav dropdown (desktop + mobile), ticker strips, and roadmap updated on website
### Changed
- `README.md`: `how-ai-detects-patterns.md` added to explainers table, repository structure tree, and What's Next checklist
- `CONTRIBUTING.md`: `how-ai-detects-patterns.md` added to existing explainers table

---

## [1.1.2] — 11 Jun 2026
### Added
- Explainer: What Is Data Leakage? — `data-leakage.md` created, added to `index.html`, `README.md`, and `CONTRIBUTING.md`
  - Full explainer covering the two primary forms: target leakage (features that encode downstream effects of the outcome being predicted) and train-test contamination (preprocessing, feature selection, or aggregation run before the train/test split)
  - Four-row domain table: credit default, healthcare readmission, criminal justice, and insurance denial — each with the specific leaking feature and the causal reason it is leakage
  - Real-world proof anchored to Audit 01 (COMPAS): `CustodyStatus` as a leaking proxy — encodes prior system contact, which encodes historical over-policing; removing it alongside `race` reduces the Black/White fairness gap from 86.77% to 15.69% (71% reduction)
  - Detection code: `detect_target_leakage()` — point-biserial correlation for continuous features and Cramér's V for categorical ones, with configurable threshold flag; `check_preprocessing_leakage()` — fits a StandardScaler on train-only, then measures train/test mean deviation to surface splits that were contaminated before fitting
  - Five numbered limitations: correlation vs. causation, aggregate feature leakage, time-series temporal splitting requirement, SMOTE application order, and the insufficiency of high test scores as proof of clean data
  - Cross-links to proxy-variables, label-bias, sampling-bias, ml-bias, and ai-hallucinations explainers; related project links to COMPAS, Healthcare Readmission, and Benefits Denial audit folders
  - Further reading: Kaufman et al. *ACM TKDD* (2012), Kapoor & Narayanan *Patterns* (2023), Nisbet et al. *Handbook of Statistical Analysis* (2018)
  - Nav dropdown (desktop + mobile), ticker strips, and roadmap updated on website
### Changed
- `README.md`: `data-leakage.md` added to explainers table, repository structure tree, and What's Next checklist
- `CONTRIBUTING.md`: `data-leakage.md` added to existing explainers table

---

## [1.1.1] — 10 Jun 2026
### Added
- Explainer: What Is Machine Learning Bias? — `ml-bias.md` created, added to `index.html`, `README.md`, and `CONTRIBUTING.md`
  - Full explainer covering the four entry points through which bias enters a model: training data bias (sampling misrepresentation), label bias (historical human decisions inherited by the target variable), proxy variables (protected signal surviving attribute removal via correlated features), and feedback loop bias (bias compounding across retraining cycles)
  - Two-axis classification: disparate treatment (protected attribute used directly) vs. disparate impact (structural outcome disparity without direct use), with cross-links to both dedicated explainers
  - Real-world proof anchored to Audit 01 (COMPAS): all four entry points demonstrated in a single production system — over-policing in training distribution, re-arrest as a biased label, `CustodyStatus` as a proxy for race, and feedback loop risk from score-influenced detention → reoffending → retraining
  - Detection code: `demographic_parity_report()` for measuring group-level positive prediction rate gaps with automatic threshold flags (>20% likely Four-Fifths Rule breach, >5% proxy analysis recommended); `check_proxy()` chi-squared test for candidate proxy screening
  - Fairness metric comparison table: demographic parity vs. equalized odds vs. predictive parity — with cross-link to [Why Fairness Metrics Conflict](fairness-metric-conflicts.md)
  - Limitations: bias reduction vs. elimination, demographic label requirement for auditing, metric appropriateness by domain
  - Cross-links to all eight related explainers and four related audits (COMPAS, AI Fair Recruitment, German Credit Lending, Benefits Denial)
  - Further reading: Barocas, Hardt & Narayanan *Fairness and Machine Learning* (fairmlbook.org), ProPublica *Machine Bias* (2016), Obermeyer et al. *Science* (2019)
  - Nav dropdown (desktop + mobile), ticker strips, and roadmap updated on website
### Changed
- `README.md`: `ml-bias.md` added to explainers table, repository structure tree, and What's Next checklist
- `CONTRIBUTING.md`: `ml-bias.md` added to existing explainers table

---

## [1.0.5] — 9 Jun 2026
### Added
- Explainer: Proxy Entanglement — `proxy-entanglement.md` created (PR #49, commits 475de938, 64a90772), added to `index.html`, `README.md`, and `CONTRIBUTING.md` (commits c018d8e8, 476a2771, 46d534fa)
  - Full explainer covering proxy entanglement as the failure mode where multiple correlated features encode the same protected signal through independent administrative channels, requiring cluster-level removal rather than one-variable-at-a-time removal
  - Real-world proof anchored to Audit 06 (Healthcare Readmission): `payer_code` (Medicaid rate encodes race: Hispanic 9.0%, AfricanAmerican 5.5%, Caucasian 2.7%), `discharge_disposition_id` (SNF access: Caucasian 17.3% vs AfricanAmerican 10.7%), `medical_specialty` (insurance access and geography), and `number_inpatient` (prior hospitalisation count: AfricanAmerican 0.70 vs Asian 0.48) identified as an entangled cluster sharing a common causal root in structural inequality
  - Results: removing the full cluster produces 25% reduction in race gap and 68% reduction in age gap; single-variable removal leaves most of the bias mechanism intact
  - `detect_proxy_entanglement()` detection code: two-pass chi-squared analysis — each candidate proxy tested against the protected attribute first, then confirmed proxies cross-tested against each other to surface the entangled cluster
  - Entangled cluster table (feature → what it encodes → causal root), limitations table (causal root ambiguity, accuracy trade-off, base-rate sensitivity in large datasets, distinction from multicollinearity), takeaway callout, and three further reading links (Obermeyer et al. *Science* 2019, Chiappa & Isaac 2019, Kilbertus et al. 2017)
  - Nav dropdown (desktop + mobile), ticker strips (original and dupe), roadmap, AI Hallucinates footer pills, and RL roadmap item (previously live but missing from roadmap) updated on website
### Changed
- `README.md`: `proxy-entanglement.md` added to explainers table, repository structure tree, and What's Next checklist (commit c018d8e8)
- `CONTRIBUTING.md`: `proxy-entanglement.md` added to existing explainers table (commit 476a2771)

---

## [1.0.4] — 8 Jun 2026
### Added
- Audit 06: Healthcare Readmission — Clinical Bias (Diabetes 130-US Hospitals 1999–2008, 101,766 records)
  - `fair.py` and `unfair.py` added to `Healthcare Readmission/` (commits ba226003, cec4a098)
  - Jupyter notebook: `06_healthcare_readmission_bias_audit.ipynb` (commit 9a8abd07)
  - Protected attributes audited: race, gender, age
  - Proxy variables identified and removed: `payer_code` (Medicaid rate encodes race: Hispanic 9.0%, AfricanAmerican 5.5%, Caucasian 2.7%), `discharge_disposition_id` (SNF access encodes insurance and geography: Caucasian 17.3% vs AfricanAmerican 10.7%), `medical_specialty` (encodes insurance type and geography), `number_inpatient` (prior hospitalisation count encodes preventive care access gap: AfricanAmerican 0.70 vs Asian 0.48)
  - Results: race gap 0.08% → 0.06% (25% reduction), age gap 0.28% → 0.09% (68% reduction), gender gap 0.02% → 0.04% (increased — proxy variables carried no meaningful gender signal; documented honestly)
  - Healthcare Readmission audit added to CI workflow (commit 60b4aa7f)
  - `index.html` updated: project card added with terminal outputs, bias bars, and key insight; desktop and mobile nav updated with `06 — Healthcare Readmission` link (commit d93fd1cf)
### Changed
- `README.md` and `CONTRIBUTING.md` updated: audit 06 added to results table, repository structure tree, projects section, and What's Next checklist (commits eced8281, 3d6f4ead)
- `.gitignore` updated to prevent `.DS_Store` from being committed (commit a175c40c)

---

## [1.0.3] — 7 Jun 2026
### Added
- Explainer: Reinforcement Learning — `reinforcement-learning.md` created by evanjain-dot (PR #48, commit a785ea95), added to `index.html`, `README.md`, and `CONTRIBUTING.md` (commit e3928af7)
  - Full explainer covering the three-part RL loop (state → action → reward → policy), reward function design as a political act, reward hacking, and the credit assignment problem
  - Real-world proof using COMPAS as an RL-adjacent system: biased policy produces 86.77% Black/White fairness gap; removing race + `CustodyStatus` proxy reduces gap to 15.69% (71% reduction)
  - Results table: biased policy vs. race-only removal vs. race + proxy removal
  - Second case: YouTube recommendation engine using watch time as reward signal — documents asymmetric demographic consequences and outrage optimisation
  - `fairness_gap()` detection code with chi-squared proxy check for state representation audit
  - Limitations table: reward misspecification, credit assignment failure, proxy exploitation, political nature of reward asymmetry
  - Further reading: Dressel & Farid (Science Advances, 2018), Sutton & Barto (MIT Press, 2018), Krakovna et al. DeepMind specification gaming catalogue (2020)
  - Nav dropdown (desktop + mobile), ticker, and AI Hallucinates footer pills updated on website
### Changed
- `README.md`: `reinforcement-learning.md` added to explainers table, repository structure tree, and What's Next checklist
- `CONTRIBUTING.md`: `reinforcement-learning.md` added to existing explainers table, folder structure tree, and blocked concepts list
- `.github/workflows/update-changelog.yml` deleted — Dependabot auto-changelog workflow removed (commit d4f1c0bb, PR #47)
- `README.md`: `update-changelog.yml` description removed (commit 63edce9a)
- PR template refined for improved contributor guidance (commit e611e442)

---

## [1.0.2] — 5–6 Jun 2026
### Added
- Explainer: Why AI Hallucinates — `ai-hallucinations.md` created by Shreyash0712 (PR #43), added to `index.html`, `README.md`, and `CONTRIBUTING.md` (commits 928ae7ae, 68c4de61, 46cd32e8)
  - Full explainer covering hallucination as out-of-distribution confidence failure, real-world proof using the Insurance Denial audit (sparse BMI/smoking/diabetic sub-populations), tabular density vs. confidence table, `audit_hallucination_risk()` detection code, four mitigation patterns (retrieval-first, source grounding, adversarial verification, confidence calibration), and limitations (confabulation vs. extrinsic vs. intrinsic hallucination taxonomy, RAG limitations, RLHF over-conservatism)
  - Legally documented real-world case: *Mata v. Avianca, Inc.* (678 F.Supp.3d 443) — ChatGPT-fabricated court citations resulting in federal sanctions
  - Nav dropdown (desktop + mobile), ticker, roadmap, and explainer footer pills updated on website
- Branch protection rules documented in `CONTRIBUTING.md`: PRs required, CI must pass, force pushes blocked, branch deletion restricted (commit 6574b20b)
- First interaction workflow added for issues and PRs (commit 60874af6)
- Dependabot configuration added for Python packages with daily changelog updates (commits fa519387, 82f6b262, 9301061c)
### Changed
- `README.md`: `ai-hallucinations.md` added to explainers table, repository structure tree, and What's Next checklist; dataset structure section refactored (commits 9a0eab2e, 6574b20b)
- `CONTRIBUTING.md`: `ai-hallucinations.md` added to existing explainers table, folder structure tree, and blocked concepts list; branch protection steps documented
- Dependencies bumped by Dependabot: `scikit-learn` ≥ 1.9.0 (PR #41, commit d8c6f9b4), `numpy` ≥ 2.4.6 (PR #39, commit 98efd433), `pandas` ≥ 3.0.3 (PR #38, commit 01e747f5), `matplotlib` ≥ 3.10.9 (PR #37, commit 3fd010cb)

---

## [1.0.1] — 4 Jun 2026
### Added
- Explainer: What Happens Inside a Neural Network — `neural-networks.md` created, added to `index.html`, `README.md`, and `CONTRIBUTING.md` (commits 4ff97866, c1023432, d372c002, f997fc52)
  - Full explainer covering forward pass, weights, loss function, backpropagation, and the three-part training loop
  - Real-world proof using the AI Fair Recruitment dataset: 20.9% → 0.1% gender gap after removing gender + age proxy
  - SHAP inspection code, what-each-component-does table, limitations table, and further reading
  - Nav dropdown (desktop + mobile), ticker, roadmap, and counterfactual fairness footer pills updated on website
### Changed
- `README.md`: neural-networks.md added to explainers table, repository structure tree, and What's Next checklist
- `CONTRIBUTING.md`: neural-networks.md added to existing explainers table, folder structure tree, and blocked concepts list

---

## [0.8.1] — 2 Jun 2026
### Added
- Explainer: Counterfactual Fairness — `counterfactual-fairness.md` created by evanjain-dot (PR #31), added to `index.html`, `README.md`, and `CONTRIBUTING.md`
  - Full explainer with SCM formal definition, COMPAS policing causal chain proof, detection code (biased model → counterfactual audit → fair model fix), IF vs CF comparison table, limitations, and further reading
  - Nav dropdown, mobile nav, and roadmap updated on website
### Changed
- `README.md` updated: counterfactual fairness added to explainers table, repository structure tree, and What's Next checklist
- `CONTRIBUTING.md` updated: counterfactual fairness added to existing explainers table and blocked concepts list
- `index.html`: CI badge added to README (commit 63c49cd8); CONTRIBUTING.md CI audit checks documented (commit 37f960c6); README formatting fixes (commit 646a3560)

---

## [0.8.0] — 2 Jun 2026
### Added
- CI pipeline: `.github/workflows/audits.yml` — runs all audit scripts (`unfair.py` and `fair.py`) automatically on every push and pull request (PR by Anjali Tiwari)
### Changed
- Dataset paths standardised across all audit scripts so every script resolves its dataset relative to its own file location, scripts now run correctly from the repo root, from within their own folder, and in CI (PR by Anjali Tiwari)

---

## [0.7.0] — 1 Jun 2026
### Added
- Explainer: Individual Fairness — added to index.html, README, and concepts covered
### Fixed
- HTML section closing tag bug in index.html (impact section broken)
- Mobile nav max-height increased for full scrollability on small screens
- Dataset path corrected in AI Fair Recruitment `fair.py` / `unfair.py` scripts (PR by Anjali Tiwari)
### Changed
- Code of Conduct revised for clarity and inclusivity
- scipy and shap package versions corrected in requirements.txt
- `CHANGELOG.md` added to project structure

---

## [0.6.0] — 31 May 2026
### Added
- Explainer: Label Bias — added to index.html, explainers directory, and CONTRIBUTING.md
### Changed
- README updated with new bias topics and explainers

---

## [0.5.1] — 30 May 2026
### Changed
- CONTRIBUTING.md revised for improved instructions
- README refactored for clarity and formatting

---

## [0.5.0] — 28–29 May 2026
### Added
- Explainer: Disparate Treatment — added to index.html, README, and CONTRIBUTING.md
- Explainer: Feedback Loop Bias — added to index.html, README, and CONTRIBUTING.md
- Welfare/Benefits Denial project button and project data on website
### Changed
- README updated with feedback loop bias and disparate treatment explainers

---

## [0.4.2] — 26–27 May 2026
### Added
- Explainer: Demographic Parity — added to index.html and CONTRIBUTING.md
- Star History section added to README
- Vercel deployment badge added to README
### Changed
- README formatting fixes

---

## [0.4.1] — 24 May 2026
### Added
- GitHub Issue Templates: bug report, new audit proposal, new explainer proposal (YAML)
- Pull request template
### Changed
- CONTRIBUTING.md updated with templates information
- README updated with PR and issue template references

---

## [0.4.0] — 21–23 May 2026
### Added
- Explainer: Calibration — `calibration.md`, added to index.html, README, CONTRIBUTING.md
- Explainer: Fairness Metric Conflicts — `fairness-metric-conflicts.md`
- Search placeholder and explainer card text updated on website
### Fixed
- Formatting fixes in CONTRIBUTING.md and README.md
### Changed
- Merged PR #26 (sofiya-iii): file additions

---

## [0.3.0] — 22 May 2026
### Added
- Audit 05: Benefits Denial (UCI Adult Census Income, 48,842 records)
  - `fair.py` and `unfair.py` for welfare eligibility bias
  - Dataset added
  - Jupyter notebook: `05_benefits_denial_bias_audit.ipynb`
  - README updated with Benefits Denial section and results
### Changed
- CONTRIBUTING.md updated for Benefits Denial audit

---

## [0.2.2] — 21 May 2026
### Added
- All five Jupyter notebooks added (`01` through `05`)
- `CITATION.cff` for project citation guidelines
- `SECURITY.md` for vulnerability reporting policy
- `requirements.txt` updated with full dependencies and instructions
### Fixed
- Various small website bugs
- Accessibility improvements and style refactors in index.html
- Cursor style set to pointer for navigation items

---

## [0.2.1] — 19–20 May 2026
### Added
- Explainer: Disparate Impact (80% Rule) — added to index.html, README, CONTRIBUTING.md
- Explainer: Equalized Odds — merged via PR #13 (TanishGoyal-Dev)
- Explainer: SHAP Values — merged via PR #12 (shwetagupta1234)
- Search bar with filtering for projects and explainers
- Copy and share buttons on website
- Back-to-top button for mobile
### Changed
- Website styles refactored: light mode, dark mode, navigation dropdowns
- Navigation improved with social media links and dropdown menus
- `requirements.txt` updated with pandas and scikit-learn

---

## [0.2.0] — 18–19 May 2026
### Added
- Audit 04: Insurance Denial (Kaggle, 1,340 records)
  - `fair.py`, `unfair.py`, dataset, and proof images
  - README and CONTRIBUTING.md updated
- Explainer: Sampling Bias — merged via PR #2 (evanjain-dot)
- `shap-values.md` added to explainers directory
- `CODE_OF_CONDUCT.md` added
### Changed
- CONTRIBUTING.md refined for explainer and audit submission guidelines
- README revised for project names, structure, and clarity

---

## [0.1.0] — 17–18 May 2026
### Added
- Audit 03: German Credit Lending Bias — merged via PR #1 (Aarav Sharma)
  - Random Forest model, dataset, `fair.py` / `unfair.py`
- Explainer section added to website with responsive styles
- Navigation dropdowns implemented in index.html
- Social media links added to navigation
### Changed
- README revised for project overview and results
- CONTRIBUTING.md created with audit guidelines

---

## [0.0.0] — 13–16 May 2026
### Added
- Audit 01: COMPAS Criminal Justice Bias (ProPublica, 70k+ records)
  - `fair.py`, `unfair.py`, dataset, proof images
- Audit 02: AI Fair Recruitment Bias (Kaggle)
  - `fair.py`, `unfair.py`, dataset, proof images
- Interactive website (`index.html`) deployed at fair-code-five.vercel.app
  - Light mode, mobile-responsive layout
- README with project overview, results table, and methodology