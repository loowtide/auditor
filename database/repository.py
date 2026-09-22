from datetime import datetime

from sqlalchemy import text

from .connection import engine


def save_audit(
    dataset_name: str,
    issues: list[dict],
    started_at: datetime,
    finished_at: datetime,
) -> int:
    """Save one audit run and all of its issues."""

    total_issues = len(issues)

    total_errors = sum(1 for issue in issues if issue["severity"] == "error")

    status = "failed" if total_errors > 0 else "passed"

    with engine.begin() as connection:
        # Save the audit run
        result = connection.execute(
            text(
                """
                INSERT INTO audit_runs (
                    dataset_name,
                    started_at,
                    finished_at,
                    status,
                    total_issues
                )
                VALUES (
                    :dataset_name,
                    :started_at,
                    :finished_at,
                    :status,
                    :total_issues
                )
                RETURNING id
                """
            ),
            {
                "dataset_name": dataset_name,
                "started_at": started_at,
                "finished_at": finished_at,
                "status": status,
                "total_issues": total_issues,
            },
        )

        audit_run_id = result.scalar_one()

        # Save individual issues
        for issue in issues:
            connection.execute(
                text(
                    """
                    INSERT INTO audit_issues (
                        audit_run_id,
                        category,
                        column_name,
                        issue_type,
                        severity,
                        message
                    )
                    VALUES (
                        :audit_run_id,
                        :category,
                        :column_name,
                        :issue_type,
                        :severity,
                        :message
                    )
                    """
                ),
                {
                    "audit_run_id": audit_run_id,
                    "category": issue["category"],
                    "column_name": issue.get("column_name"),
                    "issue_type": issue["issue_type"],
                    "severity": issue["severity"],
                    "message": issue["message"],
                },
            )

    return audit_run_id


def get_audit_history(
    dataset_name: str,
    limit: int = 10,
) -> list[dict]:
    """Return previous audit runs for a dataset."""

    with engine.connect() as connection:
        result = connection.execute(
            text(
                """
                SELECT
                    id,
                    dataset_name,
                    started_at,
                    finished_at,
                    status,
                    total_issues
                FROM audit_runs
                WHERE dataset_name = :dataset_name
                ORDER BY started_at DESC
                LIMIT :limit
                """
            ),
            {
                "dataset_name": dataset_name,
                "limit": limit,
            },
        )

        return [dict(row._mapping) for row in result]


def get_audit_issues(
    audit_run_id: int,
) -> list[dict]:
    """Return all issues for one audit run."""

    with engine.connect() as connection:
        result = connection.execute(
            text(
                """
                SELECT
                    id,
                    audit_run_id,
                    category,
                    column_name,
                    issue_type,
                    severity,
                    message
                FROM audit_issues
                WHERE audit_run_id = :audit_run_id
                ORDER BY id
                """
            ),
            {
                "audit_run_id": audit_run_id,
            },
        )

        return [dict(row._mapping) for row in result]
