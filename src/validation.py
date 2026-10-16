from datetime import datetime


DATE_FORMAT = "%Y-%m-%d"
DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
TIME_FORMAT = "%H:%M"


def _required_value(row, field_name, row_number, source_name):
    value = row.get(field_name)
    value = value.strip() if value is not None else ""
    if not value:
        raise ValueError(
            f"{source_name} row {row_number}: {field_name} is required"
        )
    return value


def validate_configs(rows):
    configs = {}

    for row_number, row in enumerate(rows, start=2):
        pipeline_name = _required_value(
            row, "pipeline_name", row_number, "pipeline_config.csv"
        )
        if pipeline_name in configs:
            raise ValueError(
                f"pipeline_config.csv row {row_number}: duplicate pipeline "
                f"'{pipeline_name}'"
            )

        expected_time = _required_value(
            row, "expected_time", row_number, "pipeline_config.csv"
        )
        try:
            datetime.strptime(expected_time, TIME_FORMAT)
        except ValueError as error:
            raise ValueError(
                f"pipeline_config.csv row {row_number}: expected_time must use HH:MM"
            ) from error

        sla_text = _required_value(
            row, "sla_minutes", row_number, "pipeline_config.csv"
        )
        try:
            sla_minutes = int(sla_text)
        except ValueError as error:
            raise ValueError(
                f"pipeline_config.csv row {row_number}: sla_minutes must be an integer"
            ) from error
        if sla_minutes <= 0:
            raise ValueError(
                f"pipeline_config.csv row {row_number}: sla_minutes must be positive"
            )

        configs[pipeline_name] = {
            "pipeline_name": pipeline_name,
            "expected_time": expected_time,
            "sla_minutes": sla_minutes,
        }

    return configs


def validate_arrivals(rows, configs):
    arrivals = []
    seen_arrivals = set()

    for row_number, row in enumerate(rows, start=2):
        pipeline_name = _required_value(
            row, "pipeline_name", row_number, "sample_arrivals.csv"
        )
        if pipeline_name not in configs:
            raise ValueError(
                f"sample_arrivals.csv row {row_number}: unknown pipeline "
                f"'{pipeline_name}'"
            )

        run_date = _required_value(
            row, "run_date", row_number, "sample_arrivals.csv"
        )
        try:
            datetime.strptime(run_date, DATE_FORMAT)
        except ValueError as error:
            raise ValueError(
                f"sample_arrivals.csv row {row_number}: run_date must use YYYY-MM-DD"
            ) from error

        arrival_key = (pipeline_name, run_date)
        if arrival_key in seen_arrivals:
            raise ValueError(
                f"sample_arrivals.csv row {row_number}: duplicate arrival for "
                f"'{pipeline_name}' on {run_date}"
            )
        seen_arrivals.add(arrival_key)

        actual_value = row.get("actual_arrival")
        actual_arrival = actual_value.strip() if actual_value is not None else ""
        if actual_arrival:
            try:
                datetime.strptime(actual_arrival, DATE_TIME_FORMAT)
            except ValueError as error:
                raise ValueError(
                    f"sample_arrivals.csv row {row_number}: actual_arrival must use "
                    "YYYY-MM-DD HH:MM:SS"
                ) from error

        checked_at = _required_value(
            row, "checked_at", row_number, "sample_arrivals.csv"
        )
        try:
            datetime.strptime(checked_at, DATE_TIME_FORMAT)
        except ValueError as error:
            raise ValueError(
                f"sample_arrivals.csv row {row_number}: checked_at must use "
                "YYYY-MM-DD HH:MM:SS"
            ) from error

        arrivals.append(
            {
                "pipeline_name": pipeline_name,
                "run_date": run_date,
                "actual_arrival": actual_arrival,
                "checked_at": checked_at,
            }
        )

    return arrivals
