CREATE TABLE IF NOT EXISTS pipeline_config (
    pipeline_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pipeline_name TEXT NOT NULL UNIQUE,
    expected_time TEXT NOT NULL,
    sla_minutes INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pipeline_name TEXT NOT NULL,
    expected_at TEXT NOT NULL,
    actual_arrival TEXT,
    status TEXT NOT NULL,
    delay_minutes INTEGER,
    freshness_minutes INTEGER,
    checked_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS incidents (
    incident_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    message TEXT NOT NULL,
    FOREIGN KEY (run_id) REFERENCES pipeline_runs (run_id)
);
