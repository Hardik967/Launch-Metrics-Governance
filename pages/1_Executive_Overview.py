import plotly.express as px
import streamlit as st

from src.data_loader import load_data
from src.metrics import (
    calculate_kpis,
    get_daily_activity,
    get_event_distribution,
    get_funnel_data,
    get_top_categories,
)


st.set_page_config(
    page_title="Executive Overview",
    page_icon="📈",
    layout="wide",
)

st.title("Executive Launch Overview")
st.caption(
    "A decision-focused view of product activity, "
    "conversion and measurement health."
)


with st.sidebar:
    st.header("Analysis Controls")

    row_limit = st.selectbox(
        "Rows to analyze",
        [
            100_000,
            250_000,
            500_000,
            1_000_000,
        ],
        index=2,
        format_func=lambda x: f"{x:,}",
    )


try:
    df = load_data(row_limit)
except Exception as error:
    st.error(str(error))
    st.stop()


kpis = calculate_kpis(df)


row1 = st.columns(4)

row1[0].metric(
    "Total Events",
    f"{kpis['total_events']:,}",
)

row1[1].metric(
    "Unique Users",
    f"{kpis['total_users']:,}",
)

row1[2].metric(
    "Unique Sessions",
    f"{kpis['total_sessions']:,}",
)

row1[3].metric(
    "Purchase Events",
    f"{kpis['purchases']:,}",
)


row2 = st.columns(4)

row2[0].metric(
    "Cart Rate",
    f"{kpis['cart_rate']:.2f}%",
)

row2[1].metric(
    "Purchase Rate",
    f"{kpis['purchase_rate']:.2f}%",
)

row2[2].metric(
    "Cart → Purchase",
    f"{kpis['cart_to_purchase_rate']:.2f}%",
)

row2[3].metric(
    "Purchasing Users",
    f"{kpis['purchase_users']:,}",
)


st.divider()


left, right = st.columns(2)

with left:
    st.subheader("Conversion Funnel")

    funnel = get_funnel_data(df)

    fig = px.funnel(
        funnel,
        x="Events",
        y="Stage",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

with right:
    st.subheader("Event Distribution")

    distribution = get_event_distribution(df)

    fig = px.pie(
        distribution,
        names="Event Type",
        values="Events",
        hole=0.5,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


st.subheader("Daily Event Activity")

daily = get_daily_activity(df)

if daily.empty:
    st.warning(
        "No valid timestamps are available "
        "for trend analysis."
    )
else:
    fig = px.line(
        daily,
        x="Date",
        y="Events",
        markers=True,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


st.subheader("Top Categories by Event Volume")

categories = get_top_categories(df)

if categories.empty:
    st.info(
        "No category data is available."
    )
else:
    fig = px.bar(
        categories,
        x="Events",
        y="Category",
        orientation="h",
    )

    fig.update_layout(
        yaxis={
            "categoryorder": "total ascending"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


st.subheader("Decision Interpretation")

st.markdown(
    f"""
    - **{kpis['views']:,} view events** establish the
      measurable top of the funnel.
    - **{kpis['cart_rate']:.2f}% cart rate** indicates how
      often view activity progresses to purchase intent.
    - **{kpis['cart_to_purchase_rate']:.2f}% cart-to-purchase
      rate** indicates downstream conversion performance.
    - **{kpis['purchase_rate']:.2f}% purchase rate** provides
      the governed end-to-end conversion signal.
    """
)