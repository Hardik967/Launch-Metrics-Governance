import streamlit as st

from src.data_loader import load_data
from src.governance import (
    get_metric_dictionary,
)
from src.metrics import calculate_kpis


st.set_page_config(
    page_title="KPI Governance",
    page_icon="📋",
    layout="wide",
)

st.title("KPI Governance")
st.caption(
    "Every governed KPI has an explicit definition, "
    "formula, source, owner, guardrail and decision."
)


try:
    df = load_data()
except Exception as error:
    st.error(str(error))
    st.stop()


dictionary = get_metric_dictionary()
kpis = calculate_kpis(df)


st.subheader("Governance Coverage")

c1, c2, c3 = st.columns(3)

c1.metric(
    "Metrics Defined",
    len(dictionary),
)

c2.metric(
    "Metrics Governed",
    int(
        (
            dictionary["Status"]
            == "GOVERNED"
        ).sum()
    ),
)

coverage = (
    (
        dictionary["Status"]
        == "GOVERNED"
    ).mean()
    * 100
)

c3.metric(
    "Governance Coverage",
    f"{coverage:.1f}%",
)


st.divider()

st.subheader("Metric Dictionary")

search = st.text_input(
    "Search metrics",
    placeholder=(
        "Search by metric, source, owner or decision..."
    ),
)

filtered = dictionary.copy()

if search:
    mask = (
        filtered
        .astype(str)
        .apply(
            lambda row: row.str.contains(
                search,
                case=False,
                na=False,
            ).any(),
            axis=1,
        )
    )

    filtered = filtered[mask]


st.dataframe(
    filtered,
    use_container_width=True,
    hide_index=True,
)


csv_data = dictionary.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "Download Metric Dictionary",
    data=csv_data,
    file_name="metric_dictionary.csv",
    mime="text/csv",
)


st.divider()

st.subheader("Live Governed KPI Values")

live_values = {
    "Total Events": (
        f"{kpis['total_events']:,}"
    ),
    "Unique Users": (
        f"{kpis['total_users']:,}"
    ),
    "Unique Sessions": (
        f"{kpis['total_sessions']:,}"
    ),
    "View Events": (
        f"{kpis['views']:,}"
    ),
    "Cart Events": (
        f"{kpis['carts']:,}"
    ),
    "Purchase Events": (
        f"{kpis['purchases']:,}"
    ),
    "Cart Rate": (
        f"{kpis['cart_rate']:.2f}%"
    ),
    "Purchase Rate": (
        f"{kpis['purchase_rate']:.2f}%"
    ),
    "Cart-to-Purchase Rate": (
        f"{kpis['cart_to_purchase_rate']:.2f}%"
    ),
}

for metric, value in live_values.items():
    with st.expander(metric):
        definition = dictionary[
            dictionary["Metric"] == metric
        ]

        st.metric(
            "Current Value",
            value,
        )

        if not definition.empty:
            row = definition.iloc[0]

            st.write(
                "**Definition:**",
                row["Definition"],
            )

            st.write(
                "**Formula:**",
                row["Formula"],
            )

            st.write(
                "**Source:**",
                row["Source"],
            )

            st.write(
                "**Decision:**",
                row["Decision"],
            )