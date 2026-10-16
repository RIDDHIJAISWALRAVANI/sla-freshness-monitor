-- Latest pipeline status
SELECT *
FROM pipeline_runs
WHERE run_id IN (
    SELECT MAX(run_id)
    FROM pipeline_runs
    GROUP BY pipeline_name
)
ORDER BY pipeline_name;

-- Monitoring history
SELECT *
FROM pipeline_runs
ORDER BY checked_at DESC, run_id DESC;

-- SLA breaches
SELECT *
FROM pipeline_runs
WHERE status = 'BREACHED'
ORDER BY checked_at DESC;

-- Incidents
SELECT *
FROM incidents
ORDER BY created_at DESC, incident_id DESC;
