import pandas as pd


def profile_missing(df: pd.DataFrame) -> dict:
    result: dict = {}

    for col in df.columns:
        missing_count = int(df[col].isna().sum())

        result[col] = {
            "missing_count": missing_count,
            "missing_pct": float(df[col].isna().mean() * 100),
        }
    return result


def check_missing_threshold(df: pd.DataFrame, threshold: float = 50.0) -> dict:
    result: dict = {}

    for col in df.columns:
        missing_pct = float(df[col].isna().mean() * 100)

        result[col] = {
            "missing_pct": missing_pct,
            "status": "fail" if missing_pct > threshold else "pass",
        }

    return result


def check_required_columns(
    df: pd.DataFrame, required_columns: list[str] | None
) -> dict:
    result: dict = {}

    if required_columns is None:
        return result

    for col in required_columns:
        if col not in df.columns:
            result[col] = {"status": "missing_column"}
            continue
        missing_count = int(df[col].isna().sum())
        result[col] = {
            "missing_count": missing_count,
            "status": "pass" if missing_count == 0 else "fail",
        }

    return result


def check_completeness(
    df: pd.DataFrame,
    missing_threshold: float = 50,
    required_columns: list[str] | None = None,
) -> dict:
    return {
        "missing": profile_missing(df),
        "threshold": check_missing_threshold(df, missing_threshold),
        "required": check_required_columns(df, required_columns)
        if required_columns
        else None,
    }
