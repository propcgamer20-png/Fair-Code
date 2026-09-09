# Audit 05: Benefits Denial - Welfare Eligibility Bias - Reproducibility

Part of [Fair Code](../README.md#results-at-a-glance). This documents how to reproduce this audit and the exact numbers to expect. It does not change any result - the figures below are the published, paper-aligned numbers. See [CLAUDE.md](../CLAUDE.md) for the paper-freeze policy.

## Reproducibility checklist

- [ ] Install pinned dependencies: `pip install -r ../requirements-lock.txt` (the exact versions used for the published run), or `pip install -r ../requirements.txt` for loose ranges
- [ ] Randomness is fixed: `random_state: 42` (declared in `audit.yaml`, and used in `unfair.py` / `fair.py`)
- [ ] Split: 80/20 train/test, stratified (`test_size: 0.2`)
- [ ] Run both scripts from the repository root, so dataset paths resolve

## Reproduce

```bash
python3 "Benefits Denial/unfair.py"   # biased baseline (protected attribute included)
python3 "Benefits Denial/fair.py"     # mitigated (protected attribute + proxies dropped)
```

## What the audit controls

- Protected attribute(s): Sex, Race, Origin, Age
- Proxy feature(s) removed in `fair.py`: Relationship, Marital Status, Hours, Occupation, fnlwgt (census sampling weight)
- Fairness metric: Demographic Parity (difference in positive-prediction rate between groups)

## Expected result (published, paper-aligned)

| Group | Gap, biased (`unfair.py`) | Gap, mitigated (`fair.py`) | Reduction |
|-------|--------------------------:|---------------------------:|----------:|
| Sex | 18.00% | 8.52% | 53% |
| Race | 12.75% | 6.90% | 46% |
| Origin | 4.40% | 0.52% | 88% |

These match the "Results at a Glance" table in the [main README](../README.md#results-at-a-glance) and the frozen snapshot in `paper/results-frozen/`. The scripts are deterministic at `random_state=42`, so a correct local run reproduces them exactly. If your numbers differ, check the seed, the split, and your package versions before opening an issue - and never edit the frozen numbers to match a local run (see [CLAUDE.md](../CLAUDE.md)).
