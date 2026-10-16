from datetime import datetime

from src.monitor import evaluate_sla


def test_data_before_deadline_is_healthy():
    expected = datetime(2026, 10, 16, 6, 0)
    actual = datetime(2026, 10, 16, 5, 57)

    assert evaluate_sla(expected, actual, 10) == ("HEALTHY", 0)


def test_late_data_is_breached():
    expected = datetime(2026, 10, 16, 14, 10)
    actual = datetime(2026, 10, 16, 14, 20, 30)

    assert evaluate_sla(expected, actual, 10) == ("BREACHED", 10)


def test_missing_data_is_missing():
    expected = datetime(2026, 10, 16, 8, 0)

    assert evaluate_sla(expected, None, 15) == ("MISSING", None)


def test_data_at_sla_deadline_is_healthy():
    expected = datetime(2026, 10, 16, 14, 10)
    actual = datetime(2026, 10, 16, 14, 20)

    assert evaluate_sla(expected, actual, 10) == ("HEALTHY", 10)
