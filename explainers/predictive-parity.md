# Explainer: What Is Predictive Parity?

*Metrics · Sufficiency-based fairness · COMPAS dual-reading · Chouldechova impossibility*

## The one-sentence version

A model satisfies **predictive parity** when a positive prediction means the same thing regardless of group membership — i.e., the Positive Predictive Value (PPV) is equal across groups. If a "high risk" flag turns into an actual bad outcome for 63% of one group and 63% of another, the flag has equal *meaning*, even if the two groups don't get flagged at the same rate.

## The formula

For a protected attribute with groups `a` and `b`:

```
PPV(group) = TP(group) / (TP(group) + FP(group))

Predictive Parity holds when:  PPV(a) ≈ PPV(b)
```

This is a **sufficiency** metric — it conditions on the *prediction*, not the ground truth. That's what separates it from Equalized Odds (Explainer 04), which conditions on the ground truth and requires equal TPR/FPR instead.

| Metric | Conditions on | Asks |
|---|---|---|
| Demographic Parity | nothing (prior) | Are positive predictions handed out at the same rate? |
| Equalized Odds | true label | Given the actual outcome, are error rates equal? |
| **Predictive Parity** | **predicted label** | **Given a positive prediction, is it equally trustworthy?** |

## Real-world proof: the COMPAS dual-reading

This is the metric at the center of the most famous fairness dispute in the field. In 2016, ProPublica's investigation of the COMPAS recidivism tool and Northpointe (its vendor) reached opposite conclusions from the *same dataset*, because they were checking different fairness criteria:

- **ProPublica's reading (error-rate balance / Equalized Odds):** the false-positive rate for Black defendants was roughly double that of white defendants — meaning Black defendants who did *not* reoffend were far more likely to be wrongly flagged high-risk.
- **Northpointe's reading (predictive parity):** the PPV was close across race — a "high risk" label corresponded to actual reoffending at a similar rate for both groups, which Northpointe presented as evidence the tool wasn't biased.

Both readings are internally consistent. Both are checking a real, legitimate fairness property. And **both cannot hold at once** unless base rates match — which is exactly the problem.

## Why this conflicts with Equalized Odds

Chouldechova (2017) proved the mechanism behind the COMPAS dispute directly: if a score satisfies predictive parity, but the underlying prevalence (base rate) of the outcome differs between groups, the false positive and false negative rates **cannot** be equal across those groups. It's not a bug in COMPAS — it's an algebraic identity. Kleinberg, Mullainathan, and Raghavan reached an equivalent conclusion in the same year via a separate impossibility result.

In the Broward County COMPAS data, recidivism prevalence differs meaningfully between Black defendants and white defendants. Given that gap, no risk score can be simultaneously well-calibrated (predictive parity) *and* error-balanced (equalized odds) — one of the two has to give. This is the concrete case behind **Explainer 06 — Why Fairness Metrics Conflict**; read that explainer for the full impossibility-theorem writeup.

## Detection code

```python
import pandas as pd

def predictive_parity_gap(df: pd.DataFrame, y_true: str, y_pred: str, group_col: str):
    """
    Computes Positive Predictive Value (PPV) per group and the resulting
    predictive-parity gap. A gap near 0 indicates predictive parity; a large
    gap means a positive prediction is more trustworthy for one group than
    another.
    """
    ppv_by_group = {}
    for group, sub in df.groupby(group_col):
        predicted_positive = sub[sub[y_pred] == 1]
        if len(predicted_positive) == 0:
            ppv_by_group[group] = float("nan")
            continue
        true_positives = (predicted_positive[y_true] == 1).sum()
        ppv_by_group[group] = true_positives / len(predicted_positive)

    groups = list(ppv_by_group.keys())
    gap = max(ppv_by_group.values()) - min(ppv_by_group.values())

    print("PPV by group:")
    for g, v in ppv_by_group.items():
        print(f"  {g}: {v:.2%}")
    print(f"Predictive Parity Gap: {gap:.2%}")

    return ppv_by_group, gap
```

Pair this with the base-rate check below — a small PPV gap next to a large base-rate gap is the signature Chouldechova identified:

```python
def base_rate_gap(df: pd.DataFrame, y_true: str, group_col: str):
    rates = df.groupby(group_col)[y_true].mean()
    print("Base rate (true prevalence) by group:")
    print(rates)
    return rates.max() - rates.min()
```

## When predictive parity is (and isn't) the right check

**Use it when:** the cost of the decision falls on whoever receives the positive label, and you care whether that label is equally reliable — e.g., a "high risk" score used to justify pretrial detention, a "high cost" flag used to deny a claim.

**Don't rely on it alone when:** base rates differ across groups for reasons rooted in structural inequality rather than individual behavior (see Explainer 05 — Disparate Impact, and the base-rate discussion in the Healthcare Readmission audit). Satisfying predictive parity in that setting can still leave one group bearing a much higher error-rate burden, exactly as COMPAS did.

## Related

- Explainer 04 — Equalized Odds (the metric predictive parity trades off against)
- Explainer 05 — Disparate Impact / 80% Rule
- Explainer 06 — Why Fairness Metrics Conflict (the impossibility theorem this explainer is a worked instance of)
- Experiment 01 — COMPAS (the dataset and audit code referenced above)

## References

- Angwin, J. et al., "Machine Bias," ProPublica, 2016.
- Chouldechova, A., "Fair Prediction with Disparate Impact," *Big Data*, 2017.
- Kleinberg, J., Mullainathan, S., Raghavan, M., "Inherent Trade-Offs in the Fair Determination of Risk Scores," ITCS 2017.
- Dieterich, W., Mendoza, C., Brennan, T., "COMPAS Risk Scales: Demonstrating Accuracy Equity and Predictive Parity," Northpointe, 2016.
