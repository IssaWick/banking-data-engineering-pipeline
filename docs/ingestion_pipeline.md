# Transaction Ingestion and Validation

## Overview

The initial ingestion workflow reads a synthetic banking transaction CSV, checks the input against the expected data contract, and separates accepted and rejected records.

## Workflow

1. Generate the source dataset using the Python data generator.
2. Read the CSV with Pandas.
3. Verify that all required columns exist.
4. Validate required fields, transaction identifiers, timestamps, amounts, currency, and allowed categorical values.
5. Write accepted records to `data/processed/valid_transactions.csv`.
6. Write rejected records and their rejection reasons to `data/processed/rejected_transactions.csv`.
7. Run automated tests to verify the validation behavior.

## Commands

Generate source data:

```bash
python src/ingestion/generate_transactions.py
```

Run validation:

```bash
python src/validation/validate_transactions.py
```

Run automated tests:

```bash
python -m pytest tests/test_validate_transactions.py -v
```

## Output Files

- `valid_transactions.csv`: records that pass all implemented validation rules.
- `rejected_transactions.csv`: records that fail validation, including one or more rejection reasons.

## Current Limitations

- The pipeline currently processes a local CSV file.
- It writes results to local CSV files rather than a database.
- Validation rules cover the initial transaction data contract, not every real-world banking rule.
- The pipeline does not yet provide scheduled execution, incremental loading, or production monitoring.

## Next Steps

Extend validation, add data quality metrics, and introduce database loading in subsequent stages of the project.