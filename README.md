# Auditor

Data-quality auditor for pandas DataFrames. It runs schema, completeness, uniqueness, validity, consistency, anomaly and integrity checks, saves each run to PostgreSQL, and writes a Markdown report.

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- PostgreSQL

## Setup

```bash
uv sync
createdb data_audit
export DATABASE_URL="postgresql+psycopg2://postgres@localhost:5432/data_audit"
```

`DATABASE_URL` defaults to the value above if not set.

## Usage

```bash
uv run main.py
```

This audits `data/sample.csv` and writes `audit_report.md`. Edit `main.py` to change the dataset or rules.

```python
from auditor import DataAuditor
from database.connection import create_tables

create_tables()  # once, before running audits

result = DataAuditor(
    df=df,
    dataset_name="sample.csv",
    expected_columns=["id", "name", "age", "status"],
    expected_types={"id": "numeric", "name": "text", "age": "numeric", "status": "categorical"},
    required_columns=["id", "name"],
    unique_columns=["id"],
    validity_rules=[...],
    consistency_rules=[...],
    anomaly_rules=[...],
    missing_threshold=50.0,
    allow_duplicate_rows=False,
).run()
```

`run()` returns `report`, `issues` and `audit_run_id` (`-1` if the database save failed).

## Types

`numeric`, `text`, `categorical`, `datetime`, `boolean`. Aliases such as `date`, `int` and `string` are accepted in `expected_types`.

## Rules

**Validity**

```python
{"column": "age", "check": "range", "min": 0, "max": 120}
{"column": "status", "check": "allowed_values", "values": ["active", "inactive"]}
{"column": "code", "check": "pattern", "pattern": r"^[A-Z]{3}$"}
```

**Consistency**

```python
{"check": "column_relation", "left": "start", "operator": "<=", "right": "end"}
{"check": "cross_column_nullity", "source": "email", "required": "name"}
```

**Anomalies**

```python
{"column": "age", "check": "iqr", "multiplier": 1.5}
{"column": "age", "check": "zscore", "threshold": 3.0}
```

## Project layout

```
auditor.py      DataAuditor and issue extraction
main.py         Example run
utils/          Individual checks and type inference
database/       PostgreSQL connection and audit storage
reporting/      Markdown report generator
data/           Sample datasets
```
