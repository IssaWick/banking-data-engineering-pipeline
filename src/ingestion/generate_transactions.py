
import argparse
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path


# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Output location for raw transaction data
OUTPUT_FILE = PROJECT_ROOT / "data" / "raw" / "transactions.csv"

# Allowed values defined in our data dictionary
TRANSACTION_TYPES = [
    "debit",
    "credit",
    "transfer",
    "fee",
    "refund",
]

CHANNELS = [
    "mobile",
    "online",
    "ATM",
    "POS",
    "branch",
]

STATUSES = [
    "completed",
    "pending",
    "failed",
    "reversed",
]

MERCHANT_CATEGORIES = [
    "groceries",
    "utilities",
    "dining",
    "transport",
    "salary",
    "transfer",
    "cash_withdrawal",
    "fees",
    "other",
]

COLUMNS = [
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


def generate_transactions(row_count: int, seed: int) -> None:
    """Generate reproducible synthetic banking transactions."""

    random.seed(seed)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    start_date = datetime(2026, 1, 1)
    date_range_seconds = 270 * 24 * 60 * 60

    with OUTPUT_FILE.open(
        mode="w",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=COLUMNS,
        )

        writer.writeheader()

        for number in range(1, row_count + 1):
            transaction_time = start_date + timedelta(
                seconds=random.randint(
                    0,
                    date_range_seconds,
                )
            )

            transaction = {
                "transaction_id": f"TXN{number:06d}",
                "account_id": (
                    f"ACC{random.randint(1, 200):04d}"
                ),
                "transaction_timestamp": (
                    transaction_time.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                ),
                "transaction_type": random.choice(
                    TRANSACTION_TYPES
                ),
                "amount": f"{random.uniform(10, 100000):.2f}",
                "currency": "LKR",
                "channel": random.choice(CHANNELS),
                "status": random.choice(STATUSES),
                "merchant_category": random.choice(
                    MERCHANT_CATEGORIES
                ),
            }

            writer.writerow(transaction)

    print(f"Generated {row_count} transactions.")
    print(f"Output file: {OUTPUT_FILE}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate synthetic banking transactions."
    )

    parser.add_argument(
        "--rows",
        type=int,
        default=1000,
        help="Number of transactions to generate.",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible data.",
    )

    args = parser.parse_args()

    if args.rows < 1:
        parser.error("--rows must be at least 1.")

    generate_transactions(
        row_count=args.rows,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()