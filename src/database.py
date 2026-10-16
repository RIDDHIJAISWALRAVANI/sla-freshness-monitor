import sqlite3


def initialize_database(database_path, schema_path):
    schema = schema_path.read_text(encoding="utf-8")

    with sqlite3.connect(database_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(schema)


def save_pipeline_config(database_path, pipeline_name, expected_time, sla_minutes):
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            INSERT INTO pipeline_config (pipeline_name, expected_time, sla_minutes)
            VALUES (?, ?, ?)
            ON CONFLICT(pipeline_name) DO UPDATE SET
                expected_time = excluded.expected_time,
                sla_minutes = excluded.sla_minutes
            """,
            (pipeline_name, expected_time, sla_minutes),
        )


def save_run(
    database_path,
    pipeline_name,
    expected_at,
    actual_arrival,
    status,
    delay_minutes,
    freshness_minutes,
    checked_at,
):
    with sqlite3.connect(database_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO pipeline_runs (
                pipeline_name, expected_at, actual_arrival, status,
                delay_minutes, freshness_minutes, checked_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                pipeline_name,
                expected_at.isoformat(sep=" "),
                actual_arrival.isoformat(sep=" ") if actual_arrival else None,
                status,
                delay_minutes,
                freshness_minutes,
                checked_at.isoformat(sep=" "),
            ),
        )
        return cursor.lastrowid


def save_incident(database_path, run_id, created_at, message):
    with sqlite3.connect(database_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(
            """
            INSERT INTO incidents (run_id, created_at, message)
            VALUES (?, ?, ?)
            """,
            (run_id, created_at.isoformat(sep=" "), message),
        )
