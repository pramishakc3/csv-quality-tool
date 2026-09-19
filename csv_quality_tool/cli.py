"""Command-line interface for csv_quality_tool."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

from .cleaner import clean_dataframe
from .profiler import profile_dataframe


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="csv-quality-tool",
        description="Profile and clean CSV files from the command line.",
    )
    parser.add_argument("input_csv", type=Path, help="Path to the input CSV file")
    parser.add_argument(
        "-o", "--output-csv", type=Path, default=None,
        help="Path to write the cleaned CSV (if omitted, no cleaned file is written)",
    )
    parser.add_argument(
        "--report", type=Path, default=None,
        help="Path to write the data quality report (.md or .json based on extension)",
    )
    parser.add_argument(
        "--missing-strategy", choices=["drop", "fill_mean", "none"], default="drop",
        help="How to handle missing values when cleaning (default: drop)",
    )
    parser.add_argument(
        "--no-dedupe", action="store_true", help="Do not remove duplicate rows when cleaning",
    )
    parser.add_argument(
        "--outlier-threshold", type=float, default=3.0,
        help="Z-score threshold for flagging numeric outliers (default: 3.0)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.input_csv.exists():
        print(f"Error: input file not found: {args.input_csv}", file=sys.stderr)
        return 1

    df = pd.read_csv(args.input_csv)

    report = profile_dataframe(df, outlier_threshold=args.outlier_threshold)
    print(report.to_markdown())

    if args.report:
        if args.report.suffix == ".json":
            args.report.write_text(json.dumps(report.to_dict(), indent=2))
        else:
            args.report.write_text(report.to_markdown())
        print(f"\nReport written to {args.report}")

    if args.output_csv:
        cleaned = clean_dataframe(
            df,
            missing_strategy=args.missing_strategy,
            dedupe=not args.no_dedupe,
        )
        cleaned.to_csv(args.output_csv, index=False)
        print(f"Cleaned CSV written to {args.output_csv} ({len(cleaned)} rows remaining)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
