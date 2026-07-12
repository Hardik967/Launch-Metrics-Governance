import streamlit as st

from src.data_loader import load_data
from src.governance import (
    get_event_lineage,
)
from src.metrics import (
    get_event_distribution,
)


st.set_page_config(
    page_title="Event Traceability",
    page_icon="🔗",
    layout="wide",
)

st.title("Event & Source Traceability")
st.caption(
    "Trace every decision-grade KPI back to "
    "the event and source field that created it."
)


try:
    df = load_data()
except Exception as error:
    st.error(str(error))
    st.stop()


lineage = get_event_lineage()


st.subheader("Governed Measurement Chain")

st.markdown(
    """
    ### Raw Event → Source Field → Metric → KPI → Decision

    A metric is considered governed only when its source,
    calculation and decision use are explicitly documented.
    """
)


st.dataframe(
    lineage,
    use_container_width=True,
    hide_index=True,
)


st.divider()

st.subheader("Live Source Event Evidence")

distribution = get_event_distribution(df)

st.dataframe(
    distribution,
    use_container_width=True,
    hide_index=True,
)


selected_event = st.selectbox(
    "Inspect raw source records",
    options=sorted(
        df["event_type"]
        .dropna()
        .unique()
        .tolist()
    ),
)


sample = (
    df[
        df["event_type"]
        == selected_event
    ][
        [
            "event_time",
            "event_type",
            "product_id",
            "category_code",
            "brand",
            "price",
            "user_id",
            "user_session",
        ]
    ]
    .head(100)
)


st.dataframe(
    sample,
    use_container_width=True,
    hide_index=True,
)


st.download_button(
    "Download Source Evidence",
    data=sample.to_csv(
        index=False
    ).encode("utf-8"),
    file_name=(
        f"{selected_event}_source_evidence.csv"
    ),
    mime="text/csv",
)