from k6_statistics import K6Statistics


def analyze(k6_path, cpu_file_path, plots_dir, metrics_dir):
    k6_stats = K6Statistics(k6_path, cpu_file_path, plots_dir=plots_dir)

    scenarios = k6_stats.get_scenarios()

    k6_stats.plot_aggregated_results_by_variation_and_endpoint(scenarios, plot_name="aggregated_plot.png")

    table = k6_stats.generate_http_req_duration_stats(scenarios)
    print(table)

    table = k6_stats.generate_aggregated_http_req_duration_stats(scenarios)
    print(table)

    table = k6_stats.generate_aggregated_http_req_duration_stats_variation_endpoint(scenarios)
    print(table)




    # endpoints = ['json', 'db', 'queries', 'updates']
    # languages = ['python', 'java', 'go']
    # variations = ['standard', 'otel', 'elastic']
    #
    # k6_stats.show_metrics()
    # k6_stats.show_total_number_of_requests()
    #
    # for lang in languages:
    #     k6_stats.plot_overhead([f'{lang}-standard-json', f'{lang}-otel-json', f'{lang}-elastic-json'],
    #                            f'{lang}-json-overhead')
    #     k6_stats.plot_overhead([f'{lang}-standard-db', f'{lang}-otel-db', f'{lang}-elastic-db'],
    #                            f'{lang}-db-overhead')
    #     k6_stats.plot_overhead([f'{lang}-standard-queries', f'{lang}-otel-queries', f'{lang}-elastic-queries'],
    #                            f'{lang}-queries-overhead')
    #     k6_stats.plot_overhead([f'{lang}-standard-updates', f'{lang}-otel-updates', f'{lang}-elastic-updates'],
    #                            f'{lang}-updates-overhead')
    #
    # # Plot Overhead Horizontally
    # endpoints_main = ['json', 'db', 'updates']
    # for lang in languages:
    #     scenario_list = []
    #     for endpoint in endpoints_main:
    #         for variation in variations:
    #             scenario_list.append(f'{lang}-{variation}-{endpoint}')
    #     k6_stats.plot_overhead_horizontal(scenario_list, f'{lang}-overhead_horizontal')
    #
    # for lang in languages:
    #     scenario_list = []
    #     for endpoint in endpoints:
    #         for variation in variations:
    #             scenario_list.append(f'{lang}-{variation}-{endpoint}')
    #     print(scenario_list)
    #     k6_stats.plot_overhead_horizontal_endpoints(scenario_list, f'{lang}-overhead_horizontal_split')
    #
    # # Group unique container names by 'endpoint' and 'container_name'
    # container_groups = {}
    # for scenario in scenarios:
    #     container_name = scenario['container_name']
    #
    #     if container_name not in container_groups:
    #         container_groups[container_name] = set()
    #
    #     container_groups[container_name].add(scenario['endpoint'])
    #
    # # Show metrics for all scenarios
    # k6_stats.show_metrics_scenarios(scenarios, metrics_dir)
    #
    # # Plot CPU usage by Scenario
    # for lang in languages:
    #     k6_stats.plot_cpu_usage_by_scenarios(scenarios, lang, 'json',
    #                                          plot_name=f'cpu-usage-scenarios-{lang}-json')
    #     k6_stats.plot_cpu_usage_by_scenarios(scenarios, lang, 'db',
    #                                          plot_name=f'cpu-usage-scenarios-{lang}-db')
    #     k6_stats.plot_cpu_usage_by_scenarios(scenarios, lang, 'updates',
    #                                          plot_name=f'cpu-usage-scenarios-{lang}-updates')
    #     k6_stats.plot_cpu_usage_by_scenarios(scenarios, lang, 'queries',
    #                                          plot_name=f'cpu-usage-scenarios-{lang}-queries')
    #
    # k6_stats.plot_request_performance(["iteration_duration"], save_plot=True)


if __name__ == '__main__':
    # Average
    ## Old
    # k6_path = '../results/2024-05-09/2024-05-09_21-37.csv'
    # cpu_file_path = "../results/2024-05-09/cpu_usage_2024-05-09_21-37.csv"
    # plots_dir = "plots/2024-05-09/21-37"
    # metrics_dir = "metrics/2024-05-09/21-37"
    ## New
    # k6_path = '../results/2024-05-22/2024-05-22_18-03.csv'
    # cpu_file_path = "../results/2024-05-22/cpu_usage_2024-05-22_18-03.csv"
    # plots_dir = "plots/2024-05-22/18-03"
    # metrics_dir = "metrics/2024-05-22/18-03"
    #
    # analyze(k6_path, cpu_file_path, plots_dir, metrics_dir)

    ## New 2
    k6_path_2 = '../results/2024-05-22/2024-05-22_19-33.csv'
    cpu_file_path_2 = "../results/2024-05-22/cpu_usage_2024-05-22_19-33.csv"
    plots_dir_2 = "plots/2024-05-22/19-33"
    metrics_dir_2 = "metrics/2024-05-22/19-33"

    analyze(k6_path_2, cpu_file_path_2, plots_dir_2, metrics_dir_2)

    # Min
    # k6_path = '../results/2024-05-09/2024-05-09_22-25.csv'
    # cpu_file_path = "../results/2024-05-09/cpu_usage_2024-05-09_22-25.csv"
    # plots_dir = "plots/2024-05-09/22-25"
    # metrics_dir = "metrics/2024-05-09/22-25"
