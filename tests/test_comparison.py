"""
Tests for the comparison data generator module.
"""

import pytest
import pandas as pd
from src.analyzer.comparison import (
    generate_algorithm_comparison,
    generate_threat_timeline,
    generate_speedup_factors,
    generate_security_gauge_data,
)


def test_algorithm_comparison_shape():
    df = generate_algorithm_comparison()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 5
    expected_cols = {
        "Algorithm",
        "Key Size Efficiency",
        "Classical Security",
        "Quantum Resistance",
        "Performance Speed",
        "Standardization Maturity",
    }
    assert expected_cols == set(df.columns)


def test_algorithm_comparison_values_in_range():
    df = generate_algorithm_comparison()
    numeric_cols = df.select_dtypes(include="number").columns
    for col in numeric_cols:
        assert df[col].min() >= 0
        assert df[col].max() <= 100


def test_threat_timeline_ordered():
    df = generate_threat_timeline()
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 8
    assert "Year" in df.columns
    assert "Event" in df.columns
    # Should be sorted by year
    years = df["Year"].tolist()
    assert years == sorted(years)


def test_speedup_factors_structure():
    bits = [32, 64, 128]
    df = generate_speedup_factors(bits)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3
    assert "Factorization Speedup" in df.columns
    assert "Search Speedup" in df.columns
    # Speedup should be > 1 for key sizes >= 32 bits
    assert all(df["Factorization Speedup"] > 1)
    assert all(df["Search Speedup"] > 1)


def test_speedup_factors_increasing():
    bits = [16, 32, 48, 64]
    df = generate_speedup_factors(bits)
    speedups = df["Factorization Speedup"].tolist()
    # Speedup should generally increase with key size
    assert speedups[-1] > speedups[0]


def test_security_gauge_data():
    data = generate_security_gauge_data()
    assert isinstance(data, list)
    assert len(data) >= 5
    for entry in data:
        assert "Algorithm" in entry
        assert "Classical Security (bits)" in entry
        assert "Quantum Security (bits)" in entry
        assert "Status" in entry
        assert entry["Classical Security (bits)"] >= 0
        assert entry["Quantum Security (bits)"] >= 0
