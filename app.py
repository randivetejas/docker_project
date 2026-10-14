
import streamlit as st
import pandas as pd
import plotly.express as px
import random
from datetime import datetime, timedelta

# -----------------------------------
# PAGE CONFIGURATION
# -----------------------------------
st.set_page_config(
    page_title="Data Engineering Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------
# CUSTOM CSS
# -----------------------------------
st.markdown("""
<style>
    .stApp {
        background-color: #f4f7fc;
    }

    [data-testid="stSidebar"] {
        background-color: #eaf0ff;
    }

    .main-title {
        font-size: 38px;
        font-weight: 800;
        color: #182848;
        margin-bottom: 5px;
    }

    .sub-title {
        font-size: 16px;
        color: #64748b;
        margin-bottom: 25px;
    }

    [data-testid="stMetric"] {
        background: white;
        padding: 20px;
        border-radius: 14px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
    }

    div.stButton > button {
        background: #2563eb;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 10px 20px;
    }

    div.stButton > button:hover {
        background: #1d4ed8;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------
# SAMPLE DATASET
# -----------------------------------
@st.cache_data
def load_demo_data():
    rng = random.Random(42)

    regions = ["North", "South", "East", "West"]
    categories = ["Electronics", "Fashion", "Grocery", "Furniture"]

    records = []

    for i in range(250):
        records.append({
            "order_id": 1001 + i,
            "order_date": datetime(2026, 1, 1)
            + timedelta(days=rng.randint(0, 180)),
            "region": rng.choice(regions),
            "category": rng.choice(categories),
            "revenue": round(rng.uniform(500, 20000), 2),
            "quantity": rng.randint(1, 15),
            "status": rng.choice(
                ["Completed", "Completed", "Pending", "Cancelled"]
            )
        })

    return pd.DataFrame(records)


# -----------------------------------
# SIDEBAR
# -----------------------------------
with st.sidebar:
    st.title("🚀 DataVision")
    st.caption("Data Engineering Analytics Platform")

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "📊 Overview",
            "🔎 Data Explorer",
            "🛡️ Data Quality",
            "ℹ️ About"
        ]
    )

    st.divider()

    uploaded_file = st.file_uploader(
        "Upload your dataset",
        type=["csv"]
    )

    st.caption("Upload a CSV or explore the sample dataset.")


# -----------------------------------
# LOAD DATA
# -----------------------------------
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.sidebar.success("Dataset uploaded successfully!")
    except Exception as error:
        st.error(f"Unable to read CSV: {error}")
        st.stop()
else:
    df = load_demo_data()

if df.empty:
    st.warning("The dataset is empty.")
    st.stop()

# Detect date columns
for column in df.columns:
    if (
        ("date" in column.lower() or "time" in column.lower())
        and not pd.api.types.is_numeric_dtype(df[column])
    ):
        converted = pd.to_datetime(df[column], errors="coerce")
        if converted.notna().sum() >= 0.7 * df[column].notna().sum():
            df[column] = converted

numeric_columns = df.select_dtypes(include="number").columns.tolist()
date_columns = df.select_dtypes(include="datetime").columns.tolist()
category_columns = df.select_dtypes(
    include=["object", "category", "string"]
).columns.tolist()

# -----------------------------------
# GLOBAL FILTERS
# -----------------------------------
with st.sidebar:
    st.subheader("Filters")

    selected_metric = None

    if numeric_columns:
        preferred = (
            "revenue" if "revenue" in numeric_columns
            else numeric_columns[0]
        )

        selected_metric = st.selectbox(
            "Select metric",
            numeric_columns,
            index=numeric_columns.index(preferred)
        )

    if category_columns:
        filter_column = st.selectbox(
            "Filter by column",
            ["None"] + category_columns
        )

        if filter_column != "None":
            options = sorted(
                df[filter_column].dropna().astype(str).unique().tolist()
            )

            selected_values = st.multiselect(
                "Select values",
                options,
                default=options
            )

            df = df[
                df[filter_column].astype(str).isin(selected_values)
            ]

    st.divider()
    st.caption("Built with Python • Streamlit • Plotly")


# -----------------------------------
# OVERVIEW PAGE
# -----------------------------------
if page == "📊 Overview":

    st.markdown(
        '<div class="main-title">📊 Analytics Dashboard</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-title">'
        'Monitor, explore and understand your data in real time.'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Records", f"{len(df):,}")
    col2.metric("Total Columns", len(df))
    col3.metric("Missing Values", f"{df.isna().sum().sum():,}")
    col4.metric("Duplicate Rows", f"{df.duplicated().sum():,}")

    st.divider()

    if selected_metric is not None:
        metric1, metric2, metric3 = st.columns(3)

        metric1.metric(
            f"Total {selected_metric}",
            f"{df[selected_metric].sum():,.2f}"
        )

        metric2.metric(
            f"Average {selected_metric}",
            f"{df[selected_metric].mean():,.2f}"
        )

        metric3.metric(
            f"Maximum {selected_metric}",
            f"{df[selected_metric].max():,.2f}"
        )

    st.subheader("📈 Interactive Visualizations")

    left, right = st.columns(2)

    with left:
        if category_columns and selected_metric:
            chart_category = st.selectbox(
                "Group data by",
                category_columns
            )

            grouped = (
                df.assign(
                    **{
                        chart_category:
                        df[chart_category].fillna("Missing").astype(str)
                    }
                )
                .groupby(chart_category, as_index=False)[selected_metric]
                .sum()
                .sort_values(selected_metric, ascending=False)
                .head(12)
            )

            fig = px.bar(
                grouped,
                x=chart_category,
                y=selected_metric,
                color=chart_category,
                title=f"{selected_metric} by {chart_category}",
                template="plotly_white"
            )

            fig.update_layout(showlegend=False)

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("Upload categorical and numeric data to view a bar chart.")

    with right:
        if date_columns and selected_metric:
            selected_date = date_columns[0]

            trend = (
                df.dropna(subset=[selected_date])
                .groupby(pd.Grouper(key=selected_date, freq="D"))[
                    selected_metric
                ]
                .sum()
                .reset_index()
            )

            fig2 = px.line(
                trend,
                x=selected_date,
                y=selected_metric,
                title=f"{selected_metric} Trend",
                markers=True,
                template="plotly_white"
            )

            st.plotly_chart(fig2, use_container_width=True)

        elif category_columns:
            counts = (
                df[category_columns[0]]
                .fillna("Missing")
                .value_counts()
                .head(10)
                .reset_index()
            )

            fig2 = px.pie(
                counts,
                names=category_columns[0],
                values="count",
                title="Category Distribution",
                hole=0.55
            )

            st.plotly_chart(fig2, use_container_width=True)

        else:
            st.info("Upload a dataset with dates or categories.")

    st.subheader("📋 Recent Records")

    st.dataframe(
        df.head(15),
        use_container_width=True,
        hide_index=True
    )


# -----------------------------------
# DATA EXPLORER PAGE
# -----------------------------------
elif page == "🔎 Data Explorer":

    st.title("🔎 Data Explorer")
    st.write("Explore, inspect and download your dataset.")

    search = st.text_input(
        "Search all columns",
        placeholder="Type a value to search..."
    )

    display_df = df.copy()

    if search:
        matches = display_df.astype(str).apply(
            lambda column: column.str.contains(
                search,
                case=False,
                na=False,
                regex=False
            )
        )
        display_df = display_df[matches.any(axis=1)]

    st.write(f"Showing {len(display_df):,} records")

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        label="⬇️ Download Filtered CSV",
        data=display_df.to_csv(index=False).encode("utf-8"),
        file_name="filtered_dataset.csv",
        mime="text/csv"
    )

    st.subheader("Column Information")

    column_info = pd.DataFrame({
        "Column": df.columns,
        "Data Type": df.dtypes.astype(str).values,
        "Null Values": df.isna().sum().values,
        "Unique Values": df.nunique().values
    })

    st.dataframe(column_info, use_container_width=True, hide_index=True)


# -----------------------------------
# DATA QUALITY PAGE
# -----------------------------------
elif page == "🛡️ Data Quality":

    st.title("🛡️ Data Quality Monitor")
    st.write("Check missing values, duplicates and dataset completeness.")

    total_cells = df.size
    missing_cells = df.isna().sum().sum()

    completeness = (
        (total_cells - missing_cells) / total_cells * 100
        if total_cells > 0 else 100
    )

    a, b, c = st.columns(3)

    a.metric("Completeness", f"{completeness:.2f}%")
    b.metric("Missing Cells", f"{missing_cells:,}")
    c.metric("Duplicate Rows", f"{df.duplicated().sum():,}")

    st.subheader("Dataset Completeness")
    st.progress(max(0.0, min(completeness / 100, 1.0)))

    null_counts = df.isna().sum().reset_index()
    null_counts.columns = ["Column", "Missing Values"]

    fig = px.bar(
        null_counts,
        x="Column",
        y="Missing Values",
        title="Missing Values by Column",
        template="plotly_white",
        color="Missing Values",
        color_continuous_scale="Blues"
    )

    st.plotly_chart(fig, use_container_width=True)

    if missing_cells == 0:
        st.success("No missing values detected!")
    else:
        st.warning("Some columns contain missing values.")

    st.subheader("Dataset Statistics")
    st.dataframe(
        df.describe(include="all").astype(str),
        use_container_width=True
    )


# -----------------------------------
# ABOUT PAGE
# -----------------------------------
elif page == "ℹ️ About":

    st.title("🚀 DataVision Analytics")

    st.markdown("""
    ### Professional Data Analytics Dashboard

    Built using:

    - **Python** — Application programming
    - **Streamlit** — Interactive web interface
    - **Pandas** — Data processing
    - **Plotly** — Interactive visualizations

    ### Features

    - Upload CSV datasets
    - Explore and search records
    - Filter data interactively
    - Analyze numeric metrics
    - Visualize trends and categories
    - Identify missing and duplicate records
    - Download filtered results

    **Designed for data analytics and data engineering projects.**
    """)

# -----------------------------------
# FOOTER
# -----------------------------------
st.divider()
st.caption("© 2026 DataVision | Powered by Streamlit")
