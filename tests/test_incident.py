from datetime import datetime

from src.incident_generator import generate_incident


def test_incident_contains_pipeline_status_and_evidence():
    expected = datetime(2026, 10, 16, 14, 10)
    actual = datetime(2026, 10, 16, 14, 26)

    message = generate_incident(
        "orders_hourly", expected, actual, 16, 10, "BREACHED"
    )

    assert "orders_hourly" in message
    assert "Status: BREACHED" in message
    assert "Actual arrival: 2026-10-16 14:26:00" in message
    assert "Delay: 16 minutes" in message
    assert "SLA tolerance: 10 minutes" in message
