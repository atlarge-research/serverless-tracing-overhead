import subprocess
import docker
import time
from datetime import datetime
import threading

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


def run_test(rps, duration, url):
    k6_command_template = f"k6 run --vus {rps} -e RPS={rps} -e DURATION={duration} -e URL={url} script.js"
    subprocess.run(k6_command_template, shell=True)


def monitor_cpu_usage(container_id, duration):
    # Calculate the sleep durations for the 1/3, 1/2, and 2/3 intervals
    measurement_points = [duration / 3, duration / 2, 2 * duration / 3]
    last_sleep_time = 0
    cpu_usage_percentages = []

    for point in measurement_points:
        # Sleep only the difference to reach the next point, adjusting for any previous sleep
        sleep_duration = point - last_sleep_time
        time.sleep(sleep_duration)
        last_sleep_time = point  # Update the last sleep time

        # Measure and store the CPU usage
        cpu_usage = get_cpu_usage(container_id)  # This function must be defined elsewhere
        cpu_usage_percentages.append(cpu_usage)
        log_to_file(f"CPU usage at point {point}s: {cpu_usage}")

    # Return the max
    return max(cpu_usage_percentages)


def calibrate(host, port, endpoint, container_id, max_rps, duration):
    rps = initial_rps
    url = f"http://{host}:{port}/{endpoint}"
    reached_target = False
    while rps <= max_rps:
        print(f"Testing with {rps} RPS for {duration} seconds, targeting {url}, on container {container_id}")
        log_to_file(f"Testing with {rps} RPS for {duration} seconds, targeting {url}, on container {container_id}")

        # Start monitoring CPU usage in the background at the halfway point of the duration
        # threading.Thread(target=monitor_cpu_usage_in_background, args=(container_id, duration)).start()
        # Run the K6 test
        threading.Thread(target=run_test, args=(rps, duration, url)).start()

        max_cpu_usage = monitor_cpu_usage(container_id, duration)

        if max_cpu_usage >= target_cpu_usage:
            log_to_file(f"Reached target CPU utilization with {rps} RPS\n")
            reached_target = True
            break
        else:
            rps += rps_increment

    if not reached_target:
        log_to_file(
            f"Did not reach target CPU Utilization for port {port} and endpoint {endpoint} and container_id {container_id}\n")

    return reached_target, rps


python_port = 5000
python_otel_port = 5001
go_port = 5100
go_otel_port = 5101

python_flask_container = "micro-benchmark-python-flask-1"
python_otel_flask_container = "micro-benchmark-python-otel-flask-1"
go_container = "micro-benchmark-go-go-1"
go_otel_container = "micro-benchmark-go-otel-go-1"

scenarios = [
    # Standard Python
    # {"language": "python", "endpoint": "plain", "port": python_port, "container_id": python_flask_container},
    # {"language": "python", "endpoint": "json", "port": python_port, "container_id": python_flask_container},
    # {"language": "python", "endpoint": "db", "port": python_port, "container_id": python_flask_container},
    # {"language": "python", "endpoint": "queries", "port": python_port, "container_id": python_flask_container},
    # {"language": "python", "endpoint": "updates", "port": python_port, "container_id": python_flask_container},
    # # Python OTEL
    # {"language": "python", "endpoint": "plain", "port": python_otel_port, "container_id": python_otel_flask_container},
    # {"language": "python", "endpoint": "json", "port": python_otel_port, "container_id": python_otel_flask_container},
    # {"language": "python", "endpoint": "db", "port": python_otel_port, "container_id": python_otel_flask_container},
    # {"language": "python", "endpoint": "queries", "port": python_otel_port, "container_id": python_otel_flask_container},
    # {"language": "python", "endpoint": "updates", "port": python_otel_port, "container_id": python_otel_flask_container},
    # GO
    {"language": "go", "endpoint": "plain", "port": go_port, "container_id": go_container},
    {"language": "go", "endpoint": "json", "port": go_port, "container_id": go_container},
    {"language": "go", "endpoint": "db", "port": go_port, "container_id": go_container},
    {"language": "go", "endpoint": "queries", "port": go_port, "container_id": go_container},
    {"language": "go", "endpoint": "updates", "port": go_port, "container_id": go_container},
    # GO OTEL
    {"language": "go", "endpoint": "plain", "port": go_otel_port, "container_id": go_otel_container},
    {"language": "go", "endpoint": "json", "port": go_otel_port, "container_id": go_otel_container},
    {"language": "go", "endpoint": "db", "port": go_otel_port, "container_id": go_otel_container},
    {"language": "go", "endpoint": "queries", "port": go_otel_port, "container_id": go_otel_container},
    {"language": "go", "endpoint": "updates", "port": go_otel_port, "container_id": go_otel_container},
]

initial_rps = 1000  # Starting RPS
rps_increment = 100  # Increment RPS by this amount each iteration
target_cpu_usage = 80.0
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_file_path = f"cpu_utilization_log_{current_time}.txt"


def main():
    # For python, make a separate one for GO
    with open(log_file_path, "w") as log_file:  # Clear the log file and start fresh
        log_file.write("RPS, CPU Usage (%)\n")
    # print(get_cpu_usage(python_flask_container))
    # print(get_cpu_usage(python_otel_flask_container))
    # print(get_cpu_usage(go_container))
    # print(get_cpu_usage(go_otel_container))
    host = "localhost"
    max_rps = 2000
    duration = 60  # Seconds

    for scenario in scenarios:
        log_to_file(f"=====Running scenario {scenario}=====")
        # if scenario["language"] == "go":
        #     max_rps =
        reached_target, rps = calibrate(host, scenario["port"], scenario["endpoint"], scenario["container_id"], max_rps,
                                        duration)
        # Add the target RPS if target was reached, otherwise add 0
        if reached_target:
            scenario["targetRPS"] = rps
        else:
            scenario["targetRPS"] = 0

    print(scenarios)
    log_to_file("\n\n=====FINAL RESULTS=====\n\n")
    for scenario in scenarios:
        log_to_file(scenario)


if __name__ == "__main__":
    main()
