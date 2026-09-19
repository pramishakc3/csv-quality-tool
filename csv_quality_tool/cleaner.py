"""Cleaning operations for a pandas DataFrame."""

from __future__ import annotations

import re

import pandas as pd


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Lowercase, strip, and snake_case all column names."""
    new_columns = {}
    for col in df.columns:
        name = str(col).strip().lower()
        name = re.sub(r"[^\w\s]", "", name)
        name = re.sub(r"\s+", "_", name)
        new_columns[col] = name
    return df.rename(columns=new_columns)


def trim_whitespace(df: pd.DataFrame) -> pd.DataFrame:
    """Strip leading/trailing whitespace from all string/object columns."""
    df = df.copy()
    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
    return df


def drop_duplicate_rows(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates().reset_index(drop=True)


def handle_missing(df: pd.DataFrame, strategy: str = "drop") -> pd.DataFrame:
    """Handle missing values.

    strategy:
      - "drop": drop any row containing a missing value
      - "fill_mean": fill numeric columns with column mean, others with mode
      - "none": leave missing values untouched
    """
    if strategy == "none":
        return df
    if strategy == "drop":
        return df.dropna().reset_index(drop=True)
    if strategy == "fill_mean":
        df = df.copy()
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(df[col].mean())
            else:
                mode = df[col].mode(dropna=True)
                if not mode.empty:
                    df[col] = df[col].fillna(mode.iloc[0])
        return df
    raise ValueError(f"Unknown missing-value strategy: {strategy!r}")


def clean_dataframe(
    df: pd.DataFrame,
    missing_strategy: str = "drop",
    dedupe: bool = True,
    standardize_columns: bool = True,
    strip_whitespace: bool = True,
) -> pd.DataFrame:
    """Run the full cleaning pipeline in a sensible, fixed order."""
    if standardize_columns:
        df = standardize_column_names(df)
    if strip_whitespace:
        df = trim_whitespace(df)
    if dedupe:
        df = drop_duplicate_rows(df)
    df = handle_missing(df, strategy=missing_strategy)
    return df
