"""Demographic column auto-detection.

Implements section 1 of faircode/SPEC.md. Kept dependency-free (no pandas import
required for the matching logic) so the keyword lists stay the single source of
truth that the JS port mirrors verbatim.
"""

from __future__ import annotations

import re

# Keyword lists — order matters; the first dimension that matches wins.
# Mirror these exactly in assets/profiler-engine.js.
KEYWORDS: list[tuple[str, tuple[str, ...]]] = [
    ("sex", ("sex", "gender")),
    ("race", ("race", "ethnic", "ethnicity")),
    ("age", ("age", "dob", "yob", "birth")),
    ("geography", ("region", "state", "zip", "zipcode", "postal", "country",
                   "county", "city", "location", "province")),
]

MAX_CATEGORICAL_CARD = 20


def _tokens(name: str) -> list[str]:
    """Split a column name into lower-case tokens on separators AND camelCase.

    'DateOfBirth' -> ['date','of','birth']; 'Sex_Code_Text' -> ['sex','code','text'];
    'ageGroup' -> ['age','group']. This token boundary is what stops 'age' from
    matching 'Agency_Text' or 'Language'.
    """
    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", str(name))
    return [t.lower() for t in re.split(r"[^A-Za-z0-9]+", spaced) if t]


def _token_matches(token: str, keyword: str) -> bool:
    """Exact match for short keywords (<4 chars); prefix match for longer ones.

    Prefix (not substring) avoids 'age' matching 'agency' while still catching
    'agegroup', 'statecode', 'ethnicity', etc.
    """
    if len(keyword) < 4:
        return token == keyword
    return token.startswith(keyword)


def classify_name(name: str) -> str | None:
    """Return the dimension kind for a column name, or None if no keyword matches."""
    tokens = _tokens(name)
    for kind, words in KEYWORDS:
        if any(_token_matches(tok, word) for tok in tokens for word in words):
            return kind
    return None


def detect_columns(df) -> list[dict]:
    """Detect demographic columns in a DataFrame.

    Returns a list of {"name": str, "kind": str} dicts. Keyword-matched columns
    are always kept; unmatched columns are kept as generic "categorical" only
    when their distinct non-null value count is in [2, MAX_CATEGORICAL_CARD].
    """
    detected: list[dict] = []
    for col in df.columns:
        kind = classify_name(col)
        if kind is not None:
            detected.append({"name": col, "kind": kind})
            continue
        # Generic categorical fallback for low-cardinality columns.
        series = df[col].dropna()
        n_unique = series.nunique()
        if 2 <= n_unique <= MAX_CATEGORICAL_CARD:
            detected.append({"name": col, "kind": "categorical"})
    return detected
