import pandas as pd


def check_iqr_outliers(df: pd.DataFrame, column: str, multiplier: float) -> dict:

    if column not in df.columns:
        return {"status": "missing_column", "column": column}
    series = df[column].dropna()

    if series.empty:
        return {"status": "no_data", "column": column}

    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)

    iqr = q3 - q1

    lower_bound = q1 - multiplier * iqr
    upper_bound = q3 + multiplier * iqr

    outliers = (series < lower_bound) | (series > upper_bound)

    return {
        "column": column,
        "method": "iqr",
        "q1": q1,
        "q3": q3,
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
        "outlier_count": int(outliers.sum()),
        "outlier_pct": float(outliers.mean() * 100),
    }


def check_zscore_outliers(df: pd.DataFrame, column: str, threshold: float) -> dict:
    if column not in df.columns:
        return {"status": "missing_column", "column": column}
    series = df[column]

    if series.empty:
        return {"status": "empty_column", "column": column}

    mean = series.mean()
    std = series.std()

    if std == 0:
        return {
            "column": column,
            "method": "zscore",
            "outlier_count": 0,
            "status": "no_variation",
        }
    z_scores = (series - mean) / std
    outliers = z_scores.abs() > threshold

    return {
        "column": column,
        "method": "zscore",
        "threshold": threshold,
        "outlier_count": int(outliers.sum()),
        "outlier_pct": float(outliers.mean() * 100),
    }


def check_anomalies(df: pd.DataFrame, rules: list[dict]) -> list[dict]:
    results = []

    for rule in rules:
        check = rule["check"]
        column = rule["column"]

        if check == "iqr":
            result = check_iqr_outliers(df, column, rule.get("multiplier", 1.5))

        elif check == "zscore":
            result = check_zscore_outliers(df, column, rule.get("threshold", 3.0))

        else:
            result = {"column": column, "status": "unknown_rule", "rule": rule}
        results.append(result)

    return results
