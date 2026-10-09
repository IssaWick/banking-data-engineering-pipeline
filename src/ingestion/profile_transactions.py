
import csv
from collections import Counter
from decimal import Decimal
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "transactions.csv"


def profile_transactions() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {INPUT_FILE}\n"
            "Run generate_transactions.py first."
        )

    row_count = 0
    transaction_ids = set()
    duplicate_ids = 0
    amounts = []

    missing_values = Counter()
    transaction_types = Counter()
    statuses = Counter()

    with INPUT_FILE.open(
        mode="r",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        for row in reader:
            row_count += 1

            for column, value in row.items():
                if value is None or not value.strip():
                    missing_values[column] += 1

            transaction_id = row["transaction_id"]

            if transaction_id in transaction_ids:
                duplicate_ids += 1
            else:
                transaction_ids.add(transaction_id)

            transaction_types[row["transaction_type"]] += 1
            statuses[row["status"]] += 1

            if row["amount"].strip():
                amounts.append(Decimal(row["amount"]))

    print("\n=== TRANSACTION DATA PROFILE ===")
    print(f"Total records: {row_count}")
    print(f"Unique transaction IDs: {len(transaction_ids)}")
    print(f"Duplicate transaction IDs: {duplicate_ids}")

    print("\nMissing values by column:")

    for column, count in sorted(missing_values.items()):
        print(f"  {column}: {count}")

    print("\nTransaction type counts:")

    for name, count in sorted(transaction_types.items()):
        print(f"  {name}: {count}")

    print("\nTransaction status counts:")

    for name, count in sorted(statuses.items()):
        print(f"  {name}: {count}")

    if amounts:
        total = sum(amounts, Decimal("0"))

        print("\nAmount statistics (LKR):")
        print(f"  Minimum: {min(amounts):.2f}")
        print(f"  Maximum: {max(amounts):.2f}")
        print(f"  Average: {total / len(amounts):.2f}")


if __name__ == "__main__":
    profile_transactions()