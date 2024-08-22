import numpy as np
import csv


dynamic_html_size_generators = {
    'test': 10,
    'small': 1000,
    'large': 100000
}
dynamic_html_event = {
    'username': 'testname',
    'random_len': dynamic_html_size_generators['test']
}

def save_each_run_results(times_dict_list, filename="each_run_results.csv"):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)

        # Write the header row
        header = ["Run"] + [f"{key} Time (ms)" for key in times_dict_list[0].keys()] + [f"{key} % of Total" for key in
                                                                                        times_dict_list[0].keys()]
        writer.writerow(header)

        # Write each run's results
        for i, times_dict in enumerate(times_dict_list):
            total_time = times_dict["total"]
            row = [i + 1] + [f"{time:.6f}" for time in times_dict.values()] + [f"{(time / total_time) * 100:.2f}" for
                                                                               time in times_dict.values()]
            writer.writerow(row)

    print(f"Results of each run saved to {filename}")


def save_aggregated_statistics(times_dict_list, filename="aggregated_statistics.csv"):
    aggregated_times = {key: [] for key in times_dict_list[0]}
    percentage_of_total = {key: [] for key in times_dict_list[0]}

    for times_dict in times_dict_list:
        total_time = times_dict["total"]
        for key, value in times_dict.items():
            aggregated_times[key].append(value)
            percentage_of_total[key].append((value / total_time) * 100)

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)

        # Write the header row
        writer.writerow(
            ["Function", "Average Time (ms)", "Median Time (ms)", "95th Percentile (ms)", "99th Percentile (ms)",
             "Average % of Total Time"])

        # Write the aggregated statistics for each function
        for func_name, times in aggregated_times.items():
            times_array = np.array(times)
            avg_time = np.mean(times_array)
            med_time = np.median(times_array)
            percentile_95 = np.percentile(times_array, 95)
            percentile_99 = np.percentile(times_array, 99)
            avg_percentage = np.mean(percentage_of_total[func_name])

            writer.writerow([
                func_name,
                f"{avg_time:.6f}",
                f"{med_time:.6f}",
                f"{percentile_95:.6f}",
                f"{percentile_99:.6f}",
                f"{avg_percentage:.2f}"
            ])

    print(f"Aggregated statistics saved to {filename}")
