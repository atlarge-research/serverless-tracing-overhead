from k6_statistics import K6Statistics

if __name__ == '__main__':
    k6_path = '../results/2024-04-26/2024-04-26_08-57.csv'
    cpu_file_path = "../results/2024-04-26/cpu_usage_2024-04-26_08-57.csv"

    k6_stats = K6Statistics(k6_path, cpu_file_path, plots_dir="plots/2024-04-26")

    scenarios = k6_stats.get_scenarios()
    for scenario in scenarios:
        print(scenario)

    k6_stats.show_metrics()
    k6_stats.show_total_number_of_requests()
    languages = ['python', 'java', 'go']
    for lang in languages:
        k6_stats.plot_overhead([f'{lang}-standard-json', f'{lang}-otel-json', f'{lang}-elastic-json'],
                                    f'{lang}-json-overhead')
        k6_stats.plot_overhead([f'{lang}-standard-db', f'{lang}-otel-db', f'{lang}-elastic-db'],
                                    f'{lang}-db-overhead')
        k6_stats.plot_overhead([f'{lang}-standard-queries', f'{lang}-otel-queries', f'{lang}-elastic-queries'],
                                    f'{lang}-queries-overhead')
        k6_stats.plot_overhead([f'{lang}-standard-updates', f'{lang}-otel-updates', f'{lang}-elastic-updates'],
                                    f'{lang}-updates-overhead')

    # Group unique container names by 'endpoint' and 'container_name'
    container_groups = {}
    for scenario in scenarios:
        container_name = scenario['container_name']

        if container_name not in container_groups:
            container_groups[container_name] = set()

        container_groups[container_name].add(scenario['endpoint'])

    # Plot CPU usage for each unique 'container_name'
    # for container_name, endpoints in container_groups.items():
    #     k6_stats.plot_cpu_usage_by_endpoints(container_name, scenarios,
    #                                          plot_name=f'cpu-usage-endpoints-{container_name}')

    for lang in languages:
        k6_stats.plot_cpu_usage_by_scenarios(scenarios, lang, 'json',
                                             plot_name=f'cpu-usage-scenarios-{lang}-json')
        k6_stats.plot_cpu_usage_by_scenarios(scenarios, lang, 'db',
                                             plot_name=f'cpu-usage-scenarios-{lang}-db')
        k6_stats.plot_cpu_usage_by_scenarios(scenarios, lang, 'updates',
                                             plot_name=f'cpu-usage-scenarios-{lang}-updates')
        k6_stats.plot_cpu_usage_by_scenarios(scenarios, lang, 'queries',
                                             plot_name=f'cpu-usage-scenarios-{lang}-queries')

    # k6_stats.plot_request_performance(["iteration_duration"], save_plot=True)
