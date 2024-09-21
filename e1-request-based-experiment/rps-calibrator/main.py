import os.path
import subprocess
import docker
import time
from datetime import datetime
import threading
import utils
import random

# Configuration
client = docker.from_env()

QUERIES_ENDPOINT_CONFIG = 10


def get_cpu_usage(container_id):
    client = docker.from_env()
    container = client.containers.get(container_id)
    stats = container.stats(stream=False)  # Fetch a single snapshot of the CPU stats
    cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - \
                stats["precpu_stats"]["cpu_usage"]["total_usage"]
    system_cpu_delta = stats["cpu_stats"]["system_cpu_usage"] - \
                       stats["precpu_stats"]["system_cpu_usage"]
    number_cpus = stats["cpu_stats"]["online_cpus"]

    cpu_usage = (cpu_delta / system_cpu_delta) * number_cpus * 100.0 if system_cpu_delta > 0 else 0
    return cpu_usage


def log_to_file(message):
    with open(log_file_path, "a") as log_file:
        log_file.write(f"{message}\n")


def run_test(rps, duration, url, timeunit="1s"):
    k6_command_template = f"k6 run --vus {rps} -e RPS={rps} -e DURATION={duration} -e TIMEUNIT={timeunit} -e URL={url} script.js"
    subprocess.run(k6_command_template, shell=True)


def monitor_cpu_usage(container_id, duration):
    # Calculate the sleep durations for three intervals
    # measurement_points = [duration / 3, duration / 2, 2 * duration / 3]
    # Calculate the sleep durations for five intervals
    # measurement_points = [duration / 6, duration / 3, duration / 2, 2 * duration / 3, 5 * duration / 6]
    # Wait 10 seconds for load to go up, considering the duration is 60 seconds
    measurement_points = [(i + 2) * (duration / 12) for i in range(9)]
    last_sleep_time = 0
    cpu_usage_percentages = []

    for point in measurement_points:
        # Sleep only the difference to reach the next point, adjusting for any previous sleep
        sleep_duration = point - last_sleep_time
        time.sleep(sleep_duration)
        last_sleep_time = point  # Update the last sleep time

        # Measure and store the CPU usage
        cpu_usage = get_cpu_usage(container_id)
        cpu_usage_percentages.append(cpu_usage)
        log_to_file(f"CPU usage at point {point}s: {cpu_usage}")

    return check_cpu_measurements(cpu_usage_percentages)


def check_cpu_measurements_old(measurements, threshold=80, required_percentage=50):
    # Check how many are over the threshold
    over_threshold_count = sum(measurement > threshold for measurement in measurements)
    actual_required_count = len(measurements) * (required_percentage / 100.0)

    # Check if it exceeds the required percentage to be over the limit
    exceeds_threshold = over_threshold_count >= actual_required_count

    return exceeds_threshold


def check_cpu_measurements(measurements, threshold=75):
    average_cpu_usage = sum(measurements) / len(measurements)
    log_to_file(f"Average CPU Usage: {average_cpu_usage}")
    return average_cpu_usage > threshold, average_cpu_usage


def calibrate(host, port, endpoint, container_id, max_rps, initial_rps, rps_increment, duration, timeunit="1s"):
    rps = initial_rps
    avg_cpu_usage = 0

    if endpoint == "queries":
        url = f"http://{host}:{port}/{endpoint}?queries={QUERIES_ENDPOINT_CONFIG}"
    else:
        url = f"http://{host}:{port}/{endpoint}"

    reached_target = False
    while rps <= max_rps:
        print(f"Testing with {rps} RPS for {duration} seconds, targeting {url}, on container {container_id}")
        log_to_file(f"Testing with {rps} RPS for {duration} seconds, targeting {url}, on container {container_id}")

        # Run the K6 test
        threading.Thread(target=run_test, args=(rps, duration, url, timeunit)).start()

        # Check CPU usage
        exceeds_usage, avg_cpu_usage = monitor_cpu_usage(container_id, duration)

        # if max_cpu_usage >= target_cpu_usage:
        if exceeds_usage:
            log_to_file(f"Reached target CPU utilization with {rps} RPS\n")
            reached_target = True
            break
        else:
            rps += rps_increment

    if not reached_target:
        log_to_file(
            f"Did not reach target CPU Utilization for port {port} and endpoint {endpoint} and container_id {container_id}\n")

    return reached_target, rps, avg_cpu_usage


def filter_configuration_by_lang(config):
    env_language = os.getenv('LANGUAGE', 'all')

    if env_language == 'all':
        return config
    elif env_language in config:
        return {env_language: config[env_language]}
    else:
        print(f"Language '{env_language}' not found in the configuration.")
        return {}


current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
results_dir = "results"
log_file_path = f"{results_dir}/cpu_utilization_log_{current_time}.txt"
csv_file_path = f"{results_dir}/rps_calibration_results.csv"


def main():
    print("Running calibrator...")
    if not os.path.isdir(results_dir):
        os.makedirs(results_dir)
    with open(log_file_path, "w") as log_file:
        log_file.write("RPS, CPU Usage (%)\n")
    initial_rps = 100  # Starting RPS
    max_rps = 5000
    rps_increment = 100
    duration = 60  # Seconds
    timeunit = "1s"
    port = 8080

    # Generate scenarios
    endpoints = ["json", "db", "updates", "queries"]
    exclude_configs = []

    os.getenv("LANGUAGES", "all")

    filtered_configuration = filter_configuration_by_lang(utils.configuration)
    print("Configuration:", filtered_configuration)

    scenarios = utils.generate_scenarios(filtered_configuration, endpoints,
                                         exclude_configs=exclude_configs)
    # Shuffle the list so the order of scenarios won't impact results anyhow
    random.shuffle(scenarios)

    print("Running scenarios:")
    for scenario in scenarios:
        log_to_file(scenario)

    for scenario in scenarios:
        host = scenario["host"]

        # Change RPS Increment to 50 for Updates and Queries endpoint
        if scenario["endpoint"] == "updates" or scenario["endpoint"] == "queries":
            if scenario["language"] == "python":
                initial_rps = 25
                rps_increment = 25
            else:
                initial_rps = 50
                rps_increment = 50

        # Change RPS increment to 200 for JSON endpoint for Go and Java
        if scenario["endpoint"] == "json" and scenario["language"] != "python":
            initial_rps = 200
            rps_increment = 200

        log_to_file(f"=====Running scenario {scenario}=====")
        reached_target, rps, avg_cpu_usage = calibrate(host, port, scenario["endpoint"],
                                                       scenario["container_id"], max_rps,
                                                       initial_rps, rps_increment, duration, timeunit)
        # Add the target RPS if target was reached, otherwise add 0
        if reached_target:
            scenario["targetRPS"] = rps
        else:
            scenario["targetRPS"] = 0

        # Add the CPU Usage
        scenario["avgCPUUsage"] = avg_cpu_usage

    log_to_file("\n\n=====FINAL RESULTS=====\n\n")
    for scenario in scenarios:
        log_to_file(scenario)

    log_to_file("\n\n=====CSV FORMAT=====\n\n")
    # Write to experiment file
    utils.write_to_csv(scenarios, log_file_path, append=True)
    # Write to common CSV
    utils.write_to_csv(scenarios, csv_file_path, append=True)


if __name__ == "__main__":
    main()
