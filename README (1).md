# Auto EDA Insight Generator

Upload any CSV file and get an automatic data quality analysis — missing value charts, outlier detection, skewness flags, correlation heatmaps, categorical profiling, a numeric statistical summary, a computed quality score, and a plain-English narrative summary — all without writing a single line of analysis code.

---

## Why This Project Exists

Exploratory Data Analysis is the most repeated task in any data workflow. Every new dataset means the same questions: How many nulls? Any duplicates? What's skewed? What correlates? What looks suspicious?

This tool answers all of them automatically. The rule-based insight engine decides what's worth surfacing — not everything, just the things that actually matter — and the narrator translates those findings into a paragraph a non-technical stakeholder can read.

**The insight engine is the core. The UI is just how you use it.**

---

## App Pages

| Page | What It Shows |
|------|---------------|
| Overview | Row/column count, missing %, duplicate %, data quality score, column type breakdown |
| Preview | Scrollable data preview with adjustable row count |
| Missing Values | Bar chart of missing rate per column + sortable table |
| Numeric Analysis | Histogram + boxplot for any selected numeric column, full statistical summary |
| Categorical Analysis | Top-N bar chart for any selected categorical column, full category profile |
| Correlation Heatmap | Interactive Plotly heatmap of all numeric column correlations |
| Insights | Automated rule-based findings ranked by importance + quality score |
| Summary & Report | Plain-English narrative summary + downloadable TXT report |

---

## Run It

```bash
git clone https://github.com/yourusername/auto-eda-insight-generator.git
cd auto-eda-insight-generator

pip install pandas numpy streamlit plotly

streamlit run app.py
```

Upload any CSV file — the full analysis runs automatically.

---

## Project Structure

```
auto-eda-insight-generator/
│
├── src/
│   ├── profiler.py          # Dataset overview, column type detection, numeric + categorical profiling
│   ├── insight_engine.py    # Rule-based insight detection (nulls, skewness, outliers, correlations)
│   └── narrator.py          # Converts structured findings into plain-English summary
│
└── app.py                   # Streamlit UI — 8-page navigation, Plotly charts, downloadable report
```

---

## How the Insight Engine Works

The insight engine runs statistical rules column by column and flags only what crosses meaningful thresholds. It does not surface noise.

**Missing value rules:**
- `> 5%` null rate → flagged as worth investigating
- `> 20%` null rate → flagged as high risk

**Numeric rules:**
- Skewness `> 2` or `< -2` → flagged as strongly skewed, log transform suggested
- `> 40%` values divisible by 10 → flagged as possible rounding artifact
- `> 50%` zeros → flagged as zero-heavy distribution
- `> 10%` IQR outliers → flagged with outlier percentage
- Only 1 unique non-null value → flagged as potentially useless for modeling

**Categorical rules:**
- `> 50` unique values → flagged as high cardinality, grouping suggested
- Top category covers `> 80%` of values → flagged as dominant category
- Case/spacing inconsistency detected → flagged for standardization

**Dataset-level rules:**
- Any duplicate rows → flagged with percentage
- Any numeric column pair with correlation `≥ 0.80` → flagged as potentially redundant

```python
from src.insight_engine import generate_column_insights, generate_dataset_level_insights

column_insights = generate_column_insights(df)
dataset_insights = generate_dataset_level_insights(df)
```

---

## Data Quality Score

A single numeric score (0–100) computed from missing data, duplicates, and total insight count:

```python
def calculate_data_quality_score(overview, total_insights):
    score = 100.0
    score -= overview["missing_percent"] * 0.5
    score -= overview["duplicate_percent"] * 0.5
    score -= min(total_insights, 20) * 1.0
    return max(0.0, round(score, 2))
```

| Score | Rating |
|-------|--------|
| 80–100 | Good Quality |
| 50–79 | Moderate Quality |
| 0–49 | Poor Quality |

---

## Narrative Summary Output (Example)

```
This dataset contains 50000 rows and 44 columns. Overall missing data is fairly
high at 18.4%, so data quality should be reviewed before deeper analysis.
The most important findings include: 'closed_date' has 18.4% missing values
and is worth investigating upstream. 'latitude' and 'longitude' show a strong
correlation of 0.94, which may indicate redundancy or a meaningful relationship.
```

This is what a data analyst would write after spending 20 minutes with a dataset. This tool produces it in under 3 seconds.

---

## Downloadable Report

Every analysis exports as a structured `.txt` report containing the full dataset overview, column type summary, quality score, all generated insights, and the narrative summary — ready to share or attach to documentation.

---

## Tech Stack

- **Python 3.13**
- **pandas** — data profiling and manipulation
- **numpy** — statistical computations
- **Plotly** — interactive charts (histogram, boxplot, heatmap, bar charts)
- **Streamlit** — multi-page UI with sidebar navigation, caching, and file upload

---

## Key Design Decisions

**Why rule-based instead of ML-based?** Rules are explainable. When the tool says "this column is strongly right-skewed," you can verify it yourself. A black-box model flagging columns without reasoning is not useful in a data quality context.

**Why separate profiler, insight engine, and narrator into three modules?** Each does one job. The profiler computes stats. The insight engine decides what's interesting. The narrator writes the prose. This separation means you can use `insight_engine.py` standalone without the UI, or swap the narrator for a different output format without touching anything else.

**Why IQR for outlier detection instead of Z-score?** IQR is robust to non-normal distributions — it does not assume your data is Gaussian. Most real-world datasets are not.

**Why correlation threshold `≥ 0.80`?** Below 0.8, correlations are common and expected. Above 0.8, two columns are saying roughly the same thing — which matters for feature selection and multicollinearity in regression models.

---

## Author

Built as a portfolio project demonstrating modular Python design, statistical reasoning, and data engineering fundamentals. Works on any CSV file — not just one specific dataset.
