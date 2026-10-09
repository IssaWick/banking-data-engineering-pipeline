# Banking Transaction Data Dictionary

## Purpose

This document defines the structure and expected values of the synthetic banking transaction dataset used in the Banking Data Engineering Pipeline.

All records are fictional and intended for educational purposes.

## Dataset: Transactions

| Column                | Data Type | Description                          | Example             |
| --------------------- | --------- | ------------------------------------ | ------------------- |
| transaction_id        | String    | Unique transaction identifier        | TXN000001           |
| account_id            | String    | Identifier of the associated account | ACC0012             |
| transaction_timestamp | Timestamp | Date and time of the transaction     | 2026-01-15 09:30:00 |
| transaction_type      | String    | Type of transaction                  | debit               |
| amount                | Decimal   | Positive transaction amount          | 2500.00             |
| currency              | String    | Currency code                        | LKR                 |
| channel               | String    | Transaction channel                  | mobile              |
| status                | String    | Transaction processing status        | completed           |
| merchant_category     | String    | Transaction or merchant category     | groceries           |

## Expected Values

* `transaction_id`: Unique and non-empty.
* `account_id`: Non-empty account identifier.
* `transaction_timestamp`: Valid timestamp.
* `transaction_type`: One of debit, credit, transfer, fee, or refund.
* `amount`: Greater than zero, with two decimal places.
* `currency`: LKR for this initial dataset.
* `channel`: One of mobile, online, ATM, POS, or branch.
* `status`: One of completed, pending, failed, or reversed.
* `merchant_category`: One of groceries, utilities, dining, transport, salary, transfer, cash_withdrawal, fees, or other.

## Initial Data Contract

The initial source dataset will contain 1,000 synthetic transaction records.

The dataset will be generated reproducibly using Python, allowing the same input parameters and random seed to produce the same records.

Data validation and rejection rules will be implemented in later stages of the project.

## Scope

This is a simulated transaction feed, not a representation of an actual banking system. The initial version focuses on ingestion, schema understanding, data validation, and storage.
