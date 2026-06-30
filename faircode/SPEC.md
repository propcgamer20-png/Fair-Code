# Fair Code Profiler — Analysis Spec

This is the **single source of truth** for the Open Dataset Profiler. Both implementations —
the Python engine (`faircode/profiler.py`) and the browser engine (`assets/profiler-engine.js`) —
must implement *exactly* this spec so the same CSV yields the same numbers in the CLI and on the web.

The Profiler is **diagnostic**, not predictive. It audits a dataset's *demographic representation*
before any model is trained. It does not train models, drop columns, or measure prediction gaps —
that is what the `unfair.py` / `fair.py` audits do. The Profiler answers a different question:
**"who is, and is not, adequately represented in this data?"**

---

## 1. Column auto-detection

**Tokenize** the column name: split on separators **and** camelCase boundaries, then lower-case.
`DateOfBirth → [date, of, birth]`, `Sex_Code_Text → [sex, code, text]`, `ageGroup → [age, group]`.
Token boundaries are what stop `age` from matching `Agency_Text` or `Language`.

A keyword matches a token by **exact match** when the keyword is <4 chars, or **prefix match** when
it is ≥4 chars (prefix, not substring — so `age` never matches `agency`, but `statecode` matches
`state`). Classify by the **first** keyword list that matches any token (order matters):

| Dimension   | Keywords                                                                 |
|-------------|--------------------------------------------------------------------------|
| `sex`       | `sex`, `gender`                                                          |
| `race`      | `race`, `ethnic`, `ethnicity`                                           |
| `age`       | `age`, `dob`, `yob`, `birth`                                            |
| `geography` | `region`, `state`, `zip`, `zipcode`, `postal`, `country`, `county`, `city`, `location`, `province` |

A column not matched above is treated as a **generic categorical** demographic *only if* its
distinct non-null value count is `2 ≤ n ≤ 20`.

Detection returns, for each kept column, its `name` and `kind` ∈ {`sex`, `race`, `age`,
`geography`, `categorical`}.

After per-dimension analysis, any dimension that exploded into more than `MAX_DIMENSION_GROUPS`
(default **50**) groups is **dropped** as a likely identifier/date column — *except* `geography`,
which legitimately has high cardinality (many cities/regions).

---

## 2. Age normalization

Age columns come in three shapes — normalize to numeric bands:

- **Numeric** (e.g. `34`): use directly.
- **Interval string** (e.g. `[70-80)`): take the lower bound integer via the first run of digits.
- **Anything else**: treat as categorical (skip numeric handling).

Fixed bands (left-closed): `0–18`, `18–30`, `30–45`, `45–60`, `60–75`, `75+`.
The band shares are then analyzed exactly like a categorical column.

---

## 3. Per-dimension metrics

For a dimension with `k` groups and null-excluded normalized shares `p_1 … p_k` (each `p_i = count_i / N_nonnull`):

- **shares** — the `p_i`, descending, with raw counts.
- **min_share** = `min(p_i)`; **max_share** = `max(p_i)`.
- **imbalance_ratio** = `max_share / min_share` (the most-represented group is this many times the least).
- **entropy_ratio** = `H / ln(k)` where `H = −Σ p_i · ln(p_i)`.
  - Range `[0, 1]`; `1` = perfectly uniform, `0` = all mass in one group.
  - If `k ≤ 1`: `entropy_ratio = 0` (a single-group column has no diversity).
  - Use natural log in both languages (`Math.log` / `math.log`); the log base cancels in the ratio.
- **under_represented** — groups with `p_i < min_share_threshold` (default **0.05**).
- **missing_pct** = `null_count / N_total` for the column.

`dimension_score = round(entropy_ratio × 100)`.

### Numeric-age extra (informational, not scored)
- **skewness** — Fisher–Pearson sample skewness of the raw numeric ages:
  `g1 = (1/N · Σ (x−x̄)³) / (1/N · Σ (x−x̄)²)^1.5`. `null`/`0` if variance is 0 or `N < 3`.

---

## 4. Intersectional gaps (informational, not scored)

Take the **first two** detected demographic dimensions (in detection order). Build their crosstab of
counts. Report every cell whose count is `0` (an absent subgroup) or `< intersection_floor` of total
rows (default **0.01** → "near-empty"). Skip if fewer than two dimensions were detected.

---

## 5. Headline score & grade

```
overall_score = round( mean( dimension_score for every detected dimension ) )   # 0 if none
```

Grade bands:

| Grade | Score   | Meaning                                              |
|:-----:|---------|------------------------------------------------------|
| A     | 85–100  | Well balanced across detected demographics           |
| B     | 70–84   | Mostly balanced, minor under-representation          |
| C     | 55–69   | Noticeable imbalance in one or more dimensions       |
| D     | 40–54   | Strong imbalance / sparse subgroups                  |
| F     | 0–39    | Severe imbalance or single-group dimensions          |

The score intentionally reflects **balance only**. Missing-data %, imbalance ratios, and
intersectional gaps are surfaced as **flags** alongside the score, not folded into it — this keeps
the two engines trivially in sync and the score easy to explain.

---

## 6. Result shape

Both engines produce this structure (keys identical; Python uses a dataclass serialized to the same
dict, JS uses a plain object):

```jsonc
{
  "n_rows": 1340,
  "n_cols": 11,
  "overall_score": 72,
  "grade": "B",
  "dimensions": [
    {
      "name": "gender", "kind": "sex", "n_groups": 2,
      "dimension_score": 99, "entropy_ratio": 0.999,
      "imbalance_ratio": 1.05, "min_share": 0.49, "missing_pct": 0.0,
      "skewness": null,
      "groups": [ {"label": "male", "count": 676, "share": 0.504},
                  {"label": "female", "count": 664, "share": 0.496} ],
      "under_represented": []
    }
  ],
  "intersections": [
    { "dims": ["age_band", "gender"], "cells": [ {"a": "75+", "b": "female", "count": 0} ] }
  ],
  "flags": [ "region: 'southwest' is under-represented (3.1%)", "..." ]
}
```

`flags` is a human-readable list assembled from: every `under_represented` group, every dimension
with `imbalance_ratio ≥ 3`, every dimension with `missing_pct ≥ 0.05`, and every intersectional gap.

---

## 7. Defaults (single place to tune)

| Constant               | Default | Used by                          |
|------------------------|:-------:|----------------------------------|
| `MIN_SHARE_THRESHOLD`  | 0.05    | under-representation flagging    |
| `INTERSECTION_FLOOR`   | 0.01    | near-empty intersection cells    |
| `MAX_CATEGORICAL_CARD` | 20      | generic-categorical detection    |
| `IMBALANCE_FLAG`       | 3.0     | imbalance-ratio flag             |
| `MISSING_FLAG`         | 0.05    | missing-data flag                |
| `AGE_BANDS`            | 0,18,30,45,60,75 | age band edges          |
