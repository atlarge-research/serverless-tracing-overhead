import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.gridspec import GridSpec
from plots_utils import parse_all_json_files, aggregate_benchmark_data, PYTHON_DIR, NODEJS_DIR
from textwrap import wrap

plt.rcParams.update({'font.size': 18})

def plot_all_benchmarks_together(aggregated_df):
    # benchmarks = aggregated_df['benchmark_name'].unique()
    ordered_benchmarks = ['dynamic-html', 'uploader', 'thumbnailer', 'video-processing', 'graph-pagerank']
    configurations = ['non-instrumented', 'instrumented']
    colors = {'non-instrumented': 'lightblue', 'instrumented': 'lightcoral'}

    fig = plt.figure(figsize=(18, 12))
    gs = GridSpec(2, 8, height_ratios=[1, 1])

    subplot_positions = [
        (gs[0, 1:3], ordered_benchmarks[0] if len(ordered_benchmarks) > 0 else None),
        (gs[0, 3:5], ordered_benchmarks[1] if len(ordered_benchmarks) > 1 else None),
        (gs[0, 5:7], ordered_benchmarks[2] if len(ordered_benchmarks) > 2 else None),
        (gs[1, 2:4], ordered_benchmarks[3] if len(ordered_benchmarks) > 3 else None),
        (gs[1, 4:6], ordered_benchmarks[4] if len(ordered_benchmarks) > 4 else None)
    ]

    for position, benchmark in subplot_positions:
        if benchmark is None:
            continue

        ax = fig.add_subplot(position)
        benchmark_data = aggregated_df[aggregated_df['benchmark_name'] == benchmark]

        data = []
        colors_list = []
        labels = []

        for config in configurations:
            data.append(benchmark_data[benchmark_data['configuration'] == config]['mean_benchmark_time'].values)
            colors_list.append(colors[config])
            if config == "non-instrumented":
                config = "Non-\nInstrumented"
            labels.append(f'{config.capitalize()}')

        box = ax.boxplot(data, labels=labels, patch_artist=True, medianprops=dict(color='black'), showfliers=False)

        for patch, color in zip(box['boxes'], colors_list):
            patch.set_facecolor(color)

        ax.set_title(f'{benchmark}', fontsize=18)
        ax.yaxis.grid(True, linestyle='--', which='both', color='gray', alpha=0.7)
        ax.set_axisbelow(True)

    # Adjust the layout
    plt.tight_layout(rect=[0.03, 0.05, 1, 0.95])

    # Add the global labels
    fig.text(0.5, 0.04, 'Configuration', ha='center', fontsize=22)
    fig.text(0.12, 0.5, 'Mean Benchmark Time (ms)', va='center', rotation='vertical', fontsize=22)

    # Save the figure as a PDF
    plt.savefig('all_benchmarks_performance_impact.pdf', bbox_inches='tight')
    plt.show()

# Example usage
benchmark_df_python = parse_all_json_files(PYTHON_DIR)
benchmark_df_nodejs = parse_all_json_files(NODEJS_DIR)
benchmark_df = pd.concat([benchmark_df_python, benchmark_df_nodejs], ignore_index=True)

aggregated_df = aggregate_benchmark_data(benchmark_df)

plot_all_benchmarks_together(aggregated_df)
