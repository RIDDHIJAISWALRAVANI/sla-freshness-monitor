def generate_incident(
    pipeline_name,
    expected_at,
    actual_arrival,
    delay_minutes,
    sla_minutes,
    status,
):
    actual_text = "MISSING"
    delay_text = "N/A"

    if actual_arrival is not None:
        actual_text = actual_arrival.strftime("%Y-%m-%d %H:%M:%S")
        delay_text = f"{delay_minutes} minutes"

    return "\n".join(
        [
            f"SLA BREACH: {pipeline_name}",
            f"Expected arrival: {expected_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Actual arrival: {actual_text}",
            f"SLA tolerance: {sla_minutes} minutes",
            f"Delay: {delay_text}",
            f"Status: {status}",
        ]
    )
