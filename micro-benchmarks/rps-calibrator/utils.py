import os
import subprocess
import uuid

import docker
import csv


def generate_scenarios(configuration, endpoints, exclude_configs=None):
    client = docker.from_env()
    all_containers = client.containers.list()  # Get all running containers
    scenarios = []

    if exclude_configs is None:
        exclude_configs = []

    # Generate expected hostnames from the configuration dictionary, considering exclusions
    expected_hostnames = []
    for base, configs in configuration.items():
        for config in configs:
            if config not in exclude_configs:
                expected_hostnames.append(f"{base}-{config}")

    # Filter containers by expected hostnames
    containers = [container for container in all_containers if
                  container.attrs['Config']['Hostname'] in expected_hostnames]

    for container in containers:
        # Extract the hostname, which is used as both host and container_id
        hostname = container.attrs['Config']['Hostname']
        parts = hostname.split('-')
        if len(parts) < 2:
            continue

        language = parts[0]
        config = '-'.join(parts[1:])

        # Ensure that the configuration is not in the excluded list before generating scenarios
        if config not in exclude_configs:
            # Generate scenarios for each endpoint
            for endpoint in endpoints:
                scenarios.append({
                    "language": language,
                    "configuration": config,
                    "endpoint": endpoint,
                    "container_id": container.id,
                    "host": hostname,
                })

    return scenarios


def write_to_csv(scenarios, filename, append=False, exclude_headers=None):
    if exclude_headers is None:
        exclude_headers = []
    # Add a random "experiment_id" to the experiment
    experiment_id = str(uuid.uuid4())
    for row in scenarios:
        row['experiment_id'] = experiment_id

    headers = list(scenarios[0].keys())

    # Optional exclude some data
    if exclude_headers:
        headers = [h for h in headers if h not in exclude_headers]

    if not os.path.isfile(filename):
        with open(filename, 'w') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            file.close()

    # Write to file
    write_mode = "a" if append else "w"
    with open(filename, write_mode, newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        for row in scenarios:
            row_filtered = {k: v for k, v in row.items() if k not in exclude_headers}
            writer.writerow(row_filtered)
            file.close()


configuration = {
    "python": ["flask-standard", "flask-otel", "flask-elastic"],
    "go": ["standard", "otel", "elastic"],
    "java": ["spring-standard", "spring-otel", "spring-elastic"]
}
