# Data Quality Standards

## Purpose

This document defines the initial quality checks used by the Banking Data Engineering Pipeline.

## Transaction-Level Validation

Each transaction is checked for:

- Presence of all required fields
- Transaction ID format and uniqueness within the input batch
- Account ID format
- Valid transaction timestamp
- Positive, finite amount with no more than two decimal places
- Supported transaction currency
- Allowed transaction type, channel, status, and merchant category

Records that fail validation are written to a rejected-record output with their rejection reasons.

## Batch-Level Quality Checks

The quality report checks:

1. **Source reconciliation:** Source record count equals valid record count plus rejected record count.
2. **Completeness:** Accepted records have no missing required values.
3. **Uniqueness:** Accepted records have unique transaction IDs.
4. **Rejection rate:** Rejected records must not exceed 5% of the source batch.
5. **Non-empty output:** At least one accepted record must remain.

## Batch Status

- `PASS`: All configured quality checks pass.
- `FAIL`: At least one quality check fails.

The 5% rejection threshold is a configurable learning-project default, not a universal banking requirement.

## Limitations

These checks are an initial quality framework. They do not yet cover all possible banking business rules, such as account balances, cross-system reconciliation, or whether a transaction is economically valid.

Further validation will be added as the project evolves.