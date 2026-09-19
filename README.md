# CSV Quality Tool

A command-line tool for profiling and cleaning messy CSV data. Built with
Python and pandas.

## Why

Real-world CSVs are rarely clean: inconsistent column names, stray
whitespace, duplicate rows, missing values, and numeric outliers are all
common. This tool gives you a quick, scriptable way to see what's wrong
with a CSV before deciding how to fix it, and then optionally clean it.

## Features

- **Data quality report**: row/column counts, missing values (count and
  %), duplicate rows, unique value counts, and numeric outlier detection
  (z-score based), output as Markdown or JSON.
- **Cleaning pipeline**: standardizes column names to `snake_case`, trims
  whitespace, drops duplicate rows, and handles missing values with a
  configurable strategy (`drop`, `fill_mean`, or `none`).
- **CLI-first**: designed to be scripted or dropped into a data pipeline.

## Installation

```bash
git clone https://github.com/pramishakc3/csv-quality-tool.git
cd csv-quality-tool
pip install -r requirements.txt
```

## Usage

Profile a CSV and print the report to the console:

```bash
python -m csv_quality_tool.cli sample_data/customers_messy.csv
```

Profile, write a report, and produce a cleaned CSV:

```bash
python -m csv_quality_tool.cli sample_data/customers_messy.csv \
  --report report.md \
  --output-csv customers_cleaned.csv \
  --missing-strategy drop
```

### Options

| Flag | Description | Default |
|---|---|---|
| `--output-csv PATH` | Write the cleaned CSV to this path | (not written) |
| `--report PATH` | Write the report as `.md` or `.json` | (not written) |
| `--missing-strategy {drop,fill_mean,none}` | How to handle missing values | `drop` |
| `--no-dedupe` | Skip duplicate-row removal | dedupe on |
| `--outlier-threshold FLOAT` | Z-score threshold for flagging outliers | `3.0` |

## Example

Given `sample_data/customers_messy.csv` (duplicate rows, inconsistent
column names, stray whitespace, missing values, and an age of 120):

```
# Data Quality Report

- **Rows:** 10
- **Columns:** 5
- **Duplicate rows:** 1

## Column Summary

| Column | Type | Missing | Missing % | Unique | Outliers |
|---|---|---|---|---|---|
| Customer ID | int64 | 0 | 0.0% | 9 | 0 |
|  Full Name  | str | 1 | 10.0% | 8 | 0 |
| Age | float64 | 1 | 10.0% | 8 | 0 |
|   Signup Date | str | 1 | 10.0% | 8 | 0 |
| Annual Spend | float64 | 1 | 10.0% | 8 | 0 |
```

## Design notes

- **Outlier detection uses population z-score**, which is simple and fast
  but has a known limitation: a single extreme outlier can inflate the
  standard deviation enough to "mask" itself in small samples. This is
  documented in the test suite (`test_outlier_detection_flags_extreme_value`)
  with a note on why the test uses a larger sample rather than a
  minimal one.
- **Cleaning order is fixed and deliberate**: column names are
  standardized first (so later steps can rely on consistent naming),
  then whitespace is trimmed, then duplicates are dropped, then missing
  values are handled last (so duplicate rows don't skew a `fill_mean`
  calculation).

## Running tests

```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```

17 tests covering the profiler and cleaner modules, including edge cases
(constant-value columns, non-numeric columns, invalid strategies).

## License

MIT
