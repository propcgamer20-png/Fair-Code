"""Core representation-profiling engine (pure pandas, no scikit-learn).

Implements faircode/SPEC.md. The single public entry point is `profile(df)`,
which returns a plain dict matching the result shape in SPEC section 6. The JS
port in assets/profiler-engine.js mirrors this logic exactly.
"""

from __future__ import annotations

import math
import re

import pandas as pd

from .detect import detect_columns

# ── Defaults (SPEC section 7) ───────────────────────────────────────────────
MIN_SHARE_THRESHOLD = 0.05
INTERSECTION_FLOOR = 0.01
IMBALANCE_FLAG = 3.0
MISSING_FLAG = 0.05
AGE_BANDS = [0, 18, 30, 45, 60, 75]  # left-closed edges; final band is "75+"
MAX_DIMENSION_GROUPS = 50  # drop identifier/date-like columns (geography exempt)

_DATE_RE = re.compile(r"\d{1,4}[/-]\d{1,2}[/-]\d{1,4}")


def _r(x, dp: int = 0):
    """Round half-up, matching JavaScript's Math.round so both engines agree.

    Python's built-in round() uses banker's rounding (88.5 -> 88), which would
    diverge from the JS port (88.5 -> 89). floor(x*f + 0.5) mirrors Math.round.
    """
    if x is None:
        return None
    f = 10 ** dp
    val = math.floor(x * f + 0.5) / f
    return int(val) if dp == 0 else val


# ── Age handling (SPEC section 2) ───────────────────────────────────────────
def _looks_like_dates(series) -> bool:
    """True if a sample of values look like dates (e.g. birthdates), not ages."""
    sample = series.dropna().astype(str).head(50)
    if len(sample) == 0:
        return False
    hits = sum(1 for v in sample if _DATE_RE.search(v))
    return hits / len(sample) > 0.5



def _age_to_numeric(value):
    """Coerce one age cell to a numeric lower-bound, or None."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    match = re.search(r"\d+", str(value))
    return float(match.group()) if match else None


def _age_band(num) -> str | None:
    if num is None:
        return None
    edges = AGE_BANDS
    for i in range(len(edges) - 1):
        if edges[i] <= num < edges[i + 1]:
            return f"{edges[i]}-{edges[i + 1]}"
    return f"{edges[-1]}+"


def _skewness(values: list[float]):
    """Fisher–Pearson sample skewness; None if undefined."""
    n = len(values)
    if n < 3:
        return None
    mean = sum(values) / n
    m2 = sum((x - mean) ** 2 for x in values) / n
    m3 = sum((x - mean) ** 3 for x in values) / n
    if m2 == 0:
        return None
    return m3 / (m2 ** 1.5)


# ── Per-dimension metrics (SPEC section 3) ──────────────────────────────────
def _analyze_groups(labels_counts: dict, n_total: int, null_count: int,
                    skewness=None) -> dict:
    """Given {label: count} for non-null values, compute the dimension metrics."""
    n_nonnull = sum(labels_counts.values())
    groups = []
    for label, count in labels_counts.items():
        share = count / n_nonnull if n_nonnull else 0.0
        groups.append({"label": str(label), "count": int(count), "share": share})
    # count desc, then label asc - deterministic tie-break so the JS port agrees.
    groups.sort(key=lambda g: (-g["count"], g["label"]))

    shares = [g["share"] for g in groups]
    k = len(shares)
    min_share = min(shares) if shares else 0.0
    max_share = max(shares) if shares else 0.0
    imbalance_ratio = (max_share / min_share) if min_share > 0 else float("inf")

    if k <= 1:
        entropy_ratio = 0.0
    else:
        H = -sum(p * math.log(p) for p in shares if p > 0)
        entropy_ratio = H / math.log(k)

    under = [g["label"] for g in groups if g["share"] < MIN_SHARE_THRESHOLD]

    return {
        "n_groups": k,
        "dimension_score": _r(entropy_ratio * 100),
        "entropy_ratio": _r(entropy_ratio, 4),
        "imbalance_ratio": (_r(imbalance_ratio, 2)
                            if imbalance_ratio != float("inf") else None),
        "min_share": _r(min_share, 4),
        "missing_pct": _r(null_count / n_total, 4) if n_total else 0.0,
        "skewness": _r(skewness, 4) if skewness is not None else None,
        "groups": groups,
        "under_represented": under,
    }


def _dimension(df: pd.DataFrame, name: str, kind: str) -> dict:
    col = df[name]
    n_total = len(df)
    skewness = None

    if kind == "age" and not _looks_like_dates(col):
        nums = [_age_to_numeric(v) for v in col]
        numeric_vals = [n for n in nums if n is not None]
        # Numeric age → bands; if nothing parsed numerically, fall back to raw.
        if numeric_vals:
            skewness = _skewness(numeric_vals)
            bands = [_age_band(n) for n in nums]
            null_count = sum(1 for b in bands if b is None)
            counts: dict = {}
            for b in bands:
                if b is not None:
                    counts[b] = counts.get(b, 0) + 1
            result = _analyze_groups(counts, n_total, null_count, skewness)
            result.update({"name": name, "kind": kind})
            return result

    # Categorical path (sex, race, geography, generic categorical, non-numeric age).
    null_count = int(col.isna().sum())
    vc = col.dropna().value_counts()
    counts = {label: int(c) for label, c in vc.items()}
    result = _analyze_groups(counts, n_total, null_count, skewness)
    result.update({"name": name, "kind": kind})
    return result


# ── Intersectional gaps (SPEC section 4) ────────────────────────────────────
def _intersections(df: pd.DataFrame, dims: list[dict]) -> list[dict]:
    if len(dims) < 2:
        return []
    a, b = dims[0], dims[1]
    n_total = len(df)
    floor = INTERSECTION_FLOOR * n_total

    def labelize(name, kind):
        if kind == "age":
            nums = [_age_to_numeric(v) for v in df[name]]
            if any(n is not None for n in nums):
                return pd.Series([_age_band(n) for n in nums], index=df.index)
        return df[name].astype("object")

    sa = labelize(a["name"], a["kind"])
    sb = labelize(b["name"], b["kind"])
    ct = pd.crosstab(sa, sb)

    cells = []
    for av in ct.index:
        for bv in ct.columns:
            count = int(ct.loc[av, bv])
            if count == 0 or count < floor:
                cells.append({"a": str(av), "b": str(bv), "count": count})
    if not cells:
        return []
    cells.sort(key=lambda c: (c["a"], c["b"]))  # deterministic order, matches JS
    return [{"dims": [a["name"], b["name"]], "cells": cells}]


# ── Flags + grade (SPEC sections 5 & 6) ─────────────────────────────────────
def _grade(score: int) -> str:
    if score >= 85:
        return "A"
    if score >= 70:
        return "B"
    if score >= 55:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def _build_flags(dimensions: list[dict], intersections: list[dict]) -> list[str]:
    flags: list[str] = []
    for d in dimensions:
        for g in d["groups"]:
            if g["label"] in d["under_represented"]:
                flags.append(
                    f"{d['name']}: '{g['label']}' is under-represented "
                    f"({g['share'] * 100:.1f}%)"
                )
        if d["imbalance_ratio"] is not None and d["imbalance_ratio"] >= IMBALANCE_FLAG:
            flags.append(
                f"{d['name']}: imbalance ratio {d['imbalance_ratio']:.1f}× "
                f"between largest and smallest group"
            )
        elif d["imbalance_ratio"] is None and d["n_groups"] > 1:
            flags.append(f"{d['name']}: a subgroup is effectively absent (0 rows)")
        if d["missing_pct"] >= MISSING_FLAG:
            flags.append(
                f"{d['name']}: {d['missing_pct'] * 100:.1f}% of values are missing"
            )
    for inter in intersections:
        a, b = inter["dims"]
        for cell in inter["cells"]:
            kind = "absent" if cell["count"] == 0 else f"only {cell['count']} rows"
            flags.append(
                f"{a}='{cell['a']}' × {b}='{cell['b']}' is {kind}"
            )
    return flags


def profile(df: pd.DataFrame) -> dict:
    """Profile a DataFrame for demographic representation. See SPEC section 6."""
    detected = detect_columns(df)
    dimensions = [_dimension(df, d["name"], d["kind"]) for d in detected]
    # Drop identifier/date-like columns that exploded into many groups; geography
    # (cities, regions) legitimately has high cardinality, so it is exempt.
    dimensions = [d for d in dimensions
                  if d["kind"] == "geography" or d["n_groups"] <= MAX_DIMENSION_GROUPS]
    kept_names = {d["name"] for d in dimensions}
    detected = [d for d in detected if d["name"] in kept_names]
    intersections = _intersections(df, detected)

    if dimensions:
        overall = _r(sum(d["dimension_score"] for d in dimensions) / len(dimensions))
    else:
        overall = 0

    return {
        "n_rows": len(df),
        "n_cols": len(df.columns),
        "overall_score": overall,
        "grade": _grade(overall),
        "dimensions": dimensions,
        "intersections": intersections,
        "flags": _build_flags(dimensions, intersections),
    }
