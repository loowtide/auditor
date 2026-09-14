import pandas as pd

from .type_infer import infer_column


def profile_dataset_level(df: pd.DataFrame) -> dict:
    return {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "duplicate_rows": df.duplicated().sum(),
        "memory": df.memory_usage(deep=True).sum(),
    }


def profile_columns(df: pd.DataFrame) -> dict:
    columns = {}

    for column in df.columns:
        series = df[column]
        columns[column] = {
            "type": infer_column(series),
            "count": int(series.count()),
            "missing_count": int(series.isna().sum()),
            "missing_pct": float(series.isna().mean() * 100),
            "unique_cnt": int(series.nunique()),
            "unique_pct": 0.0
            if len(df) == 0
            else float(series.nunique() / len(df) * 100),
        }
    return columns


def profile_numeric_summary(df: pd.DataFrame) -> dict:
    columns = {}

    for column in df.columns:
        series = df[column]
        if infer_column(series) == "numeric":
            columns[column] = {
                "name": column,
                "min": float(series.min()),
                "max": float(series.max()),
                "mean": float(series.mean()),
                "median": float(series.median()),
                "std": float(series.std()),
            }

    return columns


def profile_categorical_summary(df: pd.DataFrame) -> dict:
    columns = {}

    for column in df.columns:
        series = df[column]
        if infer_column(series) == "categorical":
            counts = series.value_counts()
            if counts.empty:
                columns[column] = {
                    "name": column,
                    "unique": 0,
                    "top": None,
                    "top_frequency": 0.0,
                }
            else:
                columns[column] = {
                    "name": column,
                    "unique": int(series.nunique()),
                    "top": counts.index[0],
                    "top_frequency": float(
                        series.value_counts(normalize=True).iloc[0] * 100
                    ),
                }

    return columns


def profile_datetime(df: pd.DataFrame) -> dict:
    columns = {}

    for column in df.columns:
        series = df[column]

        if infer_column(series) == "datetime":
            columns[column] = {
                "name": column,
                "min": series.min(),
                "max": series.max(),
                "unique": int(series.nunique()),
                "missing": int(series.isna().sum()),
            }

    return columns


def profile_dataset(df: pd.DataFrame) -> dict:
    return {
        "dataset": profile_dataset_level(df),
        "columns": profile_columns(df),
        "numeric": profile_numeric_summary(df),
        "categorical": profile_categorical_summary(df),
        "datetime": profile_datetime(df),
    }
