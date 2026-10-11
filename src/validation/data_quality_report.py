
import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SOURCE_FILE = PROJECT_ROOT / "data" / "raw" / "transactions.csv"
VALID_FILE = PROJECT_ROOT / "data" / "processed" / "valid_transactions.csv"
REJECTED_FILE = PROJECT_ROOT / "data" / "processed" / "rejected_transactions.csv"
REPORT_FILE = PROJECT_ROOT / "data" / "processed" / "quality_report.json"

REQUIRED_COLUMNS = [
    "transaction_id",
    "account_id",
    "transaction_timestamp",
    "transaction_type",
    "amount",
    "currency",
    "channel",
    "status",
    "merchant_category",
]

MAX_REJECTION_RATE_PERCENT = 5.0


def run_quality_report() -> dict:
    """Calculate batch-level quality metrics and save a JSON report."""

    for path in (SOURCE_FILE, VALID_FILE, REJECTED_FILE):
        if not path.exists():
            raise FileNotFoundError(
                f"Required pipeline output not found: {path}. "
                "Generate the source data and run validation first."
            )

    source = pd.read_csv(SOURCE_FILE, dtype=str, keep_default_na=False)
    valid = pd.read_csv(VALID_FILE, dtype=str, keep_default_na=False)
    rejected = pd.read_csv(REJECTED_FILE, dtype=str, keep_default_na=False)

    source_count = len(source)
    valid_count = len(valid)
    rejected_count = len(rejected)

    rejection_rate = (
        rejected_count / source_count * 100
        if source_count
        else 0.0
    )

    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in valid.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Valid output is missing columns: {missing_columns}"
        )

    missing_values = int(
        valid[REQUIRED_COLUMNS]
        .apply(lambda column: column.str.strip().eq(""))
        .sum()
        .sum()
    )

    duplicate_ids = int(
        valid["transaction_id"].duplicated().sum()
    )

    checks = {
        "source_reconciles_with_outputs": (
            source_count == valid_count + rejected_count
        ),
        "valid_output_has_no_missing_values": missing_values == 0,
        "valid_output_has_unique_transaction_ids": duplicate_ids == 0,
        "rejection_rate_within_threshold": (
            rejection_rate <= MAX_REJECTION_RATE_PERCENT
        ),
        "valid_output_is_not_empty": valid_count > 0,
    }

    report = {
        "source_records": source_count,
        "valid_records": valid_count,
        "rejected_records": rejected_count,
        "rejection_rate_percent": round(rejection_rate, 2),
        "missing_values_in_valid_output": missing_values,
        "duplicate_transaction_ids_in_valid_output": duplicate_ids,
        "maximum_rejection_rate_percent": MAX_REJECTION_RATE_PERCENT,
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "FAIL",
    }

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    REPORT_FILE.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print("\n=== DATA QUALITY REPORT ===")
    print(json.dumps(report, indent=2))
    print(f"\nReport saved to: {REPORT_FILE}")

    return report


if __name__ == "__main__":
    run_quality_report()
