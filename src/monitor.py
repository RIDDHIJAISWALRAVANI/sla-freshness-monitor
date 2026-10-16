from datetime import timedelta


def evaluate_sla(expected_at, actual_arrival, sla_minutes):
    if actual_arrival is None:
        return "MISSING", None

    delay_minutes = int((actual_arrival - expected_at).total_seconds() / 60)
    deadline = expected_at + timedelta(minutes=sla_minutes)

    if actual_arrival <= deadline:
        return "HEALTHY", max(delay_minutes, 0)

    return "BREACHED", delay_minutes
