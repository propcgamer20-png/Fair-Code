> *Run enough p-values at a 0.05 threshold and some will read "significant" by chance alone - a multiple-comparisons correction is how you find out which of this repo's dozens of per-audit findings actually survive that scrutiny.*

## The One-Sentence Definition

A **multiple-comparisons correction** (Bonferroni, Holm, or Benjamini-Hochberg false discovery rate) adjusts the significance threshold a batch of p-values is judged against, so that running many hypothesis tests at once doesn't inflate the chance of calling a fluke "significant" just because enough tests were run.

## Why It Matters

[What Is a Bootstrap Confidence Interval (and a Permutation Test)?](bootstrap-confidence-intervals.md) attaches a p-value to every fairness gap this repo measures - but it attaches one to *every single gap*, not just one per audit. The benchmark harness computes six metrics, across every protected attribute, for three model families and five mitigation strategies, for each of seven audits. For a single-protected-attribute audit like COMPAS (race) that's `6 metrics x 3 models x 5 strategies = 90` p-values from one audit alone; across the full frozen benchmark, `paper/results-frozen/results_fairness.csv` carries **1,320** p-values in total.

At a raw 0.05 threshold, each individual test has a 5% chance of reading "significant" purely by chance, even when nothing real is happening. Run 90 independent tests and the probability that *at least one* looks significant by chance alone climbs to `1 - 0.95^90 ≈ 99%` - not a rare edge case, a near-certainty. [Bootstrap Confidence Intervals](bootstrap-confidence-intervals.md#limitations) already names this exact gap in its own limitations section: *"No correction (e.g. Bonferroni) is currently applied across this full set."* This explainer covers what such a correction actually does to a real slice of those p-values, and what it costs.

## Core Concept

There are two different questions a correction can answer, and they trade off against each other:

**Family-wise error rate (FWER)** - the probability of even *one* false positive anywhere in the whole batch of tests. **Bonferroni** and **Holm** both control FWER.

- **Bonferroni** is the simplest possible fix: if you're running `m` tests at level `alpha`, judge every individual p-value against `alpha / m` instead of `alpha`. For COMPAS's 90 tests at `alpha = 0.05`, that's `0.05 / 90 ≈ 0.00056` - a p-value has to be almost 90 times smaller than the usual 0.05 to survive. It's conservative because it assumes the worst case (every test independent, all null), which makes it easy to reason about but quick to miss real, smaller effects.
- **Holm's step-down procedure** controls the same FWER with more power than Bonferroni, by not applying the harshest threshold to every test. Sort the `m` p-values ascending. Compare the smallest to `alpha / m` (Bonferroni's own threshold); if it survives, compare the *next* smallest to `alpha / (m - 1)` - a slightly looser bar - and keep going, each step comparing against `alpha / (m - i + 1)` for the `i`-th smallest p-value. The first p-value that fails stops the whole procedure: every larger p-value is rejected too, sequentially, even if one of them would individually have passed its own step's threshold. Holm never rejects fewer null hypotheses than Bonferroni, and can reject strictly more.

**False discovery rate (FDR)** - not "no false positives anywhere," but "of the findings I call significant, only a controlled fraction are expected to be false." **Benjamini-Hochberg (BH-FDR)** controls this instead of FWER, and is far less conservative because it's answering an easier question.

- **Benjamini-Hochberg** sorts the `m` p-values ascending (rank `1..m`) and finds the *largest* rank `i` where `p_(i) <= (i / m) * alpha`. Every p-value at or below that rank is called significant - not just the ones that individually clear their own step, unlike Holm's sequential stop. Because later, larger ranks get a looser threshold that scales up toward `alpha` itself, BH-FDR keeps far more discoveries than Bonferroni or Holm at the same nominal level, at the cost of tolerating more false positives among them (bounded, on average, at the chosen FDR rate).

## Concrete Example: COMPAS - Audit 01

COMPAS declares one protected attribute (race), so its full grid is `5 strategies x 3 models x 6 metrics = 90` p-values - real numbers straight from `paper/results-frozen/results_fairness.csv`. At the raw 0.05 threshold, **67 of the 90** read "significant." After correction:

| Correction | Significant (of 90) | Threshold used |
|---|---:|---|
| Raw (p < 0.05) | 67 | 0.05 for every test |
| Bonferroni | 53 | 0.05 / 90 = 0.00056 for every test |
| Holm | 55 | sequential, from 0.00056 up to 0.05 |
| Benjamini-Hochberg FDR | 64 | sequential, scaling with rank |

A sample of individual rows across that boundary shows what each correction actually does to a specific finding:

| Strategy | Model | Metric | p-value | Raw | Bonferroni | Holm | BH-FDR |
|---|---|---|---:|:-:|:-:|:-:|:-:|
| baseline | logistic_regression | demographic_parity_diff | 0.0000 | significant | significant | significant | significant |
| unawareness_proxy_removal | random_forest | equal_opportunity_diff | 0.0010 | significant | **not** | significant | significant |
| unawareness_proxy_removal | logistic_regression | equalized_odds_diff | 0.0015 | significant | **not** | **not** | significant |
| baseline | random_forest | accuracy_equality_diff | 0.0065 | significant | **not** | **not** | significant |
| in_processing | random_forest | demographic_parity_diff | 0.0225 | significant | **not** | **not** | significant |
| in_processing | logistic_regression | equal_opportunity_diff | 0.0385 | significant | **not** | **not** | **not** |
| baseline | logistic_regression | accuracy_equality_diff | 0.0395 | significant | **not** | **not** | **not** |
| unawareness | logistic_regression | accuracy_equality_diff | 0.9455 | not | not | not | not |

The first row (p essentially 0) survives every correction - nothing about running 90 tests changes the conclusion that COMPAS's baseline demographic parity gap by race is real. The last row was never significant to begin with. The six rows in between are exactly the point: identical raw p-values read as five different verdicts depending on which question you ask ("no false positives anywhere" vs. "a controlled fraction of my discoveries are false"), and two of them - both around p = 0.038-0.040 - are "significant" under the repo's current uncorrected reporting but wouldn't survive even the most permissive correction here.

## Detection Code

A from-scratch implementation of all three corrections, verified against `statsmodels.stats.multitest.multipletests` on the exact 90-row COMPAS/race slice above (identical significant-count results: 53 Bonferroni, 55 Holm, 64 BH-FDR):

```python
import numpy as np


def bonferroni(p_values, alpha=0.05):
    """FWER control: judge every p-value against alpha / m."""
    m = len(p_values)
    threshold = alpha / m
    return np.asarray(p_values) <= threshold


def holm(p_values, alpha=0.05):
    """FWER control, step-down: sort ascending, compare the i-th smallest
    (1-indexed) to alpha / (m - i + 1). The first failure stops rejection
    for every larger p-value too, even ones that would pass their own step."""
    p_values = np.asarray(p_values)
    m = len(p_values)
    order = np.argsort(p_values)
    reject_sorted = np.zeros(m, dtype=bool)
    for i, idx in enumerate(order):  # i is 0-indexed; rank = i + 1
        threshold = alpha / (m - i)
        if p_values[idx] <= threshold:
            reject_sorted[i] = True
        else:
            break  # every remaining (larger) p-value is not rejected
    reject = np.zeros(m, dtype=bool)
    reject[order] = reject_sorted
    return reject


def benjamini_hochberg(p_values, alpha=0.05):
    """FDR control: sort ascending, find the largest rank i where
    p_(i) <= (i / m) * alpha, then reject every p-value at or below
    that rank - not just the ones that individually clear their own step."""
    p_values = np.asarray(p_values)
    m = len(p_values)
    order = np.argsort(p_values)
    sorted_p = p_values[order]
    ranks = np.arange(1, m + 1)
    passes = sorted_p <= (ranks / m) * alpha
    reject_sorted = np.zeros(m, dtype=bool)
    if passes.any():
        cutoff_rank = np.max(np.nonzero(passes)) + 1  # last passing rank, 1-indexed
        reject_sorted[:cutoff_rank] = True
    reject = np.zeros(m, dtype=bool)
    reject[order] = reject_sorted
    return reject


# Usage example, on the p-values from any one audit's results_fairness.csv slice:
# p_values = fairness_df[fairness_df["audit"] == "compas"]["p_value"].to_numpy()
# raw_sig = p_values < 0.05
# print(raw_sig.sum(), bonferroni(p_values).sum(), holm(p_values).sum(), benjamini_hochberg(p_values).sum())
# 67 53 55 64 - matching the table above.
```

## Limitations

### 1. A correction trades false positives for false negatives

Every one of these methods makes it *harder* to call something significant - that's the whole point, but it's not free. A real, smaller effect that would have cleared the raw 0.05 threshold can fail Bonferroni or Holm once corrected for 90 simultaneous tests, exactly like two of the rows in the table above. Choosing FWER over FDR (or vice versa) is choosing which error you'd rather risk, not eliminating error.

### 2. The correction is only as meaningful as the test batch it's applied to

Correcting across "every p-value COMPAS produces" and correcting across "every p-value this repo has ever produced" give different answers to different questions - there's no single universally correct choice of `m`. This explainer corrects within one audit (90 tests) because that's the natural unit a reader evaluates a single audit's claims against; a reader asking "should I trust *any* significant finding across all seven audits" would need to correct across all 1,320.

### 3. None of these three methods account for correlated tests

Many of these 90 p-values are not independent - the same underlying data drives all six metrics for a given (strategy, model) cell, and adjacent strategies share most of their rows. Bonferroni and Holm's FWER guarantees hold regardless (they're valid under arbitrary dependence), but BH-FDR's guarantee technically assumes independence or a specific positive-dependence structure; under general dependence a stricter variant (Benjamini-Yekutieli) is the theoretically safe choice, at the cost of even fewer discoveries.

### 4. This explainer's own correction isn't applied anywhere in the actual benchmark

The table above is illustrative, computed for this explainer - `faircode/significance.py` and `faircode/benchmark.py` do not currently apply any of these corrections to the harness's real output. Reading any single p-value from `results_fairness.csv` today still means reading it uncorrected, in the context this explainer describes.

## Related Concepts

* [What Is a Bootstrap Confidence Interval (and a Permutation Test)?](bootstrap-confidence-intervals.md) - the source of every p-value this explainer corrects, and the one that first flagged this gap in its own limitations.
* [What Is the Base Rate Fallacy?](base-rate-fallacy.md) - another way a technically-correct number (a raw p-value, a screening test's accuracy) misleads without the right context attached.
* [What Is Intersectional Bias?](intersectional-bias.md) - intersectional pairs add even more simultaneous tests per audit, making the correction question sharper exactly where subgroups are already smallest.

## Related Projects in This Repo

* [`COMPAS/`](../COMPAS/) - the audit behind every number in this explainer's worked example.
* [`faircode/significance.py`](../faircode/significance.py) - computes the uncorrected p-value this explainer's code corrects; frozen per [CLAUDE.md](https://github.com/yakew7/Fair-Code/blob/main/CLAUDE.md), so the detection code above mirrors its output independently rather than importing it.
* [`paper/results-frozen/results_fairness.csv`](../paper/results-frozen/results_fairness.csv) - the 1,320-row source of every p-value cited above.

## Further Reading

* [Dunn, O. J. (1961): Multiple Comparisons Among Means, *Journal of the American Statistical Association*, 56(293), 52-64](https://www.tandfonline.com/doi/abs/10.1080/01621459.1961.10482090) - the paper that formalized the Bonferroni correction for simultaneous confidence intervals.
* [Holm, S. (1979): A Simple Sequentially Rejective Multiple Test Procedure, *Scandinavian Journal of Statistics*, 6(2), 65-70](http://www.jstor.org/stable/4615733) - the step-down procedure that dominates Bonferroni while keeping the same family-wise error guarantee.
* [Benjamini, Y., Hochberg, Y. (1995): Controlling the False Discovery Rate: A Practical and Powerful Approach to Multiple Testing, *Journal of the Royal Statistical Society: Series B*, 57(1), 289-300](https://rss.onlinelibrary.wiley.com/doi/10.1111/j.2517-6161.1995.tb02031.x) - the original false discovery rate paper, and the reason FDR control became standard practice in genomics and large-scale testing generally.

*Part of [The Fair Code Project](https://instagram.com/thefaircodeproject) - exposing and fixing algorithmic bias with real data and open code.*
