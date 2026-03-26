import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.profiler import (
    get_basic_overview,
    detect_column_types,
    numeric_profile,
    categorical_profile,
)
from src.insight_engine import (
    generate_column_insights,
    generate_dataset_level_insights,
)
from src.narrator import generate_narrative_summary


# ---------------------------------------------------------
# Page Config
# ---------------------------------------------------------
st.set_page_config(
    page_title="Auto EDA Insight Generator",
    page_icon="📊",
    layout="wide",
)


# ---------------------------------------------------------
# Custom Styling
# ---------------------------------------------------------
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }

        .main-title {
            font-size: 2.6rem;
            font-weight: 700;
            margin-bottom: 0.3rem;
        }

        .subtitle {
            font-size: 1.05rem;
            color: #b0b7c3;
            margin-bottom: 1.5rem;
        }

        .section-title {
            font-size: 1.6rem;
            font-weight: 650;
            margin-top: 0.5rem;
            margin-bottom: 1rem;
        }

        .soft-card {
            padding: 1rem 1.1rem;
            border-radius: 16px;
            background: rgba(49, 51, 63, 0.55);
            border: 1px solid rgba(255,255,255,0.06);
            margin-bottom: 1rem;
        }

        .mini-label {
            font-size: 0.95rem;
            color: #9aa4b2;
            margin-bottom: 0.25rem;
        }

        .mini-value {
            font-size: 1.8rem;
            font-weight: 700;
        }

        .nav-hint {
            font-size: 0.92rem;
            color: #9aa4b2;
            margin-top: -0.3rem;
            margin-bottom: 1rem;
        }

        div[data-testid="stRadio"] > label {
            font-weight: 600;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
@st.cache_data
def load_data(file) -> pd.DataFrame:
    return pd.read_csv(file, low_memory=False)


def calculate_data_quality_score(overview: dict, total_insights: int) -> float:
    score = 100.0
    score -= overview["missing_percent"] * 0.5
    score -= overview["duplicate_percent"] * 0.5
    score -= min(total_insights, 20) * 1.0
    return max(0.0, round(score, 2))


def build_text_report(
    overview: dict,
    col_types: dict,
    quality_score: float,
    all_insights: list[str],
    summary: str
) -> str:
    lines = [
        "AUTO EDA INSIGHT GENERATOR REPORT",
        "=" * 60,
        "",
        "DATASET OVERVIEW",
        f"Rows: {overview['rows']}",
        f"Columns: {overview['columns']}",
        f"Missing Cells: {overview['missing_cells']}",
        f"Missing Percentage: {overview['missing_percent']}%",
        f"Duplicate Rows: {overview['duplicate_rows']}",
        f"Duplicate Percentage: {overview['duplicate_percent']}%",
        "",
        "COLUMN TYPE SUMMARY",
        f"Numeric Columns: {len(col_types['numeric'])}",
        f"Categorical Columns: {len(col_types['categorical'])}",
        f"Datetime Columns: {len(col_types['datetime'])}",
        f"Other Columns: {len(col_types['other'])}",
        "",
        "DATA QUALITY SCORE",
        f"{quality_score} / 100",
        "",
        "TOP 5 KEY INSIGHTS",
    ]

    if all_insights:
        for idx, insight in enumerate(all_insights[:5], start=1):
            lines.append(f"{idx}. {insight}")
    else:
        lines.append("No major issues detected.")

    lines.extend(["", "ALL GENERATED INSIGHTS"])

    if all_insights:
        for idx, insight in enumerate(all_insights, start=1):
            lines.append(f"{idx}. {insight}")
    else:
        lines.append("No major issues detected.")

    lines.extend(["", "PLAIN-ENGLISH NARRATIVE SUMMARY", summary])

    return "\n".join(lines)


def render_quality_score(score: float) -> None:
    st.markdown('<div class="section-title">Data Quality Score</div>', unsafe_allow_html=True)

    if score >= 80:
        st.success(f"{score} / 100 — Good Quality")
    elif score >= 50:
        st.warning(f"{score} / 100 — Moderate Quality")
    else:
        st.error(f"{score} / 100 — Poor Quality")


def render_kpi_card(label: str, value: str):
    st.markdown(
        f"""
        <div class="soft-card">
            <div class="mini-label">{label}</div>
            <div class="mini-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------
st.markdown('<div class="main-title">📊 Auto EDA Insight Generator</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Upload a CSV file to automatically profile the dataset, detect data quality issues, surface statistical patterns, and generate a plain-English narrative summary.</div>',
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is None:
    st.info("Please upload a CSV file to begin.")
    st.stop()

# ---------------------------------------------------------
# Data Load
# ---------------------------------------------------------
try:
    df = load_data(uploaded_file)
    overview = get_basic_overview(df)
    col_types = detect_column_types(df)

    dataset_insights = generate_dataset_level_insights(df)
    column_insights = generate_column_insights(df)
    all_insights = dataset_insights + column_insights

    quality_score = calculate_data_quality_score(overview, len(all_insights))
    summary = generate_narrative_summary(overview, all_insights)

except Exception as e:
    st.error(f"Error while processing file: {e}")
    st.stop()

st.success("File uploaded successfully.")

# ---------------------------------------------------------
# Sidebar Navigation
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("## Navigation")
    st.markdown('<div class="nav-hint">Choose one section to view at a time.</div>', unsafe_allow_html=True)

    page = st.radio(
        "Go to",
        [
            "Overview",
            "Preview",
            "Missing Values",
            "Numeric Analysis",
            "Categorical Analysis",
            "Correlation Heatmap",
            "Insights",
            "Summary & Report",
        ],
        label_visibility="collapsed",
    )

# ---------------------------------------------------------
# Page: Overview
# ---------------------------------------------------------
if page == "Overview":
    st.markdown('<div class="section-title">Dataset Overview</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Rows", f"{overview['rows']}")
    with c2:
        render_kpi_card("Columns", f"{overview['columns']}")
    with c3:
        render_kpi_card("Missing Cells", f"{overview['missing_cells']}")
    with c4:
        render_kpi_card("Duplicate Rows", f"{overview['duplicate_rows']}")

    c5, c6, c7 = st.columns(3)
    with c5:
        render_kpi_card("Missing %", f"{overview['missing_percent']}%")
    with c6:
        render_kpi_card("Duplicate %", f"{overview['duplicate_percent']}%")
    with c7:
        render_kpi_card("Data Quality Score", f"{quality_score} / 100")

    st.markdown('<div class="section-title">Column Type Summary</div>', unsafe_allow_html=True)

    t1, t2, t3, t4 = st.columns(4)
    with t1:
        render_kpi_card("Numeric Columns", f"{len(col_types['numeric'])}")
    with t2:
        render_kpi_card("Categorical Columns", f"{len(col_types['categorical'])}")
    with t3:
        render_kpi_card("Datetime Columns", f"{len(col_types['datetime'])}")
    with t4:
        render_kpi_card("Other Columns", f"{len(col_types['other'])}")

    render_quality_score(quality_score)

# ---------------------------------------------------------
# Page: Preview
# ---------------------------------------------------------
elif page == "Preview":
    st.markdown('<div class="section-title">Dataset Preview</div>', unsafe_allow_html=True)

    preview_rows = st.slider("Number of rows to preview", min_value=5, max_value=50, value=10, step=5)
    st.dataframe(df.head(preview_rows), use_container_width=True)

    st.markdown("### Sample Shape")
    st.write(f"This preview is showing the first **{preview_rows} rows** out of **{len(df)} total rows**.")

# ---------------------------------------------------------
# Page: Missing Values
# ---------------------------------------------------------
elif page == "Missing Values":
    st.markdown('<div class="section-title">Missing Values Analysis</div>', unsafe_allow_html=True)

    missing_df = df.isna().mean().reset_index()
    missing_df.columns = ["column", "missing_rate"]
    missing_df = missing_df[missing_df["missing_rate"] > 0].sort_values(
        by="missing_rate", ascending=False
    )

    if not missing_df.empty:
        fig_missing = px.bar(
            missing_df,
            x="column",
            y="missing_rate",
            title="Missing Value Rate by Column",
            labels={"column": "Column", "missing_rate": "Missing Rate"},
        )
        fig_missing.update_layout(xaxis_tickangle=-45, height=500)
        st.plotly_chart(fig_missing, use_container_width=True)

        st.markdown("### Missing Value Table")
        st.dataframe(missing_df, use_container_width=True)
    else:
        st.success("No missing values found in the dataset.")

# ---------------------------------------------------------
# Page: Numeric Analysis
# ---------------------------------------------------------
elif page == "Numeric Analysis":
    st.markdown('<div class="section-title">Numeric Analysis</div>', unsafe_allow_html=True)

    num_profile = numeric_profile(df)
    numeric_cols = col_types["numeric"]

    if numeric_cols:
        selected_num_col = st.selectbox("Select a numeric column", options=numeric_cols)

        v1, v2 = st.columns(2)

        with v1:
            fig_hist = px.histogram(
                df,
                x=selected_num_col,
                title=f"{selected_num_col} Distribution",
            )
            st.plotly_chart(fig_hist, use_container_width=True)

        with v2:
            fig_box = px.box(
                df,
                y=selected_num_col,
                title=f"{selected_num_col} Boxplot",
            )
            st.plotly_chart(fig_box, use_container_width=True)

        st.markdown("### Statistical Summary of Numeric Features")
        if not num_profile.empty:
            st.dataframe(num_profile, use_container_width=True)
        else:
            st.info("No numeric profile available.")
    else:
        st.info("No numeric columns found in the dataset.")

# ---------------------------------------------------------
# Page: Categorical Analysis
# ---------------------------------------------------------
elif page == "Categorical Analysis":
    st.markdown('<div class="section-title">Categorical Analysis</div>', unsafe_allow_html=True)

    cat_profile = categorical_profile(df)
    categorical_cols = col_types["categorical"]

    if categorical_cols:
        selected_cat_col = st.selectbox("Select a categorical column", options=categorical_cols)

        top_n = st.slider("Top categories to display", min_value=5, max_value=20, value=10, step=1)

        top_values = (
            df[selected_cat_col]
            .fillna("Missing")
            .astype(str)
            .value_counts()
            .head(top_n)
            .reset_index()
        )
        top_values.columns = [selected_cat_col, "count"]

        fig_bar = px.bar(
            top_values,
            x=selected_cat_col,
            y="count",
            title=f"Top Categories in {selected_cat_col}",
        )
        fig_bar.update_layout(xaxis_tickangle=-45, height=500)
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("### Summary of Categorical Features")
        if not cat_profile.empty:
            st.dataframe(cat_profile, use_container_width=True)
        else:
            st.info("No categorical profile available.")
    else:
        st.info("No categorical columns found in the dataset.")

# ---------------------------------------------------------
# Page: Correlation Heatmap
# ---------------------------------------------------------
elif page == "Correlation Heatmap":
    st.markdown('<div class="section-title">Correlation Heatmap</div>', unsafe_allow_html=True)

    numeric_cols = col_types["numeric"]
    numeric_df = df[numeric_cols] if numeric_cols else pd.DataFrame()

    if not numeric_df.empty and numeric_df.shape[1] >= 2:
        corr_matrix = numeric_df.corr(numeric_only=True)

        fig_heatmap = go.Figure(
            data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.index,
                text=corr_matrix.round(2).values,
                texttemplate="%{text}",
                hoverongaps=False,
                colorscale="Blues",
                colorbar=dict(title="Correlation"),
            )
        )

        fig_heatmap.update_layout(
            title="Correlation Heatmap",
            xaxis_title="Columns",
            yaxis_title="Columns",
            height=700,
        )

        st.plotly_chart(fig_heatmap, use_container_width=True)
    else:
        st.info("At least two numeric columns are required to generate a correlation heatmap.")

# ---------------------------------------------------------
# Page: Insights
# ---------------------------------------------------------
elif page == "Insights":
    st.markdown('<div class="section-title">Automated Data Quality & Pattern Insights</div>', unsafe_allow_html=True)

    i1, i2, i3 = st.columns(3)
    with i1:
        render_kpi_card("Total Insights", f"{len(all_insights)}")
    with i2:
        render_kpi_card("Highlighted Insights", f"{min(len(all_insights), 5)}")
    with i3:
        render_kpi_card("Quality Score", f"{quality_score} / 100")

    st.markdown("### Top 5 Key Insights")
    if all_insights:
        for insight in all_insights[:5]:
            st.error(insight)
    else:
        st.success("No major issues detected by the current rule-based insight engine.")

    st.markdown("### All Insights")
    if all_insights:
        for idx, insight in enumerate(all_insights, start=1):
            st.write(f"{idx}. {insight}")
    else:
        st.success("No major issues detected by the current rule-based insight engine.")

# ---------------------------------------------------------
# Page: Summary & Report
# ---------------------------------------------------------
elif page == "Summary & Report":
    st.markdown('<div class="section-title">Narrative Summary & Report</div>', unsafe_allow_html=True)

    st.info(summary)

    report_text = build_text_report(
        overview=overview,
        col_types=col_types,
        quality_score=quality_score,
        all_insights=all_insights,
        summary=summary,
    )

    st.markdown("### Download Report")
    st.download_button(
        label="Download Report as TXT",
        data=report_text,
        file_name="eda_report.txt",
        mime="text/plain",
    )