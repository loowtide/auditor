from .type_infer import infer_column

import re
import pandas as pd


def check_column_names(df: pd.DataFrame) -> dict:
    issues: dict[str, list[str]] = {}

    for i, col in enumerate(df.columns):
        problems: list[str] = []
        name = str(col)

        # check for empty column name
        if name.strip() == "":
            problems.append("Empty/Blank name")

        # check for leading/trailing whitespaces
        if name != name.strip():
            problems.append("Leading/Trailing whitespaces")

        # check for non ASCII column name
        if not name.isascii():
            problems.append("Non-ASCII characters")

        # internal double spaces
        if "  " in name:
            problems.append("Double spaces present")

        # starts with a digit
        if name[:1].isdigit():
            problems.append("Starts with a digit")

        # check special characters
        special = set(re.findall(r"[^a-zA-Z0-9_]", name))
        if special:
            problems.append(f"Special characters {sorted(special)}")

        # tab / newline / non breaking spaces
        if re.search(r"[\t\n\r\xa0]", name):
            problems.append(" Tab/Newline/nbsp char")

        if problems:
            issues[f"[{i}] {name!r}"] = problems

    return issues


def check_duplicate_names(df: pd.DataFrame) -> dict[str, list[int]]:
    seen: dict[str, list[int]] = {}

    for i, col in enumerate(df.columns):
        seen.setdefault(col, []).append(i)

    return {col: idx for col, idx in seen.items() if len(idx) > 1}


def check_naming_convention(df: pd.DataFrame):
    pass


# check column types -> user scheme
def check_column_types(
    df: pd.DataFrame, expected_types: dict[str, str] | None = None
) -> dict | None:

    if not expected_types:
        return None

    cols = {c.lower(): c for c in df.columns}
    mismatches: dict[str, dict[str, str]] = {}
    missing: list[str] = []

    for key, value in expected_types.items():
        real = cols.get(key.lower())
        if real is None:
            missing.append(key)
            continue

        actual_type = str(infer_column(df[real])).lower()
        expected_type = str(value).lower()

        if actual_type != expected_type:
            mismatches[real] = {"expected": expected_type, "actual": actual_type}

    return {
        "valid": not (mismatches or missing),
        "missing": missing,
        "mismatches": mismatches,
    }


# check column present in dataset
def validate_columns(df: pd.DataFrame, expected_cols: list[str]) -> dict:
    actual = {c.lower(): c for c in df.columns}
    expected_lower: dict[str, str] = {c.lower(): c for c in expected_cols}

    missing = [orig for low, orig in expected_lower.items() if low not in actual]

    case_mismatches = {
        actual[low]: orig
        for low, orig in expected_lower.items()
        if low in actual and actual[low] != orig
    }

    unexpected = [orig for low, orig in actual.items() if low not in expected_lower]
    result = {
        "missing": missing,
        "case_mismatches": case_mismatches,
        "unexpected": unexpected,
    }

    return result


def check_schema(
    df: pd.DataFrame,
    expected_cols: list[str] | None = None,
    expected_types: dict[str, str] | None = None,
) -> dict:
    return {
        "check_column_names": check_column_names(df),
        "check_column_types": check_column_types(df, expected_types),
        "check_duplicate_names": check_duplicate_names(df),
        "validate_columns": validate_columns(df, expected_cols)
        if expected_cols
        else None,
    }
