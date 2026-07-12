import numpy as np
import pandas as pd


def safe_divide(numerator, denominator, multiplier=1):
    if denominator is None or denominator == 0:
        return 0.0

    return (numerator / denominator) * multiplier


def calculate_kpis(df: pd.DataFrame) -> dict:
    total_events = len(df)

    total_users = (
        df["user_id"].nunique(dropna=True)
        if "user_id" in df.columns
        else 0
    )

    total_sessions = (
        df["user_session"].nunique(dropna=True)
        if "user_session" in df.columns
        else 0
    )

    event_counts = (
        df["event_type"]
        .value_counts(dropna=False)
        .to_dict()
    )

    views = int(event_counts.get("view", 0))
    carts = int(event_counts.get("cart", 0))
    purchases = int(event_counts.get("purchase", 0))

    cart_rate = safe_divide(carts, views, 100)
    purchase_rate = safe_divide(purchases, views, 100)
    cart_to_purchase_rate = safe_divide(
        purchases,
        carts,
        100,
    )

    purchase_df = df[df["event_type"] == "purchase"]

    gross_event_value = (
        purchase_df["price"]
        .clip(lower=0)
        .fillna(0)
        .sum()
    )

    avg_purchase_value = (
        purchase_df["price"]
        .clip(lower=0)
        .dropna()
        .mean()
    )

    if pd.isna(avg_purchase_value):
        avg_purchase_value = 0.0

    events_per_user = safe_divide(
        total_events,
        total_users,
    )

    events_per_session = safe_divide(
        total_events,
        total_sessions,
    )

    purchase_users = purchase_df[
        "user_id"
    ].nunique(dropna=True)

    purchasing_user_rate = safe_divide(
        purchase_users,
        total_users,
        100,
    )

    return {
        "total_events": int(total_events),
        "total_users": int(total_users),
        "total_sessions": int(total_sessions),
        "views": views,
        "carts": carts,
        "purchases": purchases,
        "cart_rate": round(cart_rate, 2),
        "purchase_rate": round(purchase_rate, 2),
        "cart_to_purchase_rate": round(
            cart_to_purchase_rate,
            2,
        ),
        "gross_event_value": round(
            float(gross_event_value),
            2,
        ),
        "avg_purchase_value": round(
            float(avg_purchase_value),
            2,
        ),
        "events_per_user": round(
            events_per_user,
            2,
        ),
        "events_per_session": round(
            events_per_session,
            2,
        ),
        "purchase_users": int(purchase_users),
        "purchasing_user_rate": round(
            purchasing_user_rate,
            2,
        ),
    }


def get_event_distribution(
    df: pd.DataFrame,
) -> pd.DataFrame:
    distribution = (
        df["event_type"]
        .value_counts()
        .rename_axis("Event Type")
        .reset_index(name="Events")
    )

    total = distribution["Events"].sum()

    distribution["Share (%)"] = np.where(
        total > 0,
        (
            distribution["Events"]
            / total
            * 100
        ).round(2),
        0,
    )

    return distribution


def get_daily_activity(
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
                "Users",
                "Sessions",
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
        .agg(
            Events=("event_type", "size"),
            Users=("user_id", "nunique"),
            Sessions=(
                "user_session",
                "nunique",
            ),
        )
        .reset_index()
    )

    return daily


def get_funnel_data(
    df: pd.DataFrame,
) -> pd.DataFrame:
    kpis = calculate_kpis(df)

    return pd.DataFrame(
        {
            "Stage": [
                "View",
                "Cart",
                "Purchase",
            ],
            "Events": [
                kpis["views"],
                kpis["carts"],
                kpis["purchases"],
            ],
        }
    )


def get_top_categories(
    df: pd.DataFrame,
    limit: int = 10,
) -> pd.DataFrame:
    category_df = (
        df.dropna(
            subset=["category_code"]
        )
        .groupby("category_code")
        .agg(
            Events=("event_type", "size"),
            Users=("user_id", "nunique"),
        )
        .sort_values(
            "Events",
            ascending=False,
        )
        .head(limit)
        .reset_index()
        .rename(
            columns={
                "category_code": "Category"
            }
        )
    )

    return category_df