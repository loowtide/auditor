import pandas as pd


def check_numeric_range(
    df: pd.DataFrame,
    column: str,
    min_value: float | None = None,
    max_value: float | None = None,
) -> dict:
    if column not in df.columns:
        return {"column":column,"status": "column_missing"}

    series = df[column]

    if not pd.api.types.is_numeric_dtype(series):
        return {"column":column,"status":"invalid_rule"}

    invalid = pd.Series(False, df.index)

    if min_value is not None:
        invalid |= series < min_value
    if max_value is not None:
        invalid |= series > max_value

    invalid_count = int(invalid.sum())

    return {
        "column": column,
        "invalid_count": invalid_count,
        "invalid_pct": float(invalid.mean() * 100),
        "status": "pass" if invalid_count == 0 else "fail",
    }


# check allowed values for categorical columns
def check_allowed_values(
    df: pd.DataFrame, column: str, allowed_values: list[str]
) -> dict:
    if column not in df.columns:
        return {"column":column,"status": "column_missing"}

    invalid = ~df[column].isin(allowed_values)
    invalid_count = int(invalid.sum())

    return {
        "column": column,
        "invalid_count": invalid_count,
        "invalid_values": df.loc[invalid, column].dropna().unique().tolist(),
        "status": "pass" if invalid_count == 0 else "fail",
    }


def check_pattern(df: pd.DataFrame, column: str, pattern: str) -> dict:
    if column not in df.columns:
        return {"column":column,"status": "column_missing"}

    series = df[column].dropna().astype(str)

    valid = series.str.match(pattern, na=False)
    invalid_count = int((~valid).sum())

    return {
        "column": column,
        "invalid_count": invalid_count,
        "status": "pass" if invalid_count == 0 else "fail",
    }


def check_validity(df: pd.DataFrame, rules: list[dict]) -> list[dict]:
    results = []
    """
    rules format -> list of dict

    rule=[
        {
            "column":"",
            "check":"range",
            "min":0.0,
            "max":120
        },
        {
            "column":"",
            "check":"allowed_values",
            "values":[]
        },
        {
            "column":"",
            "check":"pattern",
            "pattern":r"^[A-Z]"
        },
    ]

    """
    for rule in rules:
        column = rule["column"]
        check = rule["check"]

        if check == "range":
            result = check_numeric_range(
                df, column, rule.get("min"), rule.get("max")
            )
        elif check == "allowed_values":
            result = check_allowed_values(df, column, rule["values"])
        elif check == "pattern":
            result = check_pattern(df, column, rule["pattern"])
        else:
            result = {"column": column, "status": "unknown_rule", "rule": check}
        results.append(result)

    return results
