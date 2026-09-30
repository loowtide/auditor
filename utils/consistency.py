import pandas as pd


def check_column_relation(
    df: pd.DataFrame, left_column: str, operator: str, right_column: str
) -> dict:
    if left_column not in df.columns:
        return {"status": "missing_column", "column": left_column}
    if right_column not in df.columns:
        return {"status": "missing_column", "column": right_column}

    left = df[left_column]
    right = df[right_column]

    if operator == "<=":
        valid = left <= right
    elif operator == "<":
        valid = left < right
    elif operator == ">=":
        valid = left >= right
    elif operator == ">":
        valid = left > right
    elif operator == "==":
        valid = left == right
    elif operator == "!=":
        valid = left != right

    else:
        return {"status": "unknown_operator", "operator": operator}
    invalid_count = int((~valid).sum())

    return {
        "left_column": left_column,
        "operator": operator,
        "right_column": right_column,
        "invalid_count": invalid_count,
        "status": "pass" if invalid_count == 0 else "fail",
    }


# check if one column exists so do the second
def check_cross_column_nullity(
    df: pd.DataFrame, source_column: str, required_column: str
) -> dict:
    if source_column not in df.columns:
        return {"status": "missing_column", "column": source_column}
    if required_column not in df.columns:
        return {"status": "missing_column", "column": required_column}

    invalid = df[source_column].notna() & df[required_column].isna()

    invalid_count = int(invalid.sum())

    return {
        "source_column": source_column,
        "required_column": required_column,
        "invalid_count": invalid_count,
        "status": "pass" if invalid_count == 0 else "fail",
    }


def check_consistency(df: pd.DataFrame, rules: list[dict]) -> list[dict]:
    results = []

    for rule in rules:
        check = rule["check"]

        if check == "column_relation":
            result = check_column_relation(
                df, rule["left"], rule["operator"], rule["right"]
            )
        elif check == "cross_column_nullity":
            result = check_cross_column_nullity(df, rule["source"], rule["required"])
        else:
            result = {"status": "unknown_rule", "rule": check}
        results.append(result)
    return results
