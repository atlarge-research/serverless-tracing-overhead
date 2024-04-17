import subprocess
import docker
import time
from datetime import datetime
import threading
import utils

# Configuration
client = docker.from_env()


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
    measurement_points = [duration / 6, duration / 3, duration / 2, 2 * duration / 3, 5 * duration / 6]
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

    return check_cpu_measurements(cpu_usage_percentages, required_percentage=40)


def check_cpu_measurements(measurements, threshold=80, required_percentage=50):
    # Check how many are over the threshold
    over_threshold_count = sum(measurement > threshold for measurement in measurements)
    actual_required_count = len(measurements) * (required_percentage / 100.0)

    # Check if it exceeds the required percentage to be over the limit
    exceeds_threshold = over_threshold_count >= actual_required_count

    return exceeds_threshold


def calibrate(host, port, endpoint, container_id, max_rps, initial_rps, rps_increment, duration, timeunit="1s"):
    rps = initial_rps
    url = f"http://{host}:{port}/{endpoint}"
    reached_target = False
    while rps <= max_rps:
        print(f"Testing with {rps} RPS for {duration} seconds, targeting {url}, on container {container_id}")
        log_to_file(f"Testing with {rps} RPS for {duration} seconds, targeting {url}, on container {container_id}")

        # Run the K6 test
        threading.Thread(target=run_test, args=(rps, duration, url, timeunit)).start()

        # Check CPU usage
        exceeds_usage = monitor_cpu_usage(container_id, duration)

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

    return reached_target, rps


target_cpu_usage = 80.0
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_file_path = f"cpu_utilization_log_{current_time}.txt"


def main():
    print("Running calibrator...")
    with open(log_file_path, "w") as log_file:
        log_file.write("RPS, CPU Usage (%)\n")
    initial_rps = 400  # Starting RPS
    max_rps = 5000
    rps_increment = 200
    duration = 60  # Seconds
    timeunit = "1s"
    port = 8080

    # Generate scenarios
    endpoints = ["json", "queries"]
    exclude_configs = ['elastic']

    scenarios = utils.generate_scenarios(utils.configuration, endpoints,
                                         exclude_configs=exclude_configs)

    print("Running scenarios:")
    for scenario in scenarios:
        log_to_file(scenario)

    for scenario in scenarios:
        host = scenario["host"]

        log_to_file(f"=====Running scenario {scenario}=====")
        reached_target, rps = calibrate(host, port, scenario["endpoint"],
                                        scenario["container_id"], max_rps,
                                        initial_rps, rps_increment, duration, timeunit)
        # Add the target RPS if target was reached, otherwise add 0
        if reached_target:
            scenario["targetRPS"] = rps
        else:
            scenario["targetRPS"] = 0

    log_to_file("\n\n=====FINAL RESULTS=====\n\n")
    for scenario in scenarios:
        log_to_file(scenario)


if __name__ == "__main__":
    main()


# Do two runs
# Another with 5 CPU measurement intervals, check that 2/5 measurement points are over 80%