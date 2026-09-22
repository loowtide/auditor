import pandas as pd


def profile_duplicates(df: pd.DataFrame) -> dict:

    duplicate_count = int(df.duplicated().sum())

    return {
        "duplicate_rows": duplicate_count,
        "duplicate_pct": (
            float(duplicate_count / len(df) * 100) if len(df) > 0 else 0.0
        ),
    }


def check_duplicate_rows(df: pd.DataFrame, allow_duplicates: bool = True) -> dict:

    duplicate_count = int(df.duplicated().sum())

    return {
        "duplicate_rows": duplicate_count,
        "status": "pass" if allow_duplicates or duplicate_count == 0 else "fail",
    }


def profile_column_uniqueness(df: pd.DataFrame) -> dict:
    result: dict = {}

    for col in df.columns:
        unique_count = int(df[col].nunique())

        result[col] = {
            "unique_count": unique_count,
            "unique_pct": (float(unique_count / len(df) * 100) if len(df) > 0 else 0.0),
        }

    return result


def check_unique_columns(df: pd.DataFrame, unique_columns: list[str]) -> dict:
    result: dict = {}

    for col in unique_columns:
        if col not in df.columns:
            result[col] = {"status": "missing_column"}
            continue

        duplicate_count = int(df[col].duplicated().sum())

        result[col] = {
            "duplicate_count": duplicate_count,
            "status": "pass" if duplicate_count == 0 else "fail",
        }

    return result


def check_uniqueness(
    df: pd.DataFrame,
    allow_duplicate_rows: bool = True,
    unique_columns: list[str] | None = None,
) -> dict:
    return {
        "duplicates": profile_duplicates(df),
        "duplicate_rows_check": check_duplicate_rows(df, allow_duplicate_rows),
        "check_unique_columns": check_unique_columns(df, unique_columns)
        if unique_columns
        else None,
        "columns": profile_column_uniqueness(df),
    }
