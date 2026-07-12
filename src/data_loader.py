from pathlib import Path

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

FULL_DATA_FILE = DATA_DIR / "2019-Oct.csv"
SAMPLE_DATA_FILE = DATA_DIR / "2019-Oct-sample.csv"

REQUIRED_COLUMNS = [
    "event_time",
    "event_type",
    "product_id",
    "category_id",
    "category_code",
    "brand",
    "price",
    "user_id",
    "user_session",
]


def get_data_file() -> Path:
    """
    Prefer the full real dataset locally.
    Fall back to a smaller committed sample for deployment.
    """
    if FULL_DATA_FILE.exists():
        return FULL_DATA_FILE

    if SAMPLE_DATA_FILE.exists():
        return SAMPLE_DATA_FILE

    raise FileNotFoundError(
        "No dataset found. Add '2019-Oct.csv' or "
        "'2019-Oct-sample.csv' inside the data folder."
    )


def validate_schema(df: pd.DataFrame) -> None:
    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Dataset schema validation failed. "
            f"Missing columns: {', '.join(missing_columns)}"
        )


@st.cache_data(show_spinner="Loading real event data...")
def load_data(max_rows: int = 500_000) -> pd.DataFrame:
    """
    Load a controlled number of rows so the dashboard remains responsive.
    The data remains real event-level source data.
    """
    data_file = get_data_file()

    df = pd.read_csv(
        data_file,
        nrows=max_rows,
        low_memory=False,
    )

    validate_schema(df)

    # Preserve raw row count before transformations.
    df = df.copy()

    # Parse timestamp safely.
    df["event_time"] = pd.to_datetime(
        df["event_time"],
        errors="coerce",
        utc=True,
    )

    # Numeric conversion.
    df["price"] = pd.to_numeric(
        df["price"],
        errors="coerce",
    )

    # Normalize event names.
    df["event_type"] = (
        df["event_type"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    # Useful derived fields.
    df["event_date"] = df["event_time"].dt.date
    df["event_hour"] = df["event_time"].dt.hour
    df["event_day"] = df["event_time"].dt.day_name()

    return df


def get_dataset_metadata(df: pd.DataFrame) -> dict:
    data_file = get_data_file()

    valid_times = df["event_time"].dropna()

    return {
        "file_name": data_file.name,
        "rows_loaded": len(df),
        "columns": len(df.columns),
        "earliest_event": (
            valid_times.min() if not valid_times.empty else None
        ),
        "latest_event": (
            valid_times.max() if not valid_times.empty else None
        ),
        "file_size_mb": round(
            data_file.stat().st_size / (1024 * 1024),
            2,
        ),
    }