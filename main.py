import pandas as pd

from auditor import DataAuditor
from database.connection import create_tables
from database.repository import get_audit_history
from reporting.markdown import generate_markdown_report


def main():

    # Create database tables if they don't exist
    create_tables()

    dataset_name = "sample.csv"

    # Load CSV
    df = pd.read_csv(f"data/{dataset_name}")

    # Create auditor
    auditor = DataAuditor(
        df=df,
        dataset_name=dataset_name,
        expected_columns=[
            "id",
            "name",
            "age",
            "status",
        ],
        expected_types={
            "id": "numeric",
            "name": "text",
            "age": "numeric",
            "status": "categorical",
        },
        required_columns=[
            "id",
            "name",
        ],
        unique_columns=[
            "id",
        ],
        validity_rules=[
            {
                "column": "age",
                "check": "range",
                "min": 0,
                "max": 120,
            },
            {
                "column": "status",
                "check": "allowed_values",
                "values": [
                    "active",
                    "inactive",
                ],
            },
        ],
        consistency_rules=[],
        anomaly_rules=[
            {
                "column": "age",
                "check": "iqr",
            },
        ],
        missing_threshold=50.0,
        allow_duplicate_rows=False,
    )

    # Run audit
    # This also saves the result to PostgreSQL
    result = auditor.run()

    # Get previous audit runs
    audit_history = get_audit_history(
        dataset_name=dataset_name,
        limit=10,
    )

    # Generate Markdown report
    generate_markdown_report(
        report=result["report"],
        issues=result["issues"],
        audit_history=audit_history,
        output_path="audit_report.md",
    )

    print("Audit completed successfully.")

    print(f"Audit Run ID: {result['audit_run_id']}")

    print(f"Total Issues: {len(result['issues'])}")


if __name__ == "__main__":
    main()
