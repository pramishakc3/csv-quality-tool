import pandas as pd
import pytest

from csv_quality_tool.profiler import profile_dataframe, _detect_outliers_zscore


def test_profile_counts_rows_and_columns():
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    report = profile_dataframe(df)
    assert report.row_count == 3
    assert report.column_count == 2


def test_profile_counts_missing_values():
    df = pd.DataFrame({"a": [1, None, 3], "b": ["x", "y", None]})
    report = profile_dataframe(df)
    col_a = next(c for c in report.columns if c.name == "a")
    col_b = next(c for c in report.columns if c.name == "b")
    assert col_a.missing_count == 1
    assert col_b.missing_count == 1
    assert col_a.missing_pct == pytest.approx(33.33, abs=0.1)


def test_profile_counts_duplicate_rows():
    df = pd.DataFrame({"a": [1, 1, 2], "b": ["x", "x", "y"]})
    report = profile_dataframe(df)
    assert report.duplicate_row_count == 1


def test_outlier_detection_flags_extreme_value():
    # A larger, realistic sample: with only a handful of points, a single
    # extreme outlier inflates the standard deviation enough to mask
    # itself (z-score "masking"), so this needs enough normal points for
    # the outlier to actually stand out.
    normal_values = [10, 11, 9, 10, 12, 11, 9, 10, 12, 11, 10, 9, 11, 10, 12]
    series = pd.Series(normal_values + [500])
    outliers = _detect_outliers_zscore(series, threshold=3.0)
    assert outliers == 1


def test_outlier_detection_handles_constant_series():
    series = pd.Series([5, 5, 5, 5])
    outliers = _detect_outliers_zscore(series)
    assert outliers == 0


def test_outlier_detection_handles_non_numeric_gracefully():
    series = pd.Series(["a", "b", "c"])
    outliers = _detect_outliers_zscore(series)
    assert outliers == 0


def test_report_to_dict_roundtrip():
    df = pd.DataFrame({"a": [1, 2, None]})
    report = profile_dataframe(df)
    d = report.to_dict()
    assert d["row_count"] == 3
    assert d["columns"][0]["name"] == "a"


def test_report_to_markdown_contains_header():
    df = pd.DataFrame({"a": [1, 2, 3]})
    report = profile_dataframe(df)
    md = report.to_markdown()
    assert "# Data Quality Report" in md
    assert "a" in md
