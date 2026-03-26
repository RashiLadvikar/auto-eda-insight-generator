import pandas as pd
import numpy as np


def get_basic_overview(df: pd.DataFrame) -> dict:
    """Return high-level dataset overview metrics."""
    total_cells = df.shape[0] * df.shape[1]
    missing_cells = int(df.isna().sum().sum())
    duplicate_rows = int(df.duplicated().sum())

    return {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "missing_cells": missing_cells,
        "missing_percent": round((missing_cells / total_cells) * 100, 2) if total_cells > 0 else 0,
        "duplicate_rows": duplicate_rows,
        "duplicate_percent": round((duplicate_rows / len(df)) * 100, 2) if len(df) > 0 else 0,
    }


def detect_column_types(df: pd.DataFrame) -> dict:
    """Categorize columns into numeric, categorical, datetime, and other."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    datetime_cols = df.select_dtypes(include=["datetime64[ns]"]).columns.tolist()

    categorical_cols = []
    other_cols = []

    for col in df.columns:
        if col in numeric_cols or col in datetime_cols:
            continue

        if df[col].dtype == "object" or str(df[col].dtype) == "category":
            categorical_cols.append(col)
        else:
            other_cols.append(col)

    return {
        "numeric": numeric_cols,
        "categorical": categorical_cols,
        "datetime": datetime_cols,
        "other": other_cols,
    }


def numeric_profile(df: pd.DataFrame) -> pd.DataFrame:
    """Generate profiling stats for numeric columns."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    rows = []
    for col in numeric_cols:
        series = df[col].dropna()

        if len(series) == 0:
            rows.append({
                "column": col,
                "count": 0,
                "missing_percent": round(df[col].isna().mean() * 100, 2),
                "mean": None,
                "median": None,
                "std": None,
                "min": None,
                "max": None,
                "skewness": None,
            })
            continue

        rows.append({
            "column": col,
            "count": int(series.count()),
            "missing_percent": round(df[col].isna().mean() * 100, 2),
            "mean": round(series.mean(), 2),
            "median": round(series.median(), 2),
            "std": round(series.std(), 2) if pd.notna(series.std()) else None,
            "min": round(series.min(), 2),
            "max": round(series.max(), 2),
            "skewness": round(series.skew(), 2) if pd.notna(series.skew()) else None,
        })

    return pd.DataFrame(rows)


def categorical_profile(df: pd.DataFrame) -> pd.DataFrame:
    """Generate profiling stats for categorical columns."""
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns

    rows = []
    for col in categorical_cols:
        series = df[col]
        non_null = series.dropna()

        top_value = None
        top_freq = None
        unique_count = int(non_null.nunique())

        if len(non_null) > 0:
            value_counts = non_null.value_counts(dropna=True)
            top_value = value_counts.index[0]
            top_freq = int(value_counts.iloc[0])

        rows.append({
            "column": col,
            "count": int(non_null.count()),
            "missing_percent": round(series.isna().mean() * 100, 2),
            "unique_values": unique_count,
            "top_value": str(top_value) if top_value is not None else None,
            "top_frequency": top_freq,
        })

    return pd.DataFrame(rows)