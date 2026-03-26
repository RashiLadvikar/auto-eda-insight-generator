def generate_narrative_summary(overview: dict, insights: list[str]) -> str:
    """Generate a short plain-English summary."""
    rows = overview["rows"]
    cols = overview["columns"]
    missing_percent = overview["missing_percent"]
    duplicate_percent = overview["duplicate_percent"]

    summary_parts = [
        f"This dataset contains {rows} rows and {cols} columns."
    ]

    if missing_percent > 10:
        summary_parts.append(
            f"Overall missing data is fairly high at {missing_percent}%, so data quality should be reviewed before deeper analysis."
        )
    elif missing_percent > 0:
        summary_parts.append(
            f"The dataset has {missing_percent}% missing cells, but the issue appears manageable depending on the affected columns."
        )
    else:
        summary_parts.append("No missing data was detected at the dataset level.")

    if duplicate_percent > 0:
        summary_parts.append(
            f"There are also {duplicate_percent}% duplicate rows present."
        )

    if insights:
        summary_parts.append(
            "The most important findings include: " + " ".join(insights[:3])
        )
    else:
        summary_parts.append(
            "No major red flags were detected by the current rule-based checks."
        )

    return " ".join(summary_parts)