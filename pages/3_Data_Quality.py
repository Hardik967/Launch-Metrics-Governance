import plotly.express as px
import streamlit as st

from src.data_loader import load_data
from src.data_quality import (
    calculate_data_quality,
    detect_daily_anomalies,
    get_column_quality,
    get_freshness_status,
    get_quality_checks,
)


st.set_page_config(
    page_title="Data Quality",
    page_icon="🛡️",
    layout="wide",
)

st.title("Data Quality Monitor")
st.caption(
    "Validation controls for duplicates, nulls, "
    "invalid values, timestamps, sessions and anomalies."
)


try:
    df = load_data()
except Exception as error:
    st.error(str(error))
    st.stop()


quality = calculate_data_quality(df)
freshness = get_freshness_status(df)


row1 = st.columns(4)

row1[0].metric(
    "Quality Score",
    f"{quality['quality_score']:.1f}%",
)

row1[1].metric(
    "Duplicate Rows",
    f"{quality['duplicate_rows']:,}",
)

row1[2].metric(
    "Invalid Timestamps",
    f"{quality['invalid_timestamps']:,}",
)

row1[3].metric(
    "Negative Prices",
    f"{quality['invalid_prices']:,}",
)


row2 = st.columns(4)

row2[0].metric(
    "Required-Field Null Rate",
    f"{quality['null_rate']:.2f}%",
)

row2[1].metric(
    "Missing Sessions",
    f"{quality['missing_sessions']:,}",
)

row2[2].metric(
    "Unknown Events",
    f"{quality['unknown_events']:,}",
)

row2[3].metric(
    "Overall Status",
    quality["status"],
)


st.divider()

st.subheader("Automated Quality Controls")

checks = get_quality_checks(df)

st.dataframe(
    checks,
    use_container_width=True,
    hide_index=True,
)


st.subheader("Column-Level Quality Profile")

column_quality = get_column_quality(df)

st.dataframe(
    column_quality,
    use_container_width=True,
    hide_index=True,
)


st.subheader("Freshness & Source Window")

c1, c2, c3 = st.columns(3)

c1.metric(
    "Freshness Status",
    freshness["status"],
)

c2.metric(
    "Source Window",
    (
        f"{freshness['dataset_span_days']:.2f} days"
    ),
)

c3.metric(
    "Latest Event",
    (
        str(freshness["latest_event"])
        if freshness["latest_event"]
        else "Unavailable"
    ),
)

st.info(
    freshness["message"]
)


st.subheader("Suspicious Activity Detection")

anomalies = detect_daily_anomalies(df)

if anomalies.empty:
    st.warning(
        "No valid event dates are available "
        "for anomaly detection."
    )
else:
    fig = px.line(
        anomalies,
        x="Date",
        y="Events",
        markers=True,
        hover_data=[
            "Z Score",
            "Anomaly",
        ],
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    flagged = anomalies[
        anomalies["Anomaly"]
        == "REVIEW"
    ]

    if flagged.empty:
        st.success(
            "No daily event-volume anomalies "
            "crossed the configured threshold."
        )
    else:
        st.warning(
            f"{len(flagged)} day(s) require review."
        )

        st.dataframe(
            flagged,
            use_container_width=True,
            hide_index=True,
        )