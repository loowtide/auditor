import pandas as pd


def infer_column(series: pd.Series) -> str:
    non_null = series.dropna()

    if non_null.empty:
        return "unknown"

    if pd.api.types.is_bool_dtype(series):
        return "boolean"

    if isinstance(series.dtype, pd.CategoricalDtype):
        return "categorical"

    if pd.api.types.is_numeric_dtype(series):
        return "numeric"

    if pd.api.types.is_bool_dtype(series):
        return "boolean"

    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"

    if pd.api.types.is_object_dtype(series):
        unique_ratio = non_null.nunique() / len(non_null)

        if unique_ratio < 0.05:
            return "categorical"

        return "text"

    return "unknown"
