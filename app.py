from pathlib import Path

import streamlit as st

from src.data_loader import (
    get_dataset_metadata,
    load_data,
)
from src.data_quality import (
    calculate_data_quality,
)
from src.metrics import calculate_kpis
from src.readiness import (
    calculate_launch_readiness,
)


BASE_DIR = Path(__file__).resolve().parent


st.set_page_config(
    page_title="Launch Metrics Governance",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_css():
    css_file = (
        BASE_DIR
        / "assets"
        / "style.css"
    )

    if css_file.exists():
        st.markdown(
            f"<style>{css_file.read_text()}</style>",
            unsafe_allow_html=True,
        )


load_css()


st.title("Launch Metrics Governance")
st.caption(
    "Decision-grade KPI governance, source traceability, "
    "data-quality monitoring and launch readiness."
)


with st.sidebar:
    st.header("Data Controls")

    row_limit = st.selectbox(
        "Rows to load",
        options=[
            100_000,
            250_000,
            500_000,
            1_000_000,
        ],
        index=2,
        format_func=lambda x: f"{x:,}",
    )

    st.caption(
        "The dashboard loads a controlled number of "
        "real event records for responsive analysis."
    )


try:
    df = load_data(row_limit)

except FileNotFoundError as error:
    st.error(str(error))
    st.info(
        "Add `2019-Oct.csv` inside the `data` folder."
    )
    st.stop()

except ValueError as error:
    st.error(str(error))
    st.stop()

except Exception as error:
    st.error(
        "The dataset could not be loaded safely."
    )
    st.exception(error)
    st.stop()


kpis = calculate_kpis(df)
quality = calculate_data_quality(df)
readiness = calculate_launch_readiness(df)
metadata = get_dataset_metadata(df)


st.subheader("Launch Control Summary")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Events Governed",
    f"{kpis['total_events']:,}",
)

col2.metric(
    "Unique Users",
    f"{kpis['total_users']:,}",
)

col3.metric(
    "Data Quality",
    f"{quality['quality_score']:.1f}%",
)

col4.metric(
    "Launch Decision",
    readiness["recommendation"],
)


st.divider()

left, right = st.columns([1.4, 1])

with left:
    st.subheader("What this dashboard governs")

    st.markdown(
        """
        This control center connects **raw events to metrics,
        metrics to KPIs, and KPIs to launch decisions**.

        The governed measurement flow is:

        **Raw event → validated source field → defined metric
        → launch KPI → decision/action**

        Use the pages in the sidebar to inspect KPI definitions,
        source lineage, data quality, anomalies and final
        launch readiness.
        """
    )

with right:
    st.subheader("Source Evidence")

    st.write(
        f"**Dataset:** `{metadata['file_name']}`"
    )

    st.write(
        f"**Rows loaded:** "
        f"{metadata['rows_loaded']:,}"
    )

    st.write(
        f"**File size:** "
        f"{metadata['file_size_mb']:,} MB"
    )

    st.write(
        f"**Earliest event:** "
        f"{metadata['earliest_event']}"
    )

    st.write(
        f"**Latest event:** "
        f"{metadata['latest_event']}"
    )


st.divider()

st.subheader("Governance Status")

c1, c2, c3 = st.columns(3)

c1.metric(
    "Controls Passed",
    readiness["pass_count"],
)

c2.metric(
    "Controls Warning",
    readiness["warning_count"],
)

c3.metric(
    "Controls Failed",
    readiness["fail_count"],
)

st.dataframe(
    readiness["checks"],
    use_container_width=True,
    hide_index=True,
)