import docker


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
    containers = [container for container in all_containers if container.attrs['Config']['Hostname'] in expected_hostnames]

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


configuration = {
    "python": ["flask-standard", "flask-otel", "flask-elastic"],
    "go": ["standard", "otel", "elastic"],
    "java": ["spring-standard", "spring-otel", "spring-elastic"]
}


# Generate the scenarios example
# ENDPOINTS = ["json", "db", "plaintext", "queries", "updates"]
# scenarios = generate_scenarios(configuration, ENDPOINTS, exclude_configs=['elastic'])
# for scenario in scenarios:
#     print(scenario)