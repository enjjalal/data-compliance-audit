import argparse
from pathlib import Path
from typing import List

import pandas as pd

from tagging_engine import scan_dataframe, results_to_dataframe


def find_csvs(data_dir: Path) -> List[Path]:
    return sorted(p for p in data_dir.glob("*.csv"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan CSVs for PII by column name and values")
    parser.add_argument("--data-dir", default="data", help="Directory containing CSV files")
    parser.add_argument("--out", default="outputs/pii_scan.csv", help="Path to write CSV report")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    all_results = []
    for csv_path in find_csvs(data_dir):
        df = pd.read_csv(csv_path)
        table_name = csv_path.stem
        all_results.extend(scan_dataframe(df, table_name))

    report_df = results_to_dataframe(all_results)
    report_df.to_csv(out_path, index=False)
    print(f"Wrote PII scan report to {out_path.as_posix()} ({len(report_df)} rows)")


if __name__ == "__main__":
    main()


