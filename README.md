# SLA & Freshness Monitor

## Project overview

This project simulates three data pipelines and checks whether their data arrives within configured SLA limits. It also calculates freshness, stores monitoring history in SQLite, and creates incident messages for late or missing data.

## Problem statement

Data pipelines are expected to deliver data at known times. This lightweight monitor answers four questions: did the data arrive, did it meet its SLA, how old is the latest data, and does an incident need to be raised?

## Architecture

```text
CSV configuration + sample arrivals
              |
              v
        Python monitor
              |
       +------+------+
       |             |
       v             v
   SLA check      Freshness
       |
       v
   SQLite history
       |
       v
 Incident message
```

## File structure

```text
sla-freshness-monitor/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── pipeline_config.csv
│   └── sample_arrivals.csv
├── sql/
│   ├── schema.sql
│   └── queries.sql
├── src/
│   ├── main.py
│   ├── database.py
│   ├── monitor.py
│   ├── freshness.py
│   ├── validation.py
│   └── incident_generator.py
├── tests/
│   ├── test_monitor.py
│   ├── test_incident.py
│   └── test_validation.py
└── docs/
    └── design_decision_note.md
```

## How to set up, run, and test

Python 3.9 or newer is recommended.

From the project directory, install the only development dependency, `pytest`:

```powershell
python -m pip install -r requirements.txt
```

Run the monitor against the included synthetic CSV data:

```powershell
python src/main.py
```

The command creates `monitor.db` in the project folder. Running it again adds new history instead of deleting earlier runs.

Run the complete automated test suite:

```powershell
python -m pytest
```

## Data validation

Input rows are validated before monitoring results are calculated. Pipeline names must be unique, expected times and timestamps must use the documented formats, and SLA values must be positive integers. Each arrival must reference a configured pipeline, and duplicate arrivals for the same pipeline and run date are rejected. A blank `actual_arrival` is intentionally accepted and classified as `MISSING`.

## Data model

SQLite stores the monitoring data in three tables:

- `pipeline_config` contains one configuration row per pipeline. `pipeline_name` is unique, and reruns update its expected time and SLA tolerance.
- `pipeline_runs` stores each monitoring observation, including the expected and actual arrival times, SLA status, delay, freshness, and check time. Repeated executions append history rather than replacing earlier observations.
- `incidents` stores the message created for each breached or missing run. Its `run_id` foreign key links the incident to the corresponding row in `pipeline_runs`.

The logical flow is `pipeline_config` → `pipeline_runs` → `incidents`. Table definitions are available in `sql/schema.sql`, and example history and incident queries are in `sql/queries.sql`.

## SLA calculation

SLA answers: **Did the data arrive within the allowed time?**

The deadline is the expected arrival timestamp plus the configured SLA tolerance. A missing arrival is `MISSING`, an arrival at or before the deadline is `HEALTHY`, and a later arrival is `BREACHED`. Delay is the number of complete minutes after the expected time; early arrivals show zero.

## Freshness calculation

Freshness answers: **How old is the latest available data at the time of the check?**

It is calculated as `checked_at - actual_arrival` in minutes. A missing arrival has no freshness value. The sample uses fixed, naive local datetimes so every run produces the same result.

## Example output

```text
SLA & FRESHNESS MONITOR
----------------------------------------------------------------------------

Pipeline          Expected    Actual      Status      Delay     Freshness
customer_daily    06:00       05:57       HEALTHY     0 min     543 min
orders_hourly     14:10       14:26       BREACHED    16 min    34 min
payments_daily    08:00       MISSING     MISSING     -         -
----------------------------------------------------------------------------
Total pipelines checked: 3
Healthy: 1
Breached: 1
Missing: 1
Incidents created: 2
```

Incident details are printed below the table for `BREACHED` and `MISSING` pipelines.

## Tests performed

The automated suite covers healthy early data, late data, missing data, the exact SLA deadline, incident evidence, duplicate arrivals, duplicate pipeline configuration, unknown pipelines, malformed timestamps, and zero, negative, or non-numeric SLA values. The verified result is `12 passed`.

## Design decisions

The project uses only Python standard-library modules at runtime. CSV keeps the sample input readable, SQLite provides persistent local history, and rule-based incident text stays deterministic. More detail is in `docs/design_decision_note.md`.

## Limitations and production improvements

This assignment-scale project uses strict input formats, a single local timezone, and manual execution. A production version could use timezone-aware timestamps, a scheduler or orchestrator, PostgreSQL, real pipeline metadata, and an external alerting channel.
