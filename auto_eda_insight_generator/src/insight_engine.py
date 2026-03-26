import pandas as pd
import numpy as np


def detect_outliers_iqr(series: pd.Series) -> float:
    """Return percentage of outliers using IQR method."""
    clean = series.dropna()
    if len(clean) < 5:
        return 0.0

    q1 = clean.quantile(0.25)
    q3 = clean.quantile(0.75)
    iqr = q3 - q1

    if iqr == 0:
        return 0.0

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    outlier_mask = (clean < lower) | (clean > upper)
    return round(outlier_mask.mean() * 100, 2)


def generate_column_insights(df: pd.DataFrame) -> list[str]:
    """Generate rule-based insights column by column."""
    insights = []

    for col in df.columns:
        series = df[col]
        null_rate = series.isna().mean()

        # Missing values
        if null_rate > 0.20:
            insights.append(
                f"'{col}' has a very high missing rate of {null_rate:.1%}, which could significantly affect analysis quality."
            )
        elif null_rate > 0.05:
            insights.append(
                f"'{col}' has {null_rate:.1%} missing values and is worth investigating upstream."
            )

        # Numeric insights
        if pd.api.types.is_numeric_dtype(series):
            clean = series.dropna()

            if len(clean) < 5:
                continue

            skew = clean.skew()
            if pd.notna(skew) and abs(skew) > 2:
                direction = "right" if skew > 0 else "left"
                insights.append(
                    f"'{col}' is strongly {direction}-skewed (skewness = {skew:.2f}), suggesting extreme values on one side."
                )

            # Rounded values pattern
            round_rate = ((clean % 10) == 0).mean() if len(clean) > 0 else 0
            if round_rate > 0.40 and len(clean) > 100:
                insights.append(
                    f"'{col}' has {round_rate:.0%} values divisible by 10, which may indicate rounding or data-entry artifacts."
                )

            # Zero-heavy columns
            zero_rate = (clean == 0).mean()
            if zero_rate > 0.50:
                insights.append(
                    f"'{col}' contains {zero_rate:.0%} zeros, which suggests a zero-heavy distribution."
                )

            # Low variance / constant-ish
            if clean.nunique() <= 1:
                insights.append(
                    f"'{col}' has only one unique non-null value, so it may not be useful for analysis."
                )

            # Outliers
            outlier_percent = detect_outliers_iqr(clean)
            if outlier_percent > 10:
                insights.append(
                    f"'{col}' has {outlier_percent:.1f}% potential outliers based on the IQR method."
                )

        # Categorical insights
        elif series.dtype == "object" or str(series.dtype) == "category":
            clean = series.dropna()

            if len(clean) == 0:
                continue

            unique_count = clean.nunique()
            top_share = clean.value_counts(normalize=True).iloc[0]

            if unique_count > 50:
                insights.append(
                    f"'{col}' has high cardinality with {unique_count} unique values, which may need grouping before modeling."
                )

            if top_share > 0.80:
                insights.append(
                    f"'{col}' is dominated by a single category covering {top_share:.1%} of non-null values."
                )

            # Case inconsistency check
            lowered = clean.astype(str).str.lower().str.strip()
            if lowered.nunique() < clean.nunique():
                insights.append(
                    f"'{col}' may contain inconsistent text labels (for example, differences in casing or spacing)."
                )

    return insights


def generate_dataset_level_insights(df: pd.DataFrame) -> list[str]:
    """Generate whole-dataset insights."""
    insights = []

    duplicate_rate = df.duplicated().mean()
    if duplicate_rate > 0:
        insights.append(
            f"The dataset contains {duplicate_rate:.1%} duplicate rows, which may need removal before analysis."
        )

    numeric_df = df.select_dtypes(include=[np.number])

    if numeric_df.shape[1] >= 2:
        corr_matrix = numeric_df.corr(numeric_only=True)
        strong_pairs = []

        for i, col1 in enumerate(corr_matrix.columns):
            for col2 in corr_matrix.columns[i + 1:]:
                corr_val = corr_matrix.loc[col1, col2]
                if pd.notna(corr_val) and abs(corr_val) >= 0.80:
                    strong_pairs.append((col1, col2, corr_val))

        for col1, col2, corr_val in strong_pairs[:5]:
            insights.append(
                f"'{col1}' and '{col2}' show a strong correlation of {corr_val:.2f}, which may indicate redundancy or a meaningful relationship."
            )

    return insights