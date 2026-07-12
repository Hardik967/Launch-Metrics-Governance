import pandas as pd

from src.data_quality import (
    calculate_data_quality,
    get_freshness_status,
)
from src.metrics import calculate_kpis


def calculate_launch_readiness(
    df: pd.DataFrame,
) -> dict:
    kpis = calculate_kpis(df)
    quality = calculate_data_quality(df)
    freshness = get_freshness_status(df)

    checks = []

    checks.append(
        {
            "Control": "Event data available",
            "Category": "Pipeline",
            "Observed": (
                f"{kpis['total_events']:,} events"
            ),
            "Status": (
                "PASS"
                if kpis["total_events"] > 0
                else "FAIL"
            ),
            "Action": (
                "Verify source ingestion if "
                "no events are available."
            ),
        }
    )

    checks.append(
        {
            "Control": "Users measurable",
            "Category": "Coverage",
            "Observed": (
                f"{kpis['total_users']:,} users"
            ),
            "Status": (
                "PASS"
                if kpis["total_users"] > 0
                else "FAIL"
            ),
            "Action": (
                "Check user identifier tracking."
            ),
        }
    )

    checks.append(
        {
            "Control": "Purchase event captured",
            "Category": "Funnel",
            "Observed": (
                f"{kpis['purchases']:,} purchases"
            ),
            "Status": (
                "PASS"
                if kpis["purchases"] > 0
                else "FAIL"
            ),
            "Action": (
                "Validate purchase event wiring."
            ),
        }
    )

    checks.append(
        {
            "Control": "Data quality",
            "Category": "Governance",
            "Observed": (
                f"{quality['quality_score']}%"
            ),
            "Status": (
                "PASS"
                if quality[
                    "quality_score"
                ] >= 90
                else (
                    "WARNING"
                    if quality[
                        "quality_score"
                    ] >= 75
                    else "FAIL"
                )
            ),
            "Action": (
                "Resolve invalid, missing or "
                "duplicate records."
            ),
        }
    )

    checks.append(
        {
            "Control": "Timestamp continuity",
            "Category": "Freshness",
            "Observed": (
                f"{freshness['dataset_span_days']} "
                "day source window"
            ),
            "Status": freshness["status"],
            "Action": (
                "Investigate timestamp or "
                "source-window issues."
            ),
        }
    )

    checks_df = pd.DataFrame(checks)

    pass_count = (
        checks_df["Status"] == "PASS"
    ).sum()

    warning_count = (
        checks_df["Status"] == "WARNING"
    ).sum()

    fail_count = (
        checks_df["Status"] == "FAIL"
    ).sum()

    score = round(
        (
            (
                pass_count
                + warning_count * 0.5
            )
            / len(checks_df)
        )
        * 100,
        2,
    )

    if fail_count > 0:
        recommendation = "NO-GO"
    elif warning_count > 0:
        recommendation = "CONDITIONAL GO"
    else:
        recommendation = "GO"

    return {
        "score": score,
        "recommendation": recommendation,
        "pass_count": int(pass_count),
        "warning_count": int(
            warning_count
        ),
        "fail_count": int(fail_count),
        "checks": checks_df,
    }