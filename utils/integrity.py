import pandas as pd


def check_empty_dataset(df: pd.DataFrame) -> dict:
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "is_empty": df.empty,
        "status": "fail" if df.empty else "pass",
    }


def check_index_integrity(df: pd.DataFrame) -> dict:
    duplicate_index_count = int(df.index.duplicated().sum())

    return {
        "duplicate_index_count": duplicate_index_count,
        "status": ("pass" if duplicate_index_count == 0 else "warning"),
    }


def check_integrity(df: pd.DataFrame) -> dict:
    return {
        "empty_dataset": check_empty_dataset(df),
        "index": check_index_integrity(df),
    }
