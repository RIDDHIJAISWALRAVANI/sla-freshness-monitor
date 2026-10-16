# Design Decision Note

## Python

Python is readable and well suited to implementing the monitoring logic. Its standard library provides the CSV, datetime, and SQLite support needed by this project.

## SQLite

The requirement is Python and SQL. SQLite satisfies the SQL requirement while keeping the project self-contained and avoiding database server setup. Each execution inserts new run and incident rows, so earlier monitoring history is retained.

## CSV input

CSV provides simple, inspectable mock input for the three synthetic pipelines. Fixed arrival and check timestamps make the demonstration reproducible.

## Monitoring logic

The SLA deadline is `expected_at + SLA tolerance`. Missing data is `MISSING`, data at or before the deadline is `HEALTHY`, and later data is `BREACHED`. Delay records the number of minutes after the expected time, with early arrivals shown as zero.

Freshness is calculated as `checked_at - actual_arrival`. It describes the age of the latest available data at check time and remains separate from the SLA decision. Missing data has no freshness value.

## Incident messages

Incidents are rule-based because the required evidence is structured and the output should be deterministic. External or AI APIs would add dependencies without helping this assignment.

## Limitations and production considerations

This is an assignment-scale implementation. It assumes valid CSV input, manual execution, and naive datetimes in one local time context. A production version could use timezone-aware timestamps, PostgreSQL, a scheduler or orchestrator, and an external alerting service. Those technologies are not needed for this demonstration.
