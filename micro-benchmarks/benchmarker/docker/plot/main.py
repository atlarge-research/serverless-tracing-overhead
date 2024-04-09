from k6_statistics import K6Statistics

filename = '../results/2024-04-03/json_2024-04-03_16-51.csv'


if __name__ == '__main__':
    stats = K6Statistics(filename)

    stats.show_metrics()
    stats.show_total_number_of_requests()
    stats.calculate_overhead(['python_512', 'pythonOtel_512'])
    stats.calculate_overhead(['go_512', 'goOtel_512'])
