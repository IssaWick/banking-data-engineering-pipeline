# Pipeline Execution and Troubleshooting

## Overview

The pipeline runner executes the synthetic transaction workflow in a defined sequence and records its execution status.

## Run the Pipeline

From the project root, activate the virtual environment and run:

```powershell
python src/run_pipeline.py
```

The default run generates 1,000 synthetic transactions using a fixed random seed.

## Execution Stages

1. Generate the source transaction CSV.
2. Profile the source data.
3. Validate transactions and write valid and rejected outputs.
4. Run batch-level data quality checks.
5. Write a pipeline execution summary.

## Outputs

| Output | Purpose |
|---|---|
| `data/raw/transactions.csv` | Generated source data |
| `data/processed/valid_transactions.csv` | Accepted records |
| `data/processed/rejected_transactions.csv` | Rejected records and reasons |
| `data/processed/quality_report.json` | Batch-level data quality results |
| `data/processed/pipeline_run_summary.json` | Execution status, duration, and record counts |
| `logs/pipeline.log` | Timestamped execution log |

Generated data, reports, summaries, and logs are excluded from Git tracking.

## Execution Status

- `SUCCESS`: All pipeline stages completed and data quality checks passed.
- `FAILED`: A critical stage failed or the quality report did not pass.

## Troubleshooting

### Source dataset not found

Run the pipeline from the project root and verify that the source data generator is available.

### Missing Python dependency

Activate the virtual environment and install the requirements:

```powershell
python -m pip install -r requirements.txt
```

### Data quality failure

Inspect `data/processed/quality_report.json` and the rejected transaction output to identify the failed checks and rejection reasons.

### Pipeline execution error

Review `logs/pipeline.log` for the timestamped error and traceback.

## Current Limitations

This is a local, single-process pipeline. It does not yet use a database, distributed processing, scheduled orchestration, or cloud infrastructure. Those capabilities will be introduced incrementally.