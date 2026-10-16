import csv
from datetime import datetime
from pathlib import Path

from database import initialize_database, save_incident, save_pipeline_config, save_run
from freshness import calculate_freshness
from incident_generator import generate_incident
from monitor import evaluate_sla
from validation import validate_arrivals, validate_configs


DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def main():
    project_dir = Path(__file__).resolve().parent.parent
    database_path = project_dir / "monitor.db"
    config_path = project_dir / "data" / "pipeline_config.csv"
    arrivals_path = project_dir / "data" / "sample_arrivals.csv"
    schema_path = project_dir / "sql" / "schema.sql"

    with config_path.open(newline="", encoding="utf-8") as file:
        configs = validate_configs(csv.DictReader(file))

    with arrivals_path.open(newline="", encoding="utf-8") as file:
        arrivals = validate_arrivals(csv.DictReader(file), configs)

    initialize_database(database_path, schema_path)

    for config in configs.values():
        save_pipeline_config(
            database_path,
            config["pipeline_name"],
            config["expected_time"],
            int(config["sla_minutes"]),
        )

    results = []
    incidents = []

    for arrival in arrivals:
        config = configs[arrival["pipeline_name"]]
        expected_at = datetime.strptime(
            f"{arrival['run_date']} {config['expected_time']}:00", DATE_TIME_FORMAT
        )
        actual_arrival = None
        if arrival["actual_arrival"]:
            actual_arrival = datetime.strptime(arrival["actual_arrival"], DATE_TIME_FORMAT)
        checked_at = datetime.strptime(arrival["checked_at"], DATE_TIME_FORMAT)
        sla_minutes = int(config["sla_minutes"])

        status, delay_minutes = evaluate_sla(
            expected_at, actual_arrival, sla_minutes
        )
        freshness_minutes = calculate_freshness(actual_arrival, checked_at)

        run_id = save_run(
            database_path,
            arrival["pipeline_name"],
            expected_at,
            actual_arrival,
            status,
            delay_minutes,
            freshness_minutes,
            checked_at,
        )

        if status != "HEALTHY":
            message = generate_incident(
                arrival["pipeline_name"],
                expected_at,
                actual_arrival,
                delay_minutes,
                sla_minutes,
                status,
            )
            save_incident(database_path, run_id, checked_at, message)
            incidents.append(message)

        results.append(
            (
                arrival["pipeline_name"],
                expected_at.strftime("%H:%M"),
                actual_arrival.strftime("%H:%M") if actual_arrival else "MISSING",
                status,
                f"{delay_minutes} min" if delay_minutes is not None else "-",
                f"{freshness_minutes} min"
                if freshness_minutes is not None
                else "-",
            )
        )

    separator = "-" * 76
    healthy_count = sum(result[3] == "HEALTHY" for result in results)
    breached_count = sum(result[3] == "BREACHED" for result in results)
    missing_count = sum(result[3] == "MISSING" for result in results)

    print("SLA & FRESHNESS MONITOR")
    print(separator)
    print(
        f"{'Pipeline':<18}{'Expected':<12}{'Actual':<12}"
        f"{'Status':<12}{'Delay':<10}{'Freshness'}"
    )
    for result in results:
        print(
            f"{result[0]:<18}{result[1]:<12}{result[2]:<12}"
            f"{result[3]:<12}{result[4]:<10}{result[5]}"
        )

    print(separator)
    print(f"Total pipelines checked: {len(results)}")
    print(f"Healthy: {healthy_count}")
    print(f"Breached: {breached_count}")
    print(f"Missing: {missing_count}")
    print(f"Incidents created: {len(incidents)}")

    if incidents:
        print("\nINCIDENTS")
        print(separator)
        for message in incidents:
            print(f"\n{message}")


if __name__ == "__main__":
    main()
