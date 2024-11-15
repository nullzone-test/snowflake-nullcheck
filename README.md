# snowflake-nullcheck

Lightweight null value detection and data quality testing framework for Snowflake.

## Overview

`snowflake-nullcheck` scans your Snowflake tables for null-value patterns that violate declared contracts — missing NOT NULL constraints, unexpected nulls in join keys, and temporal gaps in time-series data.

## Features

- **Contract validation** — Declare expected non-null columns in YAML, get alerts when violations occur
- **Join key integrity** — Detect nulls in foreign key columns that silently drop rows in joins
- **Temporal coverage** — Find gaps in time-series tables where null timestamps indicate missing data
- **Snowflake-native** — Uses INFORMATION_SCHEMA + RESULT_SCAN for zero-copy profiling
- **CI-ready** — Exit codes for pass/fail, JUnit XML output for CI integration

## Installation

```bash
pip install snowflake-nullcheck
```

## Quick Start

```yaml
# nullcheck.yaml
connection: my_snowflake_conn
targets:
  - database: ANALYTICS
    schema: CORE
    tables:
      - name: ORDERS
        required_columns: [ORDER_ID, CUSTOMER_ID, ORDER_DATE, TOTAL_AMOUNT]
      - name: CUSTOMERS
        required_columns: [CUSTOMER_ID, EMAIL, CREATED_AT]
        join_keys: [CUSTOMER_ID]
```

```bash
nullcheck scan --config nullcheck.yaml
```

## Output

```
snowflake-nullcheck v0.4.2 — scanning 2 tables in ANALYTICS.CORE

ORDERS
  ✓ ORDER_ID        — 0 nulls / 1,284,301 rows (0.000%)
  ✓ CUSTOMER_ID     — 0 nulls / 1,284,301 rows (0.000%)
  ✗ ORDER_DATE      — 47 nulls / 1,284,301 rows (0.004%)
  ✓ TOTAL_AMOUNT    — 0 nulls / 1,284,301 rows (0.000%)

CUSTOMERS
  ✓ CUSTOMER_ID     — 0 nulls / 89,412 rows (0.000%)
  ✗ EMAIL           — 1,203 nulls / 89,412 rows (1.345%)
  ✓ CREATED_AT      — 0 nulls / 89,412 rows (0.000%)

Summary: 2 violations found across 2 tables
Exit code: 1
```

## Configuration

See [docs/configuration.md](docs/configuration.md) for full reference.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT
