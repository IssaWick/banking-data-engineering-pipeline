
import json

import pytest

from src import run_pipeline as pipeline


def test_pipeline_runs_all_stages_in_order(tmp_path, monkeypatch):
    calls = []

    monkeypatch.setattr(
        pipeline, "LOG_FILE", tmp_path / "logs" / "pipeline.log"
    )
    monkeypatch.setattr(
        pipeline, "SUMMARY_FILE", tmp_path / "summary.json"
    )

    def generate_transactions(row_count, seed):
        calls.append(("generate", row_count, seed))

    def profile_transactions():
        calls.append(("profile",))

    def validate_transactions():
        calls.append(("validate",))
        return 9, 1

    def run_quality_report():
        calls.append(("quality",))
        return {
            "status": "PASS",
            "checks": {"source_reconciles_with_outputs": True},
        }

    monkeypatch.setattr(
        pipeline, "generate_transactions", generate_transactions
    )
    monkeypatch.setattr(
        pipeline, "profile_transactions", profile_transactions
    )
    monkeypatch.setattr(
        pipeline, "validate_transactions", validate_transactions
    )
    monkeypatch.setattr(
        pipeline, "run_quality_report", run_quality_report
    )

    result = pipeline.run_pipeline(row_count=10, seed=42)

    assert [call[0] for call in calls] == [
        "generate", "profile", "validate", "quality"
    ]
    assert calls[0] == ("generate", 10, 42)
    assert result["status"] == "SUCCESS"
    assert result["valid_records"] == 9
    assert result["rejected_records"] == 1

    saved_summary = json.loads(
        (tmp_path / "summary.json").read_text(encoding="utf-8")
    )
    assert saved_summary["status"] == "SUCCESS"


def test_pipeline_fails_when_quality_checks_fail(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(
        pipeline, "LOG_FILE", tmp_path / "logs" / "pipeline.log"
    )
    monkeypatch.setattr(
        pipeline, "SUMMARY_FILE", tmp_path / "summary.json"
    )

    monkeypatch.setattr(
        pipeline, "generate_transactions", lambda **kwargs: None
    )
    monkeypatch.setattr(
        pipeline, "profile_transactions", lambda: None
    )
    monkeypatch.setattr(
        pipeline, "validate_transactions", lambda: (8, 2)
    )
    monkeypatch.setattr(
        pipeline,
        "run_quality_report",
        lambda: {"status": "FAIL", "checks": {}},
    )

    with pytest.raises(RuntimeError, match="Data quality checks failed"):
        pipeline.run_pipeline()

    saved_summary = json.loads(
        (tmp_path / "summary.json").read_text(encoding="utf-8")
    )
    assert saved_summary["status"] == "FAILED"
    assert saved_summary["quality_status"] == "FAIL"
