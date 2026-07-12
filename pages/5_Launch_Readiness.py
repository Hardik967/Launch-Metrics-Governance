import streamlit as st

from src.data_loader import load_data
from src.readiness import (
    calculate_launch_readiness,
)


st.set_page_config(
    page_title="Launch Readiness",
    page_icon="🚦",
    layout="wide",
)

st.title("Launch Readiness")
st.caption(
    "A governed GO / CONDITIONAL GO / NO-GO "
    "decision based on measurable controls."
)


try:
    df = load_data()
except Exception as error:
    st.error(str(error))
    st.stop()


readiness = calculate_launch_readiness(df)


st.subheader("Final Recommendation")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Readiness Score",
    f"{readiness['score']:.1f}%",
)

c2.metric(
    "Passed",
    readiness["pass_count"],
)

c3.metric(
    "Warnings",
    readiness["warning_count"],
)

c4.metric(
    "Failed",
    readiness["fail_count"],
)


recommendation = readiness[
    "recommendation"
]

if recommendation == "GO":
    st.success(
        "GO — all configured launch measurement "
        "controls have passed."
    )

elif recommendation == "CONDITIONAL GO":
    st.warning(
        "CONDITIONAL GO — no blocking failure exists, "
        "but warning conditions require acknowledgement."
    )

else:
    st.error(
        "NO-GO — at least one launch measurement "
        "control has failed."
    )


st.subheader("Launch Control Register")

checks = readiness["checks"]

st.dataframe(
    checks,
    use_container_width=True,
    hide_index=True,
)


st.subheader("Open Actions")

open_actions = checks[
    checks["Status"] != "PASS"
]

if open_actions.empty:
    st.success(
        "No open measurement blockers remain."
    )
else:
    st.dataframe(
        open_actions[
            [
                "Control",
                "Category",
                "Status",
                "Action",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


st.subheader("Measurement Sign-Off")

st.markdown(
    """
    The measurement layer is considered ready when:

    - Real source events are available and queryable.
    - Required launch KPIs are explicitly defined.
    - KPI formulas and source fields are documented.
    - Data-quality controls are passing or accepted.
    - Event lineage can be demonstrated live.
    - Open warnings and failures have named actions.
    """
)


st.download_button(
    "Download Launch Control Register",
    data=checks.to_csv(
        index=False
    ).encode("utf-8"),
    file_name=(
        "launch_control_register.csv"
    ),
    mime="text/csv",
)