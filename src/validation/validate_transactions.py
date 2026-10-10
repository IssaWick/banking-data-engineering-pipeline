
import argparse
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "transactions.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

VALID_FILE = PROCESSED_DIR / "valid_transactions.csv"
REJECTED_FILE = PROCESSED_DIR / "rejected_transactions.csv"

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

ALLOWED_TYPES = {
    "debit", "credit", "transfer", "fee", "refund"
}

ALLOWED_CHANNELS = {
    "mobile", "online", "ATM", "POS", "branch"
}

ALLOWED_STATUSES = {
    "completed", "pending", "failed", "reversed"
}

ALLOWED_CATEGORIES = {
    "groceries", "utilities", "dining", "transport",
    "salary", "transfer", "cash_withdrawal", "fees", "other"
}


def validate_transactions() -> tuple[int, int]:
    """Validate source transactions and save valid and rejected records."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Source dataset not found: {INPUT_FILE}. "
            "Run generate_transactions.py first."
        )

    # Read all source fields as text to preserve identifiers and raw values.
    df = pd.read_csv(
        INPUT_FILE,
        dtype=str,
        keep_default_na=False,
    )

    missing_columns = set(REQUIRED_COLUMNS) - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    # Keep the original input values for rejected-record investigation.
    df = df[REQUIRED_COLUMNS].copy()

    # Each row collects its own validation errors.
    errors = [[] for _ in range(len(df))]

    def reject(mask: pd.Series, reason: str) -> None:
        for position in range(len(df)):
            if bool(mask.iloc[position]):
                errors[position].append(reason)

    # 1. Required fields must not be empty.
    for column in REQUIRED_COLUMNS:
        missing = df[column].str.strip().eq("")
        reject(missing, f"missing_{column}")

    # 2. Transaction identifiers must be unique.
    transaction_ids = df["transaction_id"].str.strip()
    has_id = transaction_ids.ne("")

    duplicate_ids = (
        has_id
        & transaction_ids.duplicated(keep="first")
    )
    reject(duplicate_ids, "duplicate_transaction_id")

    # 3. Timestamps must be parseable.
    timestamps = pd.to_datetime(
        df["transaction_timestamp"],
        format="%Y-%m-%d %H:%M:%S",
        errors="coerce",
    )

    invalid_timestamp = timestamps.isna()
    reject(invalid_timestamp, "invalid_transaction_timestamp")

    # 4. Amounts must be numeric and greater than zero.
    amounts = pd.to_numeric(df["amount"], errors="coerce")

    invalid_amount = amounts.isna() | amounts.le(0)
    reject(invalid_amount, "invalid_amount")

    # 5. Categorical fields must contain allowed values.
    reject(
        ~df["transaction_type"].isin(ALLOWED_TYPES),
        "invalid_transaction_type",
    )

    reject(
        ~df["channel"].isin(ALLOWED_CHANNELS),
        "invalid_channel",
    )

    reject(
        ~df["status"].isin(ALLOWED_STATUSES),
        "invalid_status",
    )

    reject(
        ~df["merchant_category"].isin(ALLOWED_CATEGORIES),
        "invalid_merchant_category",
    )

    # 6. This initial dataset supports LKR only.
    reject(
        df["currency"].ne("LKR"),
        "unsupported_currency",
    )

    # Store all rejection reasons rather than only the first.
    df["rejection_reason"] = [
        ";".join(row_errors) for row_errors in errors
    ]

    valid_mask = df["rejection_reason"].eq("")

    valid_df = df.loc[valid_mask, REQUIRED_COLUMNS].copy()
    rejected_df = df.loc[~valid_mask].copy()

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    valid_df.to_csv(VALID_FILE, index=False)
    rejected_df.to_csv(REJECTED_FILE, index=False)

    print("=== TRANSACTION VALIDATION REPORT ===")
    print(f"Source records: {len(df)}")
    print(f"Valid records: {len(valid_df)}")
    print(f"Rejected records: {len(rejected_df)}")
    print(f"Valid output: {VALID_FILE}")
    print(f"Rejected output: {REJECTED_FILE}")

    if not rejected_df.empty:
        print("\nRejection reasons:")
        reason_counts = (
            rejected_df["rejection_reason"]
            .str.split(";")
            .explode()
            .value_counts()
        )

        for reason, count in reason_counts.items():
            print(f"  {reason}: {count}")

    return len(valid_df), len(rejected_df)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate synthetic banking transactions."
    )

    parser.parse_args()
    validate_transactions()


if __name__ == "__main__":
    main()
