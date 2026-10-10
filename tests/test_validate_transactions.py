
import pandas as pd
import pytest

from src.validation import validate_transactions as validator


def make_transaction(transaction_id="TXN000001"):
    return {
        "transaction_id": transaction_id,
        "account_id": "ACC0001",
        "transaction_timestamp": "2026-01-15 09:30:00",
        "transaction_type": "debit",
        "amount": "2500.00",
        "currency": "LKR",
        "channel": "mobile",
        "status": "completed",
        "merchant_category": "groceries",
    }


@pytest.fixture
def output_paths(tmp_path, monkeypatch):
    source = tmp_path / "transactions.csv"
    processed_dir = tmp_path / "processed"

    monkeypatch.setattr(validator, "INPUT_FILE", source)
    monkeypatch.setattr(validator, "PROCESSED_DIR", processed_dir)
    monkeypatch.setattr(
        validator, "VALID_FILE", processed_dir / "valid.csv"
    )
    monkeypatch.setattr(
        validator, "REJECTED_FILE", processed_dir / "rejected.csv"
    )

    return source, processed_dir


def test_valid_transaction_is_accepted(output_paths):
    source, processed_dir = output_paths

    pd.DataFrame([make_transaction()]).to_csv(source, index=False)

    valid_count, rejected_count = validator.validate_transactions()

    assert valid_count == 1
    assert rejected_count == 0

    valid = pd.read_csv(processed_dir / "valid.csv")
    assert len(valid) == 1


def test_invalid_amount_is_rejected(output_paths):
    source, processed_dir = output_paths

    transaction = make_transaction()
    transaction["amount"] = "-500"

    pd.DataFrame([transaction]).to_csv(source, index=False)

    valid_count, rejected_count = validator.validate_transactions()

    assert valid_count == 0
    assert rejected_count == 1

    rejected = pd.read_csv(processed_dir / "rejected.csv")
    assert "invalid_amount" in rejected.iloc[0]["rejection_reason"]


def test_duplicate_transaction_id_is_rejected(output_paths):
    source, processed_dir = output_paths

    transactions = [
        make_transaction(),
        make_transaction(),
    ]

    pd.DataFrame(transactions).to_csv(source, index=False)

    valid_count, rejected_count = validator.validate_transactions()

    assert valid_count == 1
    assert rejected_count == 1

    rejected = pd.read_csv(processed_dir / "rejected.csv")
    assert (
        "duplicate_transaction_id"
        in rejected.iloc[0]["rejection_reason"]
    )


def test_missing_required_column_fails(output_paths):
    source, _ = output_paths

    transaction = make_transaction()
    del transaction["amount"]

    pd.DataFrame([transaction]).to_csv(source, index=False)

    with pytest.raises(ValueError, match="Missing required columns"):
        validator.validate_transactions()
