def calculate_freshness(actual_arrival, checked_at):
    if actual_arrival is None:
        return None

    return int((checked_at - actual_arrival).total_seconds() / 60)
