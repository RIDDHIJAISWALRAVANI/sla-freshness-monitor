import pytest

from src.validation import validate_arrivals, validate_configs


VALID_CONFIG = {
    "pipeline_name": "orders_daily",
    "expected_time": "09:00",
    "sla_minutes": "15",
}

VALID_ARRIVAL = {
    "pipeline_name": "orders_daily",
    "run_date": "2026-10-16",
    "actual_arrival": "2026-10-16 09:05:00",
    "checked_at": "2026-10-16 10:00:00",
}


def test_duplicate_arrival_is_rejected():
    configs = validate_configs([VALID_CONFIG])

    with pytest.raises(ValueError, match="duplicate arrival"):
        validate_arrivals([VALID_ARRIVAL, VALID_ARRIVAL], configs)


def test_unknown_pipeline_is_rejected():
    configs = validate_configs([VALID_CONFIG])
    arrival = {**VALID_ARRIVAL, "pipeline_name": "unknown_daily"}

    with pytest.raises(ValueError, match="unknown pipeline"):
        validate_arrivals([arrival], configs)


def test_malformed_timestamp_is_rejected():
    configs = validate_configs([VALID_CONFIG])
    arrival = {**VALID_ARRIVAL, "actual_arrival": "16-10-2026 09:05"}

    with pytest.raises(ValueError, match="actual_arrival must use"):
        validate_arrivals([arrival], configs)


@pytest.mark.parametrize("sla_minutes", ["0", "-5", "fifteen"])
def test_invalid_sla_is_rejected(sla_minutes):
    config = {**VALID_CONFIG, "sla_minutes": sla_minutes}

    with pytest.raises(ValueError, match="sla_minutes must"):
        validate_configs([config])


def test_duplicate_pipeline_config_is_rejected():
    with pytest.raises(ValueError, match="duplicate pipeline"):
        validate_configs([VALID_CONFIG, VALID_CONFIG])
