"""Data quality profiling for a pandas DataFrame."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


@dataclass
class ColumnReport:
    name: str
    dtype: str
    missing_count: int
    missing_pct: float
    unique_count: int
    outlier_count: int = 0
    sample_values: list = field(default_factory=list)


@dataclass
class QualityReport:
    row_count: int
    column_count: int
    duplicate_row_count: int
    columns: list[ColumnReport]

    def to_markdown(self) -> str:
        lines = [
            "# Data Quality Report",
            "",
            f"- **Rows:** {self.row_count}",
            f"- **Columns:** {self.column_count}",
            f"- **Duplicate rows:** {self.duplicate_row_count}",
            "",
            "## Column Summary",
            "",
            "| Column | Type | Missing | Missing % | Unique | Outliers |",
            "|---|---|---|---|---|---|",
        ]
        for col in self.columns:
            lines.append(
                f"| {col.name} | {col.dtype} | {col.missing_count} | "
                f"{col.missing_pct:.1f}% | {col.unique_count} | {col.outlier_count} |"
            )
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "row_count": self.row_count,
            "column_count": self.column_count,
            "duplicate_row_count": self.duplicate_row_count,
            "columns": [
                {
                    "name": c.name,
                    "dtype": c.dtype,
                    "missing_count": c.missing_count,
                    "missing_pct": round(c.missing_pct, 2),
                    "unique_count": c.unique_count,
                    "outlier_count": c.outlier_count,
                    "sample_values": c.sample_values,
                }
                for c in self.columns
            ],
        }


def _detect_outliers_zscore(series: pd.Series, threshold: float = 3.0) -> int:
    """Count outliers in a numeric series using the z-score method.

    Returns 0 for non-numeric series or series with zero/near-zero variance,
    rather than raising, since a data quality report should degrade
    gracefully on messy real-world columns.
    """
    numeric = pd.to_numeric(series, errors="coerce").dropna()
    if len(numeric) < 3 or numeric.std(ddof=0) == 0:
        return 0
    z_scores = np.abs((numeric - numeric.mean()) / numeric.std(ddof=0))
    return int((z_scores > threshold).sum())


def profile_dataframe(df: pd.DataFrame, outlier_threshold: float = 3.0) -> QualityReport:
    """Build a QualityReport summarising missingness, duplicates, and outliers."""
    row_count = len(df)
    duplicate_row_count = int(df.duplicated().sum())

    column_reports = []
    for col_name in df.columns:
        series = df[col_name]
        missing_count = int(series.isna().sum())
        missing_pct = (missing_count / row_count * 100) if row_count else 0.0
        unique_count = int(series.nunique(dropna=True))

        outlier_count = 0
        if pd.api.types.is_numeric_dtype(series):
            outlier_count = _detect_outliers_zscore(series, outlier_threshold)

        sample_values = series.dropna().unique()[:3].tolist()

        column_reports.append(
            ColumnReport(
                name=str(col_name),
                dtype=str(series.dtype),
                missing_count=missing_count,
                missing_pct=missing_pct,
                unique_count=unique_count,
                outlier_count=outlier_count,
                sample_values=sample_values,
            )
        )

    return QualityReport(
        row_count=row_count,
        column_count=len(df.columns),
        duplicate_row_count=duplicate_row_count,
        columns=column_reports,
    )
