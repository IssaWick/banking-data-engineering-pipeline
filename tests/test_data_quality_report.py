
import pandas as pd

from src.validation import data_quality_report as quality_report
from src.validation.validate_transactions import REQUIRED_COLUMNS


def make_transaction(number):
    return {
        "transaction_id": f"TXN{number:06d}",
        "account_id": "ACC0001",
        "transaction_timestamp": "2026-01-15 09:30:00",
        "transaction_type": "debit",
        "amount": "2500.00",
        "currency": "LKR",
        "channel": "mobile",
        "status": "completed",
        "merchant_category": "groceries",
    }


def configure_report_paths(tmp_path, monkeypatch):
    source = tmp_path / "source.csv"
    valid = tmp_path / "valid.csv"
    rejected = tmp_path / "rejected.csv"
    report = tmp_path / "quality_report.json"

    monkeypatch.setattr(quality_report, "SOURCE_FILE", source)
    monkeypatch.setattr(quality_report, "VALID_FILE", valid)
    monkeypatch.setattr(quality_report, "REJECTED_FILE", rejected)
    monkeypatch.setattr(quality_report, "REPORT_FILE", report)

    return source, valid, rejected, report


def test_quality_report_passes_for_clean_batch(tmp_path, monkeypatch):
    source, valid, rejected, report_path = configure_report_paths(
        tmp_path, monkeypatch
    )

    transactions = [
        make_transaction(1),
        make_transaction(2),
    ]

    pd.DataFrame(transactions).to_csv(source, index=False)
    pd.DataFrame(transactions).to_csv(valid, index=False)
    pd.DataFrame(columns=REQUIRED_COLUMNS + ["rejection_reason"]).to_csv(
        rejected, index=False
    )

    report = quality_report.run_quality_report()

    assert report["status"] == "PASS"
    assert report["source_records"] == 2
    assert report["valid_records"] == 2
    assert report["rejected_records"] == 0
    assert report_path.exists()


def test_quality_report_fails_when_rejection_rate_is_too_high(
    tmp_path, monkeypatch
):
    source, valid, rejected, _ = configure_report_paths(
        tmp_path, monkeypatch
    )

    transactions = [
        make_transaction(number)
        for number in range(1, 11)
    ]

    pd.DataFrame(transactions).to_csv(source, index=False)
    pd.DataFrame(transactions[:9]).to_csv(valid, index=False)

    rejected_row = make_transaction(10)
    rejected_row["rejection_reason"] = "invalid_amount"

    pd.DataFrame([rejected_row]).to_csv(rejected, index=False)

    report = quality_report.run_quality_report()

    assert report["rejection_rate_percent"] == 10.0
    assert report["checks"]["source_reconciles_with_outputs"]
    assert not report["checks"]["rejection_rate_within_threshold"]
    assert report["status"] == "FAIL"
