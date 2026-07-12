# Launch Metrics Governance

A Streamlit-based data analytics project for governing launch KPIs using real event-level e-commerce data.

## Purpose

The project converts raw behavioral events into trusted, traceable and decision-grade launch metrics.

The governance chain is:

**Raw Event → Source Field → Metric → KPI → Decision**

## Core Features

- Executive launch KPI overview
- Governed metric dictionary
- KPI definitions and formulas
- Event-to-decision source lineage
- Data-quality monitoring
- Duplicate detection
- Null monitoring
- Invalid timestamp detection
- Invalid price detection
- Unknown event detection
- Missing session monitoring
- Daily anomaly detection
- Historical source-window freshness checks
- Launch readiness scoring
- GO / CONDITIONAL GO / NO-GO decision
- Metric dictionary export
- Launch control register export
- Raw source evidence export

## Dataset

The project uses:

`2019-Oct.csv`

Expected columns:

- event_time
- event_type
- product_id
- category_id
- category_code
- brand
- price
- user_id
- user_session

The source contains real event-level behavioral data including:

- view
- cart
- purchase

The full dataset is intentionally excluded from Git because of its size.

## Project Structure

```text
Launch-Metrics-Governance/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/
│   ├── 2019-Oct.csv
│   └── 2019-Oct-sample.csv
│
├── pages/
│   ├── 1_Executive_Overview.py
│   ├── 2_KPI_Governance.py
│   ├── 3_Data_Quality.py
│   ├── 4_Event_Traceability.py
│   ├── 5_Launch_Readiness.py
│   └── 6_Metric_Dictionary.py
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── metrics.py
│   ├── data_quality.py
│   ├── governance.py
│   └── readiness.py
│
└── assets/
    └── style.css
```

## Installation

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it on macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Dataset Setup

Place the full dataset at:

```text
data/2019-Oct.csv
```

For deployment, a smaller sample can be placed at:

```text
data/2019-Oct-sample.csv
```

The application automatically prefers the full local dataset and falls back to the sample dataset.

## Run the Dashboard

```bash
streamlit run app.py
```

## Governed KPIs

The dashboard governs metrics including:

- Total Events
- Unique Users
- Unique Sessions
- View Events
- Cart Events
- Purchase Events
- Cart Rate
- Purchase Rate
- Cart-to-Purchase Rate
- Data Quality Score

Every governed metric includes:

- Definition
- Formula
- Source
- Required field
- Owner
- Decision
- Guardrail
- Governance status

## Data Quality Controls

The project checks:

- Duplicate records
- Missing required values
- Invalid timestamps
- Negative prices
- Unknown event types
- Missing session identifiers
- Suspicious daily event-volume changes

## Launch Decision Logic

The final launch recommendation is:

### GO

All configured measurement controls pass.

### CONDITIONAL GO

No blocking failures exist, but warning conditions require acknowledgement.

### NO-GO

One or more measurement controls fail.

## Deployment Note

The full dataset should not be pushed to GitHub because of its size.

Create a smaller deployment sample if required:

```python
import pandas as pd

df = pd.read_csv(
    "data/2019-Oct.csv",
    nrows=100000
)

df.to_csv(
    "data/2019-Oct-sample.csv",
    index=False
)
```

The deployed application will automatically use the sample file when the full dataset is unavailable.