import pandas as pd


def get_metric_dictionary() -> pd.DataFrame:
    metrics = [
        {
            "Metric": "Total Events",
            "Definition": (
                "Total number of event records "
                "received in the governed dataset."
            ),
            "Formula": "COUNT(*)",
            "Source": "All event rows",
            "Required Field": "event_type",
            "Owner": "Data Analytics",
            "Decision": (
                "Detect whether event collection "
                "volume is sufficient and flowing."
            ),
            "Guardrail": "> 0 events",
            "Status": "GOVERNED",
        },
        {
            "Metric": "Unique Users",
            "Definition": (
                "Distinct users represented "
                "in the event stream."
            ),
            "Formula": (
                "COUNT(DISTINCT user_id)"
            ),
            "Source": "user_id",
            "Required Field": "user_id",
            "Owner": "Product Analytics",
            "Decision": (
                "Assess user reach and whether "
                "launch usage is measurable."
            ),
            "Guardrail": "> 0 users",
            "Status": "GOVERNED",
        },
        {
            "Metric": "Unique Sessions",
            "Definition": (
                "Distinct browsing sessions "
                "observed in the source data."
            ),
            "Formula": (
                "COUNT(DISTINCT user_session)"
            ),
            "Source": "user_session",
            "Required Field": "user_session",
            "Owner": "Product Analytics",
            "Decision": (
                "Measure session activity and "
                "identify session tracking gaps."
            ),
            "Guardrail": (
                "Missing sessions < 5%"
            ),
            "Status": "GOVERNED",
        },
        {
            "Metric": "View Events",
            "Definition": (
                "Number of events where "
                "event_type equals view."
            ),
            "Formula": (
                "COUNT(event_type = 'view')"
            ),
            "Source": "event_type",
            "Required Field": "event_type",
            "Owner": "Growth Analytics",
            "Decision": (
                "Establish the top of the "
                "conversion funnel."
            ),
            "Guardrail": "> 0 views",
            "Status": "GOVERNED",
        },
        {
            "Metric": "Cart Events",
            "Definition": (
                "Number of add-to-cart events."
            ),
            "Formula": (
                "COUNT(event_type = 'cart')"
            ),
            "Source": "event_type",
            "Required Field": "event_type",
            "Owner": "Growth Analytics",
            "Decision": (
                "Evaluate product intent and "
                "funnel progression."
            ),
            "Guardrail": "> 0 carts",
            "Status": "GOVERNED",
        },
        {
            "Metric": "Purchase Events",
            "Definition": (
                "Number of recorded purchase "
                "events."
            ),
            "Formula": (
                "COUNT(event_type = 'purchase')"
            ),
            "Source": "event_type",
            "Required Field": "event_type",
            "Owner": "Revenue Analytics",
            "Decision": (
                "Confirm the conversion endpoint "
                "is being captured."
            ),
            "Guardrail": "> 0 purchases",
            "Status": "GOVERNED",
        },
        {
            "Metric": "Cart Rate",
            "Definition": (
                "Cart events as a percentage "
                "of view events."
            ),
            "Formula": (
                "cart events / view events * 100"
            ),
            "Source": "event_type",
            "Required Field": "event_type",
            "Owner": "Growth Analytics",
            "Decision": (
                "Investigate product discovery "
                "or product-page friction."
            ),
            "Guardrail": "> 0%",
            "Status": "GOVERNED",
        },
        {
            "Metric": "Purchase Rate",
            "Definition": (
                "Purchase events as a percentage "
                "of view events."
            ),
            "Formula": (
                "purchase events / view events * 100"
            ),
            "Source": "event_type",
            "Required Field": "event_type",
            "Owner": "Growth Analytics",
            "Decision": (
                "Evaluate overall funnel "
                "conversion health."
            ),
            "Guardrail": "> 0%",
            "Status": "GOVERNED",
        },
        {
            "Metric": "Cart-to-Purchase Rate",
            "Definition": (
                "Purchase events divided by "
                "cart events."
            ),
            "Formula": (
                "purchase events / cart events * 100"
            ),
            "Source": "event_type",
            "Required Field": "event_type",
            "Owner": "Revenue Analytics",
            "Decision": (
                "Identify checkout or purchase "
                "completion friction."
            ),
            "Guardrail": "> 0%",
            "Status": "GOVERNED",
        },
        {
            "Metric": "Data Quality Score",
            "Definition": (
                "Weighted governance score based "
                "on duplicates, nulls and invalid "
                "records."
            ),
            "Formula": (
                "100 - weighted quality penalties"
            ),
            "Source": "All required source fields",
            "Required Field": (
                "Required schema"
            ),
            "Owner": "Data Governance",
            "Decision": (
                "Block or condition launch when "
                "analytics data cannot be trusted."
            ),
            "Guardrail": ">= 90",
            "Status": "GOVERNED",
        },
    ]

    return pd.DataFrame(metrics)


def get_event_lineage() -> pd.DataFrame:
    lineage = [
        {
            "Raw Event": "view",
            "Source Field": "event_type",
            "Derived Metric": "View Events",
            "KPI": "Funnel Volume",
            "Decision": (
                "Verify top-of-funnel activity "
                "is being captured."
            ),
        },
        {
            "Raw Event": "cart",
            "Source Field": "event_type",
            "Derived Metric": "Cart Events",
            "KPI": "Cart Rate",
            "Decision": (
                "Investigate product or "
                "merchandising friction."
            ),
        },
        {
            "Raw Event": "purchase",
            "Source Field": "event_type",
            "Derived Metric": (
                "Purchase Events"
            ),
            "KPI": "Purchase Rate",
            "Decision": (
                "Evaluate whether the conversion "
                "journey is launch-ready."
            ),
        },
        {
            "Raw Event": "purchase",
            "Source Field": (
                "event_type + price"
            ),
            "Derived Metric": (
                "Gross Event Value"
            ),
            "KPI": "Revenue Signal",
            "Decision": (
                "Verify purchase value tracking "
                "before launch."
            ),
        },
        {
            "Raw Event": "all events",
            "Source Field": "event_time",
            "Derived Metric": (
                "Event Continuity"
            ),
            "KPI": "Source Freshness",
            "Decision": (
                "Investigate broken or delayed "
                "event pipelines."
            ),
        },
        {
            "Raw Event": "all events",
            "Source Field": (
                "required schema"
            ),
            "Derived Metric": (
                "Data Quality Score"
            ),
            "KPI": "Measurement Trust",
            "Decision": (
                "Block launch decisions when "
                "measurement quality is poor."
            ),
        },
    ]

    return pd.DataFrame(lineage)