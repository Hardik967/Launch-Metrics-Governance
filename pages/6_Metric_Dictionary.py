import streamlit as st

from src.governance import (
    get_metric_dictionary,
)


st.set_page_config(
    page_title="Metric Dictionary",
    page_icon="📚",
    layout="wide",
)

st.title("Governed Metric Dictionary")
st.caption(
    "The single reference point for metric "
    "definitions, formulas, sources, owners "
    "and decisions."
)


dictionary = get_metric_dictionary()


owners = sorted(
    dictionary["Owner"]
    .dropna()
    .unique()
    .tolist()
)

selected_owners = st.multiselect(
    "Filter by owner",
    options=owners,
    default=owners,
)


filtered = dictionary[
    dictionary["Owner"]
    .isin(selected_owners)
]


st.dataframe(
    filtered,
    use_container_width=True,
    hide_index=True,
)


st.download_button(
    "Export Full Metric Dictionary",
    data=dictionary.to_csv(
        index=False
    ).encode("utf-8"),
    file_name="metric_dictionary.csv",
    mime="text/csv",
)


st.divider()

st.subheader("Metric Detail")

metric_name = st.selectbox(
    "Select a metric",
    dictionary["Metric"].tolist(),
)

metric = dictionary[
    dictionary["Metric"]
    == metric_name
].iloc[0]


c1, c2 = st.columns(2)

with c1:
    st.write(
        "**Definition**"
    )
    st.write(
        metric["Definition"]
    )

    st.write(
        "**Formula**"
    )
    st.code(
        metric["Formula"],
        language=None,
    )

    st.write(
        "**Source**"
    )
    st.write(
        metric["Source"]
    )

with c2:
    st.write(
        "**Owner**"
    )
    st.write(
        metric["Owner"]
    )

    st.write(
        "**Guardrail**"
    )
    st.write(
        metric["Guardrail"]
    )

    st.write(
        "**Decision Triggered**"
    )
    st.write(
        metric["Decision"]
    )

    st.write(
        "**Governance Status**"
    )
    st.write(
        metric["Status"]
    )