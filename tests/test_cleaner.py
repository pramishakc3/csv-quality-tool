import pandas as pd

from csv_quality_tool.cleaner import (
    standardize_column_names,
    trim_whitespace,
    drop_duplicate_rows,
    handle_missing,
    clean_dataframe,
)


def test_standardize_column_names():
    df = pd.DataFrame(columns=["Customer ID", " Full Name ", "Annual Spend!"])
    result = standardize_column_names(df)
    assert list(result.columns) == ["customer_id", "full_name", "annual_spend"]


def test_trim_whitespace():
    df = pd.DataFrame({"name": [" Alice ", "Bob  ", "  Charlie"]})
    result = trim_whitespace(df)
    assert list(result["name"]) == ["Alice", "Bob", "Charlie"]


def test_trim_whitespace_ignores_non_string_columns():
    df = pd.DataFrame({"age": [29, 41, 35]})
    result = trim_whitespace(df)
    assert list(result["age"]) == [29, 41, 35]


def test_drop_duplicate_rows():
    df = pd.DataFrame({"a": [1, 1, 2], "b": ["x", "x", "y"]})
    result = drop_duplicate_rows(df)
    assert len(result) == 2


def test_handle_missing_drop_strategy():
    df = pd.DataFrame({"a": [1, None, 3]})
    result = handle_missing(df, strategy="drop")
    assert len(result) == 2


def test_handle_missing_fill_mean_strategy():
    df = pd.DataFrame({"a": [1.0, None, 3.0]})
    result = handle_missing(df, strategy="fill_mean")
    assert result["a"].iloc[1] == 2.0


def test_handle_missing_none_strategy_leaves_data_untouched():
    df = pd.DataFrame({"a": [1, None, 3]})
    result = handle_missing(df, strategy="none")
    assert result["a"].isna().sum() == 1


def test_handle_missing_invalid_strategy_raises():
    df = pd.DataFrame({"a": [1, None, 3]})
    try:
        handle_missing(df, strategy="bogus")
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_clean_dataframe_full_pipeline():
    df = pd.DataFrame({
        "Customer ID ": [1, 1, 2],
        " Name": [" Alice ", " Alice ", "Bob"],
    })
    result = clean_dataframe(df, missing_strategy="drop")
    assert list(result.columns) == ["customer_id", "name"]
    assert len(result) == 2  # duplicate row removed
