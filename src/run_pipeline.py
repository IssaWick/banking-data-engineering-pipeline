
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    # Imports when run as a module or imported by tests.
    from .ingestion.generate_transactions import generate_transactions
    from .ingestion.profile_transactions import profile_transactions
    from .validation.validate_transactions import validate_transactions
    from .validation.data_quality_report import run_quality_report
    from .pipeline_logging import configure_logging

except ImportError:
    # Imports when executed directly:
    # python src/run_pipeline.py
    from ingestion.generate_transactions import generate_transactions
    from ingestion.profile_transactions import profile_transactions
    from validation.validate_transactions import validate_transactions
    from validation.data_quality_report import run_quality_report
    from pipeline_logging import configure_logging

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOG_FILE = PROJECT_ROOT / "logs" / "pipeline.log"

SUMMARY_FILE = (
    PROJECT_ROOT / "data" / "processed" / "pipeline_run_summary.json"
)


def run_pipeline(
    row_count: int = 1000,
    seed: int = 42,
) -> dict:
    """Execute the complete local transaction data pipeline."""

    logger = configure_logging(LOG_FILE)
    started_at = datetime.now(timezone.utc)
    start_time = time.perf_counter()

    summary = {
        "started_at": started_at.isoformat(),
        "finished_at": None,
        "duration_seconds": None,
        "status": "FAILED",
        "source_records": 0,
        "valid_records": 0,
        "rejected_records": 0,
        "quality_status": "NOT_RUN",
        "error": None,
    }

    logger.info("Pipeline execution started.")
    logger.info("Requested rows: %s | Random seed: %s", row_count, seed)

    try:
        logger.info("Stage 1/4: Generate source transactions.")
        generate_transactions(row_count=row_count, seed=seed)

        logger.info("Stage 2/4: Profile source transactions.")
        profile_transactions()

        logger.info("Stage 3/4: Validate transactions.")
        valid_count, rejected_count = validate_transactions()

        logger.info("Stage 4/4: Run data quality checks.")
        quality_report = run_quality_report()

        summary["source_records"] = row_count
        summary["valid_records"] = valid_count
        summary["rejected_records"] = rejected_count
        summary["quality_status"] = quality_report["status"]

        if quality_report["status"] != "PASS":
            raise RuntimeError(
                "Data quality checks failed. "
                "Review the quality report before proceeding."
            )

        summary["status"] = "SUCCESS"
        logger.info("All pipeline stages completed successfully.")

    except Exception as exc:
        summary["error"] = str(exc)
        logger.exception("Pipeline execution failed.")
        raise

    finally:
        summary["finished_at"] = datetime.now(timezone.utc).isoformat()
        summary["duration_seconds"] = round(
            time.perf_counter() - start_time,
            3,
        )

        SUMMARY_FILE.parent.mkdir(parents=True, exist_ok=True)
        SUMMARY_FILE.write_text(
            json.dumps(summary, indent=2),
            encoding="utf-8",
        )

        logger.info(
            "Pipeline finished | status=%s | duration_seconds=%s",
            summary["status"],
            summary["duration_seconds"],
        )
        logger.info("Run summary saved to %s", SUMMARY_FILE)

    return summary


if __name__ == "__main__":
    try:
        result = run_pipeline()
        print("\nPipeline status:", result["status"])
    except Exception:
        raise SystemExit(1)
