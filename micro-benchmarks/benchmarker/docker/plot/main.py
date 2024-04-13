from k6_statistics import K6Statistics

filename = '../results/2024-04-09/test_2024-04-09_18-16.csv'
cpu_filename = '../results/2024-04-09/test.csv'


if __name__ == '__main__':
    stats = K6Statistics(filename, cpu_filename)

    stats.plot_cpu_usage(["micro-benchmark-go-go-1"], 1712680070)

    # stats.show_metrics()
    # stats.show_total_number_of_requests()
    # stats.calculate_overhead(['python', 'python-otel'])
    # stats.calculate_overhead(['go', 'go-otel'])
