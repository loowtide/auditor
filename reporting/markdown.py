from pathlib import Path


def generate_markdown_report(
    report: dict,
    output_path: str,
    issues: list[dict] | None = None,
    audit_history: list[dict] | None = None,
) -> None:
    """Generate a Markdown audit report."""

    issues = issues or []
    audit_history = audit_history or []

    # Count issues
    total_errors = sum(1 for issue in issues if issue["severity"] == "error")

    total_warnings = sum(1 for issue in issues if issue["severity"] == "warning")

    lines = []

    # -------------------------
    # Title
    # -------------------------

    lines.append("# Data Audit Report")
    lines.append("")

    # -------------------------
    # Summary
    # -------------------------

    lines.append("## Summary")
    lines.append("")

    lines.append(f"- **Errors:** {total_errors}")

    lines.append(f"- **Warnings:** {total_warnings}")

    lines.append(f"- **Total Issues:** {len(issues)}")

    lines.append("")

    if total_errors > 0:
        lines.append("**Status:**  Failed")
    else:
        lines.append("**Status:**  Passed")

    lines.append("")

    # -------------------------
    # Dataset Profile
    # -------------------------

    dataset = report["profile"]["dataset"]

    lines.append("## Dataset Profile")
    lines.append("")

    lines.append(f"- **Rows:** {dataset['rows']}")

    lines.append(f"- **Columns:** {dataset['columns']}")

    lines.append(f"- **Duplicate Rows:** {dataset['duplicate_rows']}")

    lines.append(f"- **Memory:** {dataset['memory']} bytes")

    lines.append("")

    # -------------------------
    # Issues
    # -------------------------

    lines.append("## Issues")
    lines.append("")

    if not issues:
        lines.append("No issues found.")
        lines.append("")

    else:
        lines.append("| Severity | Category | Column | Issue | Message |")

        lines.append("|---|---|---|---|---|")

        for issue in issues:
            column = issue.get("column_name") or "-"

            lines.append(
                f"| {issue['severity']} | "
                f"{issue['category']} | "
                f"{column} | "
                f"{issue['issue_type']} | "
                f"{issue['message']} |"
            )

        lines.append("")

    # -------------------------
    # Audit History
    # -------------------------

    lines.append("## Audit History")
    lines.append("")

    if not audit_history:
        lines.append("No previous audit runs found.")
        lines.append("")

    else:
        lines.append("| Run ID | Date | Status | Total Issues |")

        lines.append("|---:|---|---|---:|")

        # Oldest → newest
        for run in reversed(audit_history):
            status = run["status"]

            if status == "passed":
                status_display = "Passed"
            else:
                status_display = "Failed"

            lines.append(
                f"| {run['id']} | "
                f"{run['started_at'].strftime('%Y-%m-%d %H:%M:%S')} | "
                f"{status_display} | "
                f"{run['total_issues']} |"
            )

        lines.append("")

    # -------------------------
    # Write report
    # -------------------------

    Path(output_path).write_text(
        "\n".join(lines),
        encoding="utf-8",
    )
