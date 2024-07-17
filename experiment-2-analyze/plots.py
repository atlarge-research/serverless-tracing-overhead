import matplotlib.pyplot as plt
import pandas as pd
from plots_utils import parse_all_json_files, aggregate_benchmark_data, PYTHON_DIR, NODEJS_DIR

def plot_individual_benchmark_comparison(aggregated_df):
    benchmarks = aggregated_df['benchmark_name'].unique()
    configurations = ['non-instrumented', 'instrumented']
    colors = {'non-instrumented': 'lightblue', 'instrumented': 'lightcoral'}

    for benchmark in benchmarks:
        fig, ax = plt.subplots(figsize=(6, 6))  # Make the plot narrower

        benchmark_data = aggregated_df[aggregated_df['benchmark_name'] == benchmark]

        data = []
        colors_list = []
        labels = []

        for config in configurations:
            data.append(benchmark_data[benchmark_data['configuration'] == config]['mean_benchmark_time'].values)
            colors_list.append(colors[config])
            labels.append(f'{config.capitalize()}')

        box = ax.boxplot(data, labels=labels, patch_artist=True, medianprops=dict(color='black'), showfliers=False)

        for patch, color in zip(box['boxes'], colors_list):
            patch.set_facecolor(color)

        ax.set_title(f'Performance Impact of Distributed Tracing on {benchmark}', fontsize=14)
        ax.set_ylabel('Mean Benchmark Time (ms)', fontsize=12)
        ax.set_xlabel('Configuration', fontsize=12)
        ax.yaxis.grid(True, linestyle='--', which='both', color='gray', alpha=0.7)
        ax.set_axisbelow(True)

        plt.xticks()
        plt.tight_layout()
        plt.show()

# Example usage
benchmark_df_python = parse_all_json_files(PYTHON_DIR)
benchmark_df_nodejs = parse_all_json_files(NODEJS_DIR)
benchmark_df = pd.concat([benchmark_df_python, benchmark_df_nodejs], ignore_index=True)

aggregated_df = aggregate_benchmark_data(benchmark_df)

plot_individual_benchmark_comparison(aggregated_df)
