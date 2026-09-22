import os

from sqlalchemy import create_engine, text


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres@localhost:5432/data_audit",
)


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


def create_tables() -> None:
    """Create the audit tables if they do not exist."""

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS audit_runs (
                    id SERIAL PRIMARY KEY,
                    dataset_name VARCHAR(255) NOT NULL,
                    started_at TIMESTAMP NOT NULL,
                    finished_at TIMESTAMP NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    total_issues INTEGER NOT NULL DEFAULT 0
                )
                """
            )
        )

        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS audit_issues (
                    id SERIAL PRIMARY KEY,
                    audit_run_id INTEGER NOT NULL
                        REFERENCES audit_runs(id),
                    category VARCHAR(100) NOT NULL,
                    column_name VARCHAR(255),
                    issue_type VARCHAR(100) NOT NULL,
                    severity VARCHAR(50) NOT NULL,
                    message TEXT NOT NULL
                )
                """
            )
        )
