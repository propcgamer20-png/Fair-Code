# What Is Conditional Demographic Parity?

> *Plain demographic parity asks whether two groups get positive outcomes at the same rate. Conditional demographic parity asks whether they get them at the same rate once you hold a chosen "legitimate" factor fixed - and the choice of that factor decides the answer.*

## The One-Sentence Definition

**Conditional demographic parity** (CDP) requires equal positive-outcome rates across protected groups *within* each stratum of one or more explicitly chosen legitimate factors, rather than across the whole population at once.

## Why It Matters

Plain [demographic parity](demographic-parity.md) requires `P(Y_hat = 1 | G = A) = P(Y_hat = 1 | G = B)` unconditionally. Two things go wrong with that in practice:

- It is satisfied by a model that is equally useless for everyone (predict the base rate, ignore the features), so passing it is not evidence of a good model.
- It is violated by a model that legitimately uses a lawful, non-proxy factor - years of experience in a hiring model, loan amount in a credit model - that happens to correlate with a protected group. The violation may be entirely explained by that factor, not by the protected attribute.

Conditional demographic parity is the standard refinement for the second problem. You pick one or more conditioning factors `L` that you are willing to treat as a legitimate basis for outcome differences, stratify the population by `L`, and check demographic parity *within* each stratum:

```
P(Y_hat = 1 | G = A, L = l) = P(Y_hat = 1 | G = B, L = l)   for every level l
```

If the groups reach parity within every stratum of `L`, the aggregate gap was "explained by `L`". If a gap persists within strata, `L` does not account for it.

This is a real, commonly used construction - it is the fairness analogue of adding a control variable to a regression, and it is close to what US disparate-impact analysis does when it asks whether a challenged practice is "job related and consistent with business necessity". It is not a synonym for plain demographic parity, and it is not the same as [intersectional](intersectional-bias.md) or [subgroup](subgroup-fairness.md) fairness, which stratify by *other protected attributes* to find hidden gaps rather than by a legitimate factor to explain one.

## How It Works

Start from the identity that makes the aggregate gap decomposable. For each group `g`:

```
P(Y_hat = 1 | G = g) = sum over l of  P(L = l | G = g) * P(Y_hat = 1 | G = g, L = l)
```

The aggregate rate is a weighted average of within-stratum rates, weighted by how group `g` is distributed across the strata of `L`. Subtracting the two groups' aggregate rates gives a gap with two sources: different within-stratum rates (`P(Y_hat = 1 | G = g, L = l)` differs by `g`), and different stratum weights (`P(L = l | G = g)` differs by `g`).

Conditional demographic parity zeroes out the second source by construction: it only compares groups at the same value of `L`. What is left is the within-stratum gap. A sample-size-weighted average of the within-stratum gaps is the part of the aggregate gap that stratifying on `L` does *not* remove.

The catch is entirely in the choice of `L`. If `L` is a genuine exogenous factor, the within-stratum gap is the disparity net of a real confounder. If `L` is a [proxy](proxy-variables.md) for the protected attribute, conditioning on it absorbs the discrimination into the "legitimate" term and the within-stratum gap understates the real harm. CDP gives you a knob; it does not tell you where to set it.

## Concrete Example: Benefits Denial - Audit 04

`Benefits Denial/` audits the Adult Census Income dataset (`adult.csv`, 32,561 rows). The target is `income == '>50K'` and `sex` is a declared protected attribute. Using the dataset's own outcome rates (the base rate a label-level demographic parity check compares):

**Unconditional:**

| Group | n | P(income > 50K) |
|---|---:|---:|
| Male | 21,790 | 30.6% |
| Female | 10,771 | 11.0% |
| Gap (M - F) | | **+19.6 pp** |

Now apply CDP with two different choices of legitimate factor `L`.

### L = education level (`education.num`, 15 levels)

| education.num | n | Gap (M - F) |
|---:|---:|---:|
| 9 (HS grad) | 10,501 | +13.7 pp |
| 10 (some college) | 7,291 | +19.5 pp |
| 13 (Bachelors) | 5,355 | +29.4 pp |
| 14 (Masters) | 1,723 | +32.3 pp |
| 15 (Prof-school) | 576 | +33.1 pp |
| 16 (Doctorate) | 413 | +20.2 pp |

Sample-weighted within-stratum gap: **+18.4 pp**. Conditioning on education removes almost none of the aggregate gap - within every education level men are markedly more likely to be high earners, and at the top three levels the gap is *larger* than the unconditional +19.6. CDP conditioned on education says: the disparity is not an artifact of women being less educated in this dataset.

### L = marital status (`marital.status`)

| marital.status | n | Gap (M - F) |
|---|---:|---:|
| Married-civ-spouse | 14,976 | -0.9 pp |
| Never-married | 10,683 | +2.0 pp |
| Divorced | 4,443 | +9.3 pp |
| Widowed | 993 | +17.6 pp |

Sample-weighted within-stratum gap: roughly **+3 pp**, and inside the single largest stratum the sign reverses (women 0.9 points ahead). Conditioning on marital status makes most of the aggregate gap disappear.

### The two answers disagree, and that is the point

Same protected attribute, same dataset, same +19.6 pp aggregate. Condition on education and the gap stands. Condition on marital status and it nearly vanishes. CDP did not resolve the fairness question - it moved it to a new one: *is marital status a legitimate basis for a 20-point income difference between men and women, or is it a proxy for a sex-role division of unpaid labor that the outcome variable should not be conditioned on?* That is a normative and legal question, not a statistical one, and CDP's output is only as defensible as the answer to it. (This is the same aggregate-vs-stratified divergence covered from the other direction in [Simpson's Paradox](simpsons-paradox.md).)

```python
import pandas as pd
import numpy as np

df = pd.read_csv("Benefits Denial/adult.csv")
df["high_income"] = (df["income"] == ">50K").astype(int)


def within_stratum_gap(frame, condition_col):
    rows = []
    for level, sub in frame.groupby(condition_col):
        m = sub.loc[sub["sex"] == "Male", "high_income"]
        f = sub.loc[sub["sex"] == "Female", "high_income"]
        if len(m) < 30 or len(f) < 30:
            continue
        rows.append((level, len(sub), m.mean() - f.mean()))
    tbl = pd.DataFrame(rows, columns=["level", "n", "gap"])
    weighted = np.average(tbl["gap"], weights=tbl["n"])
    return tbl, weighted


for col in ("education.num", "marital.status"):
    _, w = within_stratum_gap(df, col)
    print(f"condition on {col:16s}: weighted within-stratum gap = {w:+.4f}")
# condition on education.num   : weighted within-stratum gap = +0.1844
# condition on marital.status  : weighted within-stratum gap = +0.0305
```

## Detection Code

The following module computes the unconditional demographic parity gap, the conditional (within-stratum) gap for a chosen legitimate factor, and the fraction of the unconditional gap that conditioning explains away.

```python
import numpy as np
import pandas as pd


def conditional_demographic_parity(
    df: pd.DataFrame,
    outcome_col: str,
    group_col: str,
    advantaged: str,
    disadvantaged: str,
    condition_cols: list[str],
    min_group_in_stratum: int = 30,
) -> dict:
    """
    Compare the unconditional demographic parity gap for (advantaged -
    disadvantaged) against the gap computed within each stratum defined by
    cross-tabulating condition_cols.

    outcome_col must be 0/1. Returns a dict with:
      unconditional_gap        aggregate P(Y=1|adv) - P(Y=1|dis)
      conditional_gap          sample-size-weighted mean of within-stratum gaps
      explained_fraction       1 - conditional_gap / unconditional_gap, i.e.
                               how much of the aggregate gap stratifying removed
      strata                   per-stratum table (level, n, gap)

    A strata row is skipped if either group has fewer than
    min_group_in_stratum members in it (its within-stratum rate would be too
    noisy to compare).
    """
    d = df[[outcome_col, group_col, *condition_cols]].dropna()
    d = d[d[group_col].isin([advantaged, disadvantaged])]

    def gap(frame):
        a = frame.loc[frame[group_col] == advantaged, outcome_col]
        b = frame.loc[frame[group_col] == disadvantaged, outcome_col]
        if len(a) == 0 or len(b) == 0:
            return np.nan, len(a), len(b)
        return a.mean() - b.mean(), len(a), len(b)

    uncond_gap, _, _ = gap(d)

    rows = []
    for level, sub in d.groupby(condition_cols if len(condition_cols) > 1
                                else condition_cols[0]):
        g, na, nb = gap(sub)
        if np.isnan(g) or min(na, nb) < min_group_in_stratum:
            continue
        rows.append({"level": level, "n": len(sub), "gap": g})

    strata = pd.DataFrame(rows).sort_values("n", ascending=False)
    if strata.empty:
        return {"unconditional_gap": float(uncond_gap),
                "conditional_gap": np.nan, "explained_fraction": np.nan,
                "strata": strata}

    cond_gap = float(np.average(strata["gap"], weights=strata["n"]))
    explained = (1.0 - cond_gap / uncond_gap) if uncond_gap != 0 else np.nan

    return {
        "unconditional_gap": float(uncond_gap),
        "conditional_gap": cond_gap,
        "explained_fraction": float(explained),
        "strata": strata.reset_index(drop=True),
    }


def print_cdp_report(result: dict, condition_label: str) -> None:
    print(f"Conditioning factor: {condition_label}")
    print(f"  unconditional DP gap:        {result['unconditional_gap']:+.4f}")
    print(f"  conditional (within) DP gap: {result['conditional_gap']:+.4f}")
    if not np.isnan(result["explained_fraction"]):
        print(f"  fraction of gap explained:   "
              f"{result['explained_fraction']:.1%}")
    print("  per-stratum gaps (largest first):")
    for _, row in result["strata"].iterrows():
        print(f"    {str(row['level'])[:28]:28s} n={int(row['n']):6d}  "
              f"gap={row['gap']:+.4f}")


# Usage on the Benefits Denial audit:
# import pandas as pd
# df = pd.read_csv("Benefits Denial/adult.csv")
# df["high_income"] = (df["income"] == ">50K").astype(int)
# print_cdp_report(conditional_demographic_parity(
#     df, "high_income", "sex", "Male", "Female", ["education.num"]),
#     "education.num")
# print_cdp_report(conditional_demographic_parity(
#     df, "high_income", "sex", "Male", "Female", ["marital.status"]),
#     "marital.status")
```

Against `Benefits Denial/adult.csv` this reports an `explained_fraction` near `0.06` for `education.num` (conditioning removes almost nothing) and near `0.84` for `marital.status` (conditioning removes most of the gap) - the same +19.6 pp aggregate, two incompatible readings.

## Limitations and Trade-offs

### 1. The conditioning set is a value judgment, not a statistical choice

Everything CDP reports is downstream of which factors you declared "legitimate". There is no test that tells you whether marital status, or occupation, or prior loan history, is a fair thing to condition on. Pick a factor that is genuinely a proxy for the protected attribute and CDP will confidently report that the disparity is "explained", which is exactly the [proxy-variable](proxy-variables.md) trap.

### 2. Conditioning can only ever shrink or hold the gap you can attribute, never validate the factor

A small within-stratum gap means the aggregate gap co-varies with `L`. It does not mean `L` *causes* the outcome difference, and it does not mean using `L` is lawful or ethical. Those require an argument outside the data.

### 3. Strata multiply fast and thin out

Conditioning on one categorical factor is usually fine; conditioning on two or three cross-tabulated factors produces many strata with tiny per-group counts, unstable within-stratum rates, and a weighted gap dominated by a few large cells. Keep the conditioning set minimal and report per-stratum sample sizes.

### 4. Continuous conditioning factors require binning

`education.num` above is discrete. A continuous factor (age, income, tenure) has to be binned, and the bin edges change the answer. Coarse bins can leave residual confounding inside each bin; fine bins run into the small-strata problem in point 3.

### 5. It does not fix the "equally useless model" hole

Like plain demographic parity, CDP is a rate comparison. A model that is equally bad within every stratum still passes. CDP tightens demographic parity against one specific failure (a legitimate confounder); it does not turn it into a sufficiency or calibration guarantee.

## Related Concepts

* [What Is Demographic Parity?](demographic-parity.md) - the unconditional metric CDP refines.
* [What Is a Proxy Variable?](proxy-variables.md) - why conditioning on the wrong factor launders discrimination instead of explaining it.
* [What Is Simpson's Paradox in Fairness Audits?](simpsons-paradox.md) - the same aggregate-vs-stratified divergence, framed as a reversal rather than a refinement.
* [What Is Subgroup Fairness (and Fairness Gerrymandering)?](subgroup-fairness.md) - stratifying by other protected attributes to find hidden gaps, the opposite motivation from CDP.
* [Why Fairness Metrics Conflict](fairness-metric-conflicts.md) - where conditional and unconditional parity sit among the impossibility results.

## Related Projects in This Repo

* [`Benefits Denial/`](../Benefits%20Denial/) - the Adult Census Income audit above; conditioning the `sex` income gap on education preserves it, conditioning on marital status removes it.
* [`German Credit Lending/`](../German%20Credit%20Lending/) - a credit audit where loan amount and credit history are candidate "business necessity" factors to condition an age gap on.

## Further Reading

* [Corbett-Davies, S., Pierson, E., Feller, A., Goel, S., Huq, A. (2017): Algorithmic Decision Making and the Cost of Fairness, *KDD 2017*](https://arxiv.org/abs/1701.08230) - introduces conditional statistical parity and shows how the choice of conditioning variables trades off against error rates.
* [Wachter, S., Mittelstadt, B., Russell, C. (2021): Why Fairness Cannot Be Automated, *Computer Law and Security Review*, 41](https://arxiv.org/abs/2005.05906) - argues that the "legitimate factor" choice at the heart of conditional parity mirrors, and cannot be separated from, EU non-discrimination law's contextual reasoning.
* [Kilbertus, N., Rojas-Carulla, M., Parascandolo, G., Hardt, M., Janzing, D., Scholkopf, B. (2017): Avoiding Discrimination through Causal Reasoning, *NeurIPS 2017*](https://arxiv.org/abs/1706.02744) - frames "which variables may we condition on" as a causal-graph question rather than a statistical one.

---

*Part of [The Fair Code Project](https://instagram.com/thefaircodeproject) - exposing and fixing algorithmic bias with real data and open code.*
