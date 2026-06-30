"""Tests for the Fair Code dataset profiler.

Run from the repo root:  pytest tests/ -q
"""

import math
from pathlib import Path

import pandas as pd
import pytest

from faircode import profile
from faircode.detect import classify_name, detect_columns
from faircode.profiler import _age_band, _age_to_numeric, _skewness

ROOT = Path(__file__).resolve().parent.parent


# ── Column detection ────────────────────────────────────────────────────────
def test_classify_keyword_columns():
    assert classify_name("gender") == "sex"
    assert classify_name("Sex_Code_Text") == "sex"
    assert classify_name("race") == "race"
    assert classify_name("Ethnic_Code_Text") == "race"
    assert classify_name("age") == "age"
    assert classify_name("DateOfBirth") == "age"
    assert classify_name("region") == "geography"
    assert classify_name("native.country") == "geography"


def test_classify_rejects_false_positives():
    # The bugs that token-matching fixes: 'age' must not match these.
    assert classify_name("Agency_Text") is None
    assert classify_name("Language") is None
    assert classify_name("LegalStatus") is None


def test_detect_includes_low_cardinality_categorical():
    df = pd.DataFrame({"smoker": ["y", "n"] * 25})
    kinds = {d["name"]: d["kind"] for d in detect_columns(df)}
    assert kinds["smoker"] == "categorical"


def test_high_cardinality_id_excluded_from_categorical():
    df = pd.DataFrame({"uid": [f"u{i}" for i in range(100)]})
    assert detect_columns(df) == []  # 100 distinct > MAX_CATEGORICAL_CARD


# ── Age helpers ──────────────────────────────────────────────────────────────
def test_age_to_numeric():
    assert _age_to_numeric(34) == 34.0
    assert _age_to_numeric("[70-80)") == 70.0
    assert _age_to_numeric(None) is None
    assert _age_to_numeric("n/a") is None


def test_age_band_edges():
    assert _age_band(0) == "0-18"
    assert _age_band(17) == "0-18"
    assert _age_band(18) == "18-30"
    assert _age_band(80) == "75+"


def test_skewness_symmetric_is_zero():
    assert abs(_skewness([1, 2, 3, 4, 5])) < 1e-9


# ── Core metrics ─────────────────────────────────────────────────────────────
def test_balanced_binary_scores_high():
    df = pd.DataFrame({"sex": ["M", "F"] * 50})
    result = profile(df)
    dim = result["dimensions"][0]
    assert dim["dimension_score"] == 100
    assert math.isclose(dim["entropy_ratio"], 1.0, abs_tol=1e-9)
    assert dim["under_represented"] == []


def test_skewed_distribution_flags_under_represented():
    df = pd.DataFrame({"sex": ["M"] * 98 + ["F"] * 2})
    result = profile(df)
    dim = result["dimensions"][0]
    assert "F" in dim["under_represented"]
    assert dim["dimension_score"] < 50
    assert any("under-represented" in f for f in result["flags"])


def test_single_group_scores_zero():
    df = pd.DataFrame({"sex": ["M"] * 100})
    # one distinct value -> not a valid categorical (needs >=2), so not detected by
    # cardinality; but the name 'sex' is keyword-detected regardless.
    result = profile(df)
    dim = result["dimensions"][0]
    assert dim["dimension_score"] == 0


def test_empty_demographics_overall_zero():
    # High-cardinality continuous columns -> nothing detected as demographic.
    df = pd.DataFrame({"price": [i * 1.5 for i in range(100)],
                       "qty": list(range(100))})
    result = profile(df)
    assert result["overall_score"] == 0
    assert result["grade"] == "F"
    assert result["dimensions"] == []


# ── End-to-end on bundled datasets ───────────────────────────────────────────
@pytest.mark.parametrize("csv", [
    "Insurance Denial/insurance.csv",
    "Benefits Denial/adult.csv",
])
def test_real_datasets_produce_sane_result(csv):
    path = ROOT / csv
    if not path.exists():
        pytest.skip(f"dataset not present: {csv}")
    result = profile(pd.read_csv(path))
    assert result["n_rows"] > 0
    assert 0 <= result["overall_score"] <= 100
    assert result["grade"] in {"A", "B", "C", "D", "F"}
    kinds = {d["kind"] for d in result["dimensions"]}
    assert "age" in kinds and "sex" in kinds  # both datasets have age + sex


def test_date_column_dropped_not_garbage():
    # A birthdate column must not become 6 nonsense age bands.
    df = pd.DataFrame({
        "DateOfBirth": [f"{1+i%12:02d}/05/19{40+i%50:02d}" for i in range(200)],
        "sex": ["M", "F"] * 100,
    })
    result = profile(df)
    names = {d["name"] for d in result["dimensions"]}
    assert "DateOfBirth" not in names
    assert "sex" in names
