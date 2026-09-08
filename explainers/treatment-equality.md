> *Two groups can have identical true-positive-rate and false-positive-rate gaps and still disagree sharply on which kind of error dominates within each group - Treatment Equality is the metric built to see that.*

## The One-Sentence Definition

**Treatment Equality** (Berk et al. 2018) requires the *ratio* of false negatives to false positives to be equal across protected groups - not the individual rates, but the balance between the two error types within each group.

## Why It Matters

This repo's other confusion-matrix-based metrics each answer a different question: [Equal Opportunity](equal-opportunity.md) checks the true-positive-rate gap, [Equalized Odds](equalized-odds.md) checks the larger of the true-positive-rate and false-positive-rate gaps, and [Accuracy Equality](accuracy-equality.md) checks overall accuracy. None of them asks Treatment Equality's question: *within* a group's errors, are false negatives and false positives showing up in the same proportion as in the other group?

That distinction is real, not academic. Two groups can have matching TPR gaps and matching FPR gaps - passing Equalized Odds cleanly - while one group's errors skew heavily toward false negatives and the other's skew toward false positives. Equalized Odds only compares each error rate *across* groups; Treatment Equality compares the *mix* of errors *within* each group. A criminal-justice risk tool where Black defendants' errors are mostly wrongful high-risk flags (false positives) and white defendants' errors are mostly wrongful low-risk clears (false negatives) is exactly the pattern Treatment Equality was built to surface, and the ProPublica COMPAS analysis (Angwin et al. 2016) that motivated this whole family of metrics found precisely that asymmetry.

## Concrete Example: COMPAS - Audit 01

None of `faircode/benchmark.py`'s six computed metrics is a treatment-equality ratio, so this example is a from-scratch confusion-matrix computation on the same COMPAS baseline logistic regression model used throughout this repo's other explainers - the same precedent [Individual Fairness](individual-fairness.md) uses, not a number pulled from `paper/results-frozen/results_fairness.csv`.

For the baseline model on race (disadvantaged: African-American defendants, n=1,788; advantaged: Caucasian defendants, n=1,466), the confusion matrix per group gives:

| Group | False Negatives | False Positives | FN:FP Ratio |
|---|---:|---:|---:|
| African-American (disadvantaged) | 73 | 575 | 0.13 |
| Caucasian (advantaged) | 465 | 15 | 31.00 |

(Positive-rate check against the frozen `demographic_parity_diff` for this exact model/split: (975+575)/1,788 = 86.7% vs. (2+15)/1,466 = 1.2%, an 85.5-point gap - matching `paper/results-frozen/results_fairness.csv` exactly, confirming this is the same baseline run.)

The two groups' *individual* false-negative and false-positive counts are the same kind of numbers Equalized Odds already compares - what Treatment Equality adds is the ratio between them, and here it is extreme in both directions at once. This baseline model predicts "high risk" for the overwhelming majority of African-American defendants and almost none of the Caucasian defendants (the 85.5-point demographic parity gap above), so its errors on each group are lopsided in opposite ways: African-American defendants' errors are almost entirely false positives (FN:FP of 0.13 - the model rarely clears someone it should have flagged, but very often flags someone it shouldn't), while Caucasian defendants' errors are almost entirely false negatives (FN:FP of 31.0 - the model almost never wrongly flags anyone, but very often wrongly clears someone). A 0.13-vs-31.0 ratio gap is not a subtle statistical artifact; it is the direct arithmetic consequence of a model that essentially never predicts "high risk" for one group and reports it as two completely different kinds of unreliable, one per group.



## Detection Code

```python
import numpy as np
import pandas as pd


def treatment_equality(y_true, y_pred, group, disadvantaged, advantaged):
    """
    Computes the Treatment Equality ratio (false negatives / false positives)
    for two groups and the gap between them.

    Parameters:
        y_true: array-like of true binary labels (1 = positive class)
        y_pred: array-like of predicted binary labels
        group: array-like of group membership, same length as y_true
        disadvantaged, advantaged: the two group values to compare

    Returns a dict with fn, fp counts and the FN:FP ratio for each group,
    plus the ratio gap. A ratio of float('inf') means zero false positives
    for that group (division by zero avoided by returning inf explicitly).
    """
    df = pd.DataFrame({"y_true": np.asarray(y_true), "y_pred": np.asarray(y_pred),
                        "group": np.asarray(group)})

    def counts(g):
        sub = df[df["group"] == g]
        fn = int(((sub["y_true"] == 1) & (sub["y_pred"] == 0)).sum())
        fp = int(((sub["y_true"] == 0) & (sub["y_pred"] == 1)).sum())
        ratio = fn / fp if fp else float("inf")
        return fn, fp, ratio

    fn_d, fp_d, ratio_d = counts(disadvantaged)
    fn_a, fp_a, ratio_a = counts(advantaged)

    return {
        "disadvantaged": {"fn": fn_d, "fp": fp_d, "fn_fp_ratio": ratio_d},
        "advantaged": {"fn": fn_a, "fp": fp_a, "fn_fp_ratio": ratio_a},
        "ratio_gap": ratio_d - ratio_a,
    }


# Usage example:
# result = treatment_equality(
#     y_true, y_pred, df["race"], disadvantaged="African-American", advantaged="Caucasian",
# )
# print(result)
# A large ratio_gap means the two groups' errors are skewed toward
# opposite error types, even if their individual FN and FP rates
# separately look comparable.
```

## Limitations

### 1. It says nothing about the overall error rate

Two groups can have an identical FN:FP ratio while one group is simply wrong far more often overall. Treatment Equality checks the *balance* of errors, not their *volume* - pair it with [Accuracy Equality](accuracy-equality.md) or [Equalized Odds](equalized-odds.md) to see both.

### 2. A ratio is sensitive to small counts

`fp = 0` forces the ratio to infinity, and a handful of extra false positives in a small subgroup can swing the ratio dramatically. Report the raw FN and FP counts alongside the ratio, not the ratio alone.

### 3. It still depends on a clean ground-truth label

Like every metric that uses `y_true`, Treatment Equality is only as trustworthy as the label it's measured against. See [What Is Label Bias?](label-bias.md).

### 4. Equalizing the ratio doesn't mean equalizing the harm

A false negative and a false positive are rarely equally costly (see [False Positives vs. False Negatives in Medical Risk Models](false-positives-vs-false-negatives.md)) - equalizing the *ratio* between them across groups doesn't equalize the real-world harm those errors cause, since the two error types weren't equally harmful to begin with.

## Related Concepts

* [What Is Equalized Odds?](equalized-odds.md) - compares each error rate *across* groups; Treatment Equality compares the *mix* of errors *within* each group instead.
* [What Is Accuracy Equality?](accuracy-equality.md) - checks overall accuracy, blind to which error type is driving it, the same blind spot Treatment Equality's ratio is built to expose.
* [What Is a Confusion Matrix?](confusion-matrix.md) - the four-way breakdown Treatment Equality's ratio is built from.
* [False Positives vs. False Negatives in Medical Risk Models](false-positives-vs-false-negatives.md) - why the two error types Treatment Equality balances are rarely equally costly to begin with.

## Related Projects in This Repo

* [`COMPAS/`](../COMPAS/) - the audit above, where the two groups' FN:FP ratios point in opposite directions.
* [`faircode/metrics.py`](../faircode/metrics.py) - this repo's six computed fairness metrics; Treatment Equality isn't among them, which is why the example above is a fresh computation rather than a frozen-CSV quote.

## Further Reading

* [Berk, R. et al. (2018): Fairness in Criminal Justice Risk Assessments](https://arxiv.org/abs/1703.09207) - introduces Treatment Equality alongside the broader family of statistical fairness criteria and the trade-offs between them.
* [Angwin, J. et al. (2016): Machine Bias (ProPublica)](https://www.propublica.org/article/machine-bias-risk-assessments-in-criminal-sentencing) - the COMPAS investigation whose finding (opposite-skewed error types across race) is the real-world pattern Treatment Equality was formalized to measure.
* [Barocas, S., Hardt, M., Narayanan, A. (2019): *Fairness and Machine Learning*](https://fairmlbook.org/classification.html) - situates Treatment Equality among the full family of classification-based fairness criteria.

*Part of [The Fair Code Project](https://instagram.com/thefaircodeproject) - exposing and fixing algorithmic bias with real data and open code.*
