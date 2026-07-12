import numpy as np
import pandas as pd


REQUIRED_COLUMNS = [
    "event_time",
    "event_type",
    "product_id",
    "category_id",
    "price",
    "user_id",
    "user_session",
]


def calculate_data_quality(
    df: pd.DataFrame,
) -> dict:
    total_rows = len(df)

    if total_rows == 0:
        return {
            "total_rows": 0,
            "duplicate_rows": 0,
            "duplicate_rate": 0.0,
            "total_nulls": 0,
            "null_rate": 0.0,
            "invalid_prices": 0,
            "invalid_timestamps": 0,
            "missing_sessions": 0,
            "unknown_events": 0,
            "quality_score": 0.0,
            "status": "FAIL",
        }

    duplicate_rows = int(
        df.duplicated().sum()
    )

    duplicate_rate = (
        duplicate_rows
        / total_rows
        * 100
    )

    available_required = [
        column
        for column in REQUIRED_COLUMNS
        if column in df.columns
    ]

    total_cells = (
        total_rows
        * len(available_required)
    )

    total_nulls = int(
        df[
            available_required
        ].isna().sum().sum()
    )

    null_rate = (
        total_nulls
        / total_cells
        * 100
        if total_cells > 0
        else 0
    )

    invalid_prices = int(
        (
            df["price"].notna()
            & (df["price"] < 0)
        ).sum()
    )

    invalid_timestamps = int(
        df["event_time"].isna().sum()
    )

    missing_sessions = int(
        df["user_session"].isna().sum()
    )

    allowed_events = {
        "view",
        "cart",
        "purchase",
    }

    unknown_events = int(
        (
            ~df["event_type"].isin(
                allowed_events
            )
            & df["event_type"].notna()
        ).sum()
    )

    # Weighted penalty model.
    duplicate_penalty = min(
        duplicate_rate * 2,
        25,
    )

    null_penalty = min(
        null_rate * 1.5,
        25,
    )

    invalid_price_rate = (
        invalid_prices
        / total_rows
        * 100
    )

    timestamp_error_rate = (
        invalid_timestamps
        / total_rows
        * 100
    )

    unknown_event_rate = (
        unknown_events
        / total_rows
        * 100
    )

    validity_penalty = min(
        (
            invalid_price_rate
            + timestamp_error_rate
            + unknown_event_rate
        )
        * 2,
        30,
    )

    session_penalty = min(
        (
            missing_sessions
            / total_rows
            * 100
        ),
        20,
    )

    quality_score = max(
        0,
        100
        - duplicate_penalty
        - null_penalty
        - validity_penalty
        - session_penalty,
    )

    if quality_score >= 90:
        status = "PASS"
    elif quality_score >= 75:
        status = "WARNING"
    else:
        status = "FAIL"

    return {
        "total_rows": total_rows,
        "duplicate_rows": duplicate_rows,
        "duplicate_rate": round(
            duplicate_rate,
            2,
        ),
        "total_nulls": total_nulls,
        "null_rate": round(
            null_rate,
            2,
        ),
        "invalid_prices": invalid_prices,
        "invalid_timestamps": (
            invalid_timestamps
        ),
        "missing_sessions": (
            missing_sessions
        ),
        "unknown_events": unknown_events,
        "quality_score": round(
            quality_score,
            2,
        ),
        "status": status,
    }


def get_column_quality(
    df: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    for column in df.columns:
        null_count = int(
            df[column].isna().sum()
        )

        null_rate = (
            null_count
            / len(df)
            * 100
            if len(df) > 0
            else 0
        )

        unique_values = int(
            df[column].nunique(
                dropna=True
            )
        )

        rows.append(
            {
                "Column": column,
                "Data Type": str(
                    df[column].dtype
                ),
                "Null Count": null_count,
                "Null Rate (%)": round(
                    null_rate,
                    2,
                ),
                "Unique Values": (
                    unique_values
                ),
            }
        )

    return pd.DataFrame(rows)


def get_quality_checks(
    df: pd.DataFrame,
) -> pd.DataFrame:
    quality = calculate_data_quality(df)

    checks = [
        {
            "Check": "Duplicate rows",
            "Observed": (
                quality["duplicate_rows"]
            ),
            "Rule": "< 1% of rows",
            "Status": (
                "PASS"
                if quality[
                    "duplicate_rate"
                ] < 1
                else "WARNING"
            ),
        },
        {
            "Check": "Invalid timestamps",
            "Observed": (
                quality[
                    "invalid_timestamps"
                ]
            ),
            "Rule": "0 invalid timestamps",
            "Status": (
                "PASS"
                if quality[
                    "invalid_timestamps"
                ] == 0
                else "FAIL"
            ),
        },
        {
            "Check": "Negative prices",
            "Observed": (
                quality[
                    "invalid_prices"
                ]
            ),
            "Rule": "0 negative prices",
            "Status": (
                "PASS"
                if quality[
                    "invalid_prices"
                ] == 0
                else "FAIL"
            ),
        },
        {
            "Check": "Unknown event types",
            "Observed": (
                quality["unknown_events"]
            ),
            "Rule": (
                "Only view, cart, purchase"
            ),
            "Status": (
                "PASS"
                if quality[
                    "unknown_events"
                ] == 0
                else "FAIL"
            ),
        },
        {
            "Check": "Missing sessions",
            "Observed": (
                quality[
                    "missing_sessions"
                ]
            ),
            "Rule": "< 5% of rows",
            "Status": (
                "PASS"
                if (
                    quality[
                        "missing_sessions"
                    ]
                    / max(len(df), 1)
                    * 100
                ) < 5
                else "WARNING"
            ),
        },
    ]

    return pd.DataFrame(checks)


def detect_daily_anomalies(
    df: pd.DataFrame,
) -> pd.DataFrame:
    valid_df = df.dropna(
        subset=["event_time"]
    ).copy()

    if valid_df.empty:
        return pd.DataFrame(
            columns=[
                "Date",
                "Events",
                "Z Score",
                "Anomaly",
            ]
        )

    daily = (
        valid_df
        .assign(
            Date=valid_df[
                "event_time"
            ].dt.floor("D")
        )
        .groupby("Date")
        .size()
        .reset_index(name="Events")
    )

    if len(daily) < 2:
        daily["Z Score"] = 0.0
        daily["Anomaly"] = "NORMAL"
        return daily

    mean_events = daily["Events"].mean()
    std_events = daily["Events"].std()

    if (
        pd.isna(std_events)
        or std_events == 0
    ):
        daily["Z Score"] = 0.0
    else:
        daily["Z Score"] = (
            (
                daily["Events"]
                - mean_events
            )
            / std_events
        ).round(2)

    daily["Anomaly"] = np.where(
        daily["Z Score"].abs() >= 2,
        "REVIEW",
        "NORMAL",
    )

    return daily


def get_freshness_status(
    df: pd.DataFrame,
) -> dict:
    valid_times = df[
        "event_time"
    ].dropna()

    if valid_times.empty:
        return {
            "latest_event": None,
            "dataset_span_days": 0,
            "status": "FAIL",
            "message": (
                "No valid timestamps found."
            ),
        }

    latest_event = valid_times.max()
    earliest_event = valid_times.min()

    span_days = (
        latest_event
        - earliest_event
    ).total_seconds() / 86400

    # This is a historical benchmark dataset,
    # so freshness means continuity inside
    # the loaded source window, not closeness
    # to today's date.
    status = (
        "PASS"
        if span_days > 0
        else "WARNING"
    )

    return {
        "latest_event": latest_event,
        "earliest_event": earliest_event,
        "dataset_span_days": round(
            span_days,
            2,
        ),
        "status": status,
        "message": (
            "Historical source freshness is "
            "measured against the loaded "
            "event window."
        ),
    }