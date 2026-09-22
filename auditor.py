from datetime import datetime, timezone

import pandas as pd
import logging
from database.repository import save_audit

from utils.anomalies import check_anomalies
from utils.completeness import check_completeness
from utils.consistency import check_consistency
from utils.integrity import check_integrity
from utils.profiling import profile_dataset
from utils.schema import check_schema
from utils.uniqueness import check_uniqueness
from utils.validity import check_validity

logger = logging.getLogger(__name__)


def extract_issues(report: dict) -> list[dict]:
    """Convert audit results into a simple list of issues."""

    issues = []

    # -------------------------
    # Schema
    # -------------------------

    schema = report["schema"]

    column_check = schema["validate_columns"]

    if column_check:
        for column in column_check["missing"]:
            issues.append(
                {
                    "category": "schema",
                    "column_name": column,
                    "issue_type": "missing_column",
                    "severity": "error",
                    "message": (f"Expected column '{column}' is missing"),
                }
            )

        for column in column_check["unexpected"]:
            issues.append(
                {
                    "category": "schema",
                    "column_name": column,
                    "issue_type": "unexpected_column",
                    "severity": "warning",
                    "message": (f"Unexpected column '{column}' found"),
                }
            )

        for actual, expected in column_check["case_mismatches"].items():
            issues.append(
                {
                    "category": "schema",
                    "column_name": actual,
                    "issue_type": "case_mismatch",
                    "severity": "warning",
                    "message": (f"Column '{actual}' should be named '{expected}'"),
                }
            )

    # Column type checks
    type_check = schema["check_column_types"]

    if type_check:
        for column in type_check["missing"]:
            issues.append(
                {
                    "category": "schema",
                    "column_name": column,
                    "issue_type": "missing_column",
                    "severity": "error",
                    "message": (
                        f"Expected column '{column}' is missing for type validation"
                    ),
                }
            )

        for column, result in type_check["mismatches"].items():
            issues.append(
                {
                    "category": "schema",
                    "column_name": column,
                    "issue_type": "type_mismatch",
                    "severity": "error",
                    "message": (
                        f"Column '{column}' has type "
                        f"'{result['actual']}', expected "
                        f"'{result['expected']}'"
                    ),
                }
            )

    # Column name checks
    for result in schema["check_column_names"]:
        issues.append(
            {
                "category": "schema",
                "column_name": result["name"],
                "issue_type": "invalid_column_name",
                "severity": "warning",
                "message": (
                    f"Column '{result['name']}' has naming issues: "
                    f"{', '.join(result['problems'])}"
                ),
            }
        )

    # Duplicate column names
    for column, indexes in schema["check_duplicate_names"].items():
        issues.append(
            {
                "category": "schema",
                "column_name": column,
                "issue_type": "duplicate_column_name",
                "severity": "error",
                "message": (f"Column name '{column}' appears multiple times"),
            }
        )

    # -------------------------
    # Completeness
    # -------------------------

    completeness = report["completeness"]

    for column, result in completeness["threshold"].items():
        if result["status"] == "fail":
            issues.append(
                {
                    "category": "completeness",
                    "column_name": column,
                    "issue_type": "missing_threshold",
                    "severity": "warning",
                    "message": (
                        f"Column '{column}' exceeds the missing-value threshold"
                    ),
                }
            )

    for column, result in completeness["required"].items():
        if result["status"] == "fail":
            issues.append(
                {
                    "category": "completeness",
                    "column_name": column,
                    "issue_type": "required_column_missing_values",
                    "severity": "error",
                    "message": (f"Required column '{column}' contains missing values"),
                }
            )

        elif result["status"] == "missing_column":
            issues.append(
                {
                    "category": "completeness",
                    "column_name": column,
                    "issue_type": "required_column_missing",
                    "severity": "error",
                    "message": (f"Required column '{column}' is missing"),
                }
            )

    # -------------------------
    # Uniqueness
    # -------------------------

    uniqueness = report["uniqueness"]

    duplicate_check = uniqueness["duplicate_rows_check"]

    if duplicate_check["status"] == "fail":
        issues.append(
            {
                "category": "uniqueness",
                "column_name": None,
                "issue_type": "duplicate_rows",
                "severity": "error",
                "message": "Duplicate rows were found",
            }
        )

    for column, result in (uniqueness["check_unique_columns"] or {}).items():
        if result["status"] == "fail":
            issues.append(
                {
                    "category": "uniqueness",
                    "column_name": column,
                    "issue_type": "duplicate_values",
                    "severity": "error",
                    "message": (f"Duplicate values found in unique column '{column}'"),
                }
            )

        elif result["status"] == "missing_column":
            issues.append(
                {
                    "category": "uniqueness",
                    "column_name": column,
                    "issue_type": "unique_column_missing",
                    "severity": "error",
                    "message": (f"Unique column '{column}' is missing"),
                }
            )

    # -------------------------
    # Validity
    # -------------------------

    for result in report["validity"]:
        if result["status"] == "fail":
            issues.append(
                {
                    "category": "validity",
                    "column_name": result.get("column"),
                    "issue_type": "invalid_value",
                    "severity": "error",
                    "message": (f"Invalid values found in '{result.get('column')}'"),
                }
            )

        elif result["status"] == "missing_column":
            issues.append(
                {
                    "category": "validity",
                    "column_name": result.get("column"),
                    "issue_type": "column_missing",
                    "severity": "error",
                    "message": (
                        f"Validity rule references missing "
                        f"column '{result.get('column')}'"
                    ),
                }
            )

    # -------------------------
    # Consistency
    # -------------------------

    for result in report["consistency"]:
        if result["status"] == "fail":
            issues.append(
                {
                    "category": "consistency",
                    "column_name": result.get("left_column"),
                    "issue_type": "column_inconsistency",
                    "severity": "error",
                    "message": ("Cross-column consistency rule failed"),
                }
            )

        elif result["status"] == "missing_column":
            issues.append(
                {
                    "category": "consistency",
                    "column_name": result.get("column"),
                    "issue_type": "column_missing",
                    "severity": "error",
                    "message": ("Consistency rule references a missing column"),
                }
            )

    # -------------------------
    # Anomalies
    # -------------------------

    for result in report["anomalies"]:
        if result.get("outlier_count", 0) > 0:
            issues.append(
                {
                    "category": "anomalies",
                    "column_name": result.get("column"),
                    "issue_type": "outlier",
                    "severity": "warning",
                    "message": (f"Outliers detected in '{result.get('column')}'"),
                }
            )

        elif result.get("status") == "missing_column":
            issues.append(
                {
                    "category": "anomalies",
                    "column_name": result.get("column"),
                    "issue_type": "column_missing",
                    "severity": "error",
                    "message": (
                        f"Anomaly rule references missing "
                        f"column '{result.get('column')}'"
                    ),
                }
            )

    # -------------------------
    # Integrity
    # -------------------------

    integrity = report["integrity"]

    if integrity["empty_dataset"]["status"] == "fail":
        issues.append(
            {
                "category": "integrity",
                "column_name": None,
                "issue_type": "empty_dataset",
                "severity": "error",
                "message": "Dataset is empty",
            }
        )

    if integrity["index"]["status"] == "warning":
        issues.append(
            {
                "category": "integrity",
                "column_name": None,
                "issue_type": "duplicate_index",
                "severity": "warning",
                "message": "Duplicate index values were found",
            }
        )

    return issues


class DataAuditor:
    def __init__(
        self,
        df: pd.DataFrame,
        dataset_name: str,
        expected_columns: list[str] | None = None,
        expected_types: dict[str, str] | None = None,
        required_columns: list[str] | None = None,
        unique_columns: list[str] | None = None,
        validity_rules: list[dict] | None = None,
        consistency_rules: list[dict] | None = None,
        anomaly_rules: list[dict] | None = None,
        missing_threshold: float = 50.0,
        allow_duplicate_rows: bool = True,
    ):

        self.df = df
        self.dataset_name = dataset_name

        self.expected_columns = expected_columns
        self.expected_types = expected_types
        self.required_columns = required_columns
        self.unique_columns = unique_columns

        self.validity_rules = validity_rules or []
        self.consistency_rules = consistency_rules or []
        self.anomaly_rules = anomaly_rules or []

        self.missing_threshold = missing_threshold
        self.allow_duplicate_rows = allow_duplicate_rows

    def run(self) -> dict:

        started_at = datetime.now()

        report = {
            "profile": profile_dataset(self.df),
            "schema": check_schema(
                self.df,
                expected_columns=self.expected_columns,
                expected_types=self.expected_types,
            ),
            "completeness": check_completeness(
                self.df,
                missing_threshold=self.missing_threshold,
                required_columns=self.required_columns,
            ),
            "uniqueness": check_uniqueness(
                self.df,
                allow_duplicate_rows=self.allow_duplicate_rows,
                unique_columns=self.unique_columns,
            ),
            "validity": check_validity(
                self.df,
                self.validity_rules,
            ),
            "consistency": check_consistency(
                self.df,
                self.consistency_rules,
            ),
            "anomalies": check_anomalies(
                self.df,
                self.anomaly_rules,
            ),
            "integrity": check_integrity(self.df),
        }

        # Convert audit results into issues
        issues = extract_issues(report)

        finished_at = datetime.now()

        audit_run_id = None
        try:
            audit_run_id = save_audit(
                dataset_name=self.dataset_name,
                issues=issues,
                started_at=started_at,
                finished_at=finished_at,
            )
        except Exception as e:
            logger.error(f"Failed to save_audit: {e}")
            audit_run_id = -1
        return {
            "report": report,
            "issues": issues,
            "audit_run_id": audit_run_id,
        }
