import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.gridspec import GridSpec
from plots_utils import parse_all_json_files, aggregate_benchmark_data, PYTHON_DIR, NODEJS_DIR
from textwrap import wrap
import numpy as np

plt.rcParams.update({'font.size': 18})

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec


def annotate_median(ax, data, position, endpoint):
    median = data.median()
    ax.annotate(f'Median:\n{median:.2f}',
                xy=(position, median),
                xytext=(position + endpoint, median),
                bbox=dict(boxstyle='round,pad=0.3', edgecolor='black', facecolor='white'),
                color='black',
                ha='center',
                va='center',
                fontsize='16')


def plot_all_benchmarks_together(aggregated_df):
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

        for i, config in enumerate(configurations):
            config_data = benchmark_data[benchmark_data['configuration'] == config]['mean_benchmark_time']
            data.append(config_data.values)
            colors_list.append(colors[config])
            labels.append("Non-\nInstrumented" if config == "non-instrumented" else config.capitalize())

        # Create the boxplot
        box = ax.boxplot(data, labels=labels, patch_artist=True, medianprops=dict(color='black'), showfliers=False)

        # Set colors for the boxes
        for patch, color in zip(box['boxes'], colors_list):
            patch.set_facecolor(color)

        # Annotate median values
        for j, config_data in enumerate(data):
            annotate_median(ax, pd.Series(config_data), j + 1, 0.35)  # position is 1-based, endpoint is 0.35

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
    plt.savefig('all_benchmarks_performance_impact.png', bbox_inches='tight')

    # plt.show()



def create_boxplot(times_data_python, times_data_nodejs, time_metric='benchmark_time'):
    """
    Creates a boxplot comparing Python and Node.js results for the specified time metric.

    Parameters:
    - times_data_python: DataFrame containing parsed results for Python.
    - times_data_nodejs: DataFrame containing parsed results for Node.js.
    - time_metric: str, either 'benchmark_time' or 'client_time' to specify which metric to plot.
    """
    # Check that the time_metric is valid
    if time_metric not in ['benchmark_time', 'client_time']:
        raise ValueError("Invalid time metric. Choose either 'benchmark_time' or 'client_time'.")

    python_data = times_data_python[time_metric].dropna()
    nodejs_data = times_data_nodejs[time_metric].dropna()

    plt.figure(figsize=(12, 6))
    plt.boxplot([python_data, nodejs_data], labels=['Python', 'Node.js'], showfliers=False)
    plt.title(f'Comparison of {time_metric.replace("_", " ").title()} for Python and Node.js')
    plt.ylabel(f'{time_metric.replace("_", " ").title()} (ms)')
    plt.xlabel('Language')
    plt.grid(True, linestyle='--', linewidth=0.5)

    plt.tight_layout()
    plt.savefig('python_nodejs_comparison.pdf', bbox_inches='tight')

    # plt.show()


def create_violin_plot(times_data_python, times_data_nodejs, time_metric='benchmark_time'):
    """
    Creates a violin plot comparing Python and Node.js results for the specified time metric.

    Parameters:
    - times_data_python: DataFrame containing parsed results for Python.
    - times_data_nodejs: DataFrame containing parsed results for Node.js.
    - time_metric: str, either 'benchmark_time' or 'client_time' to specify which metric to plot.
    """
    # Check that the time_metric is valid
    if time_metric not in ['benchmark_time', 'client_time']:
        raise ValueError("Invalid time metric. Choose either 'benchmark_time' or 'client_time'.")

    # Extract the relevant data
    python_data = times_data_python[time_metric].dropna()
    nodejs_data = times_data_nodejs[time_metric].dropna()

    # Create the violin plot
    plt.figure(figsize=(12, 6))
    plt.violinplot([python_data, nodejs_data], showmeans=True, showmedians=True)

    # Setting x-ticks and labels
    plt.xticks([1, 2], ['Python', 'Node.js'])
    plt.title(f'Comparison of {time_metric.replace("_", " ").title()} for Python and Node.js')
    plt.ylabel(f'{time_metric.replace("_", " ").title()} (ms)')
    plt.xlabel('Language')
    plt.grid(True, linestyle='--', linewidth=0.5)

    # Show the plot
    plt.tight_layout()
    plt.savefig('python_nodejs_comparison_violin.pdf', bbox_inches='tight')

    # plt.show()


def create_instrumentation_comparison_boxplot(times_data, language='Python', time_metric='benchmark_time'):
    """
    Creates a boxplot comparing instrumented and non-instrumented configurations for a specified language.

    Parameters:
    - times_data: DataFrame containing parsed results for both Python and Node.js.
    - language: str, the programming language to filter by (e.g., 'Python' or 'Node.js').
    - time_metric: str, either 'benchmark_time' or 'client_time' to specify which metric to plot.
    """
    # Check that the time_metric is valid
    if time_metric not in ['benchmark_time', 'client_time']:
        raise ValueError("Invalid time metric. Choose either 'benchmark_time' or 'client_time'.")

    # Filter data for the specified language
    filtered_data = times_data[times_data['language'] == language]

    # Separate instrumented and non-instrumented data
    instrumented_data = filtered_data[filtered_data['configuration'] == 'instrumented'][time_metric].dropna()
    non_instrumented_data = filtered_data[filtered_data['configuration'] == 'non-instrumented'][time_metric].dropna()

    # Create the boxplot
    plt.figure(figsize=(12, 6))
    plt.boxplot([instrumented_data, non_instrumented_data], labels=['Instrumented', 'Non-Instrumented'], showfliers=False)
    plt.title(f'{language} - Comparison of {time_metric.replace("_", " ").title()} (Instrumented vs Non-Instrumented)')
    plt.ylabel(f'{time_metric.replace("_", " ").title()} (ms)')
    plt.xlabel('Configuration')
    plt.grid(True, linestyle='--', linewidth=0.5)

    # Show the plot
    plt.tight_layout()
    plt.savefig(f'{language}_instrumentation_comparison_plot.pdf', bbox_inches='tight')


def create_strip_plot(times_data, time_metric='benchmark_time'):
    """
    Creates a strip plot comparing overhead for Python and Node.js across instrumented and non-instrumented configurations.

    Parameters:
    - times_data: DataFrame containing parsed results for both Python and Node.js.
    - time_metric: str, either 'benchmark_time' or 'client_time' to specify which metric to plot.
    """
    # Check that the time_metric is valid
    if time_metric not in ['benchmark_time', 'client_time']:
        raise ValueError("Invalid time metric. Choose either 'benchmark_time' or 'client_time'.")

    # Define the configurations for plotting
    configurations = [
        ('Python', 'instrumented'),
        ('Python', 'non-instrumented'),
        ('Node.js', 'instrumented'),
        ('Node.js', 'non-instrumented')
    ]

    # Create lists to hold the plot data
    plot_data = []
    labels = []

    # Prepare the data for each configuration
    for language, config in configurations:
        # Filter the data for the specific language and configuration
        data = times_data[(times_data['language'] == language) & (times_data['configuration'] == config)][
            time_metric].dropna()
        plot_data.append(data)
        labels.append(f'{language} {config.capitalize()}')

    # Create the strip plot with jitter
    plt.figure(figsize=(14, 7))
    for i, data in enumerate(plot_data):
        # Apply jitter to the x-axis position
        jitter = np.random.uniform(-0.1, 0.1, size=len(data))
        plt.scatter(np.full(len(data), i + 1) + jitter, data, alpha=0.6)

    # Customize the plot
    plt.xticks(range(1, len(labels) + 1), labels, rotation=45)
    plt.title(f'Comparison of {time_metric.replace("_", " ").title()} Across Configurations')
    plt.ylabel(f'{time_metric.replace("_", " ").title()} (ms)')
    plt.xlabel('Language and Configuration')
    plt.grid(axis='y', linestyle='--', linewidth=0.5)

    # Show the plot
    plt.tight_layout()
    # plt.show()



def plot_all_benchmarks_together_violin(aggregated_df):
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

        for i, config in enumerate(configurations):
            config_data = benchmark_data[benchmark_data['configuration'] == config]['mean_benchmark_time']
            data.append(config_data.values)
            colors_list.append(colors[config])
            labels.append("Non-\nInstrumented" if config == "non-instrumented" else config.capitalize())

        # Plot violin plots
        violin = ax.violinplot(data, showmeans=False, showmedians=True)

        # Set colors for the violins
        for i, body in enumerate(violin['bodies']):
            body.set_facecolor(colors_list[i])
            body.set_edgecolor('black')
            body.set_alpha(0.7)

        # Customize the median line color
        violin['cmedians'].set_color('black')
        violin['cmedians'].set_linewidth(2)

        # Annotate median values
        for j, config_data in enumerate(data):
            annotate_median(ax, pd.Series(config_data), j + 1, 0.35)  # position is 1-based, endpoint is 0.35

        ax.set_title(f'{benchmark}', fontsize=18)
        ax.yaxis.grid(True, linestyle='--', which='both', color='gray', alpha=0.7)
        ax.set_axisbelow(True)
        ax.set_xticks([1, 2])
        ax.set_xticklabels(labels)

    # Adjust the layout
    plt.tight_layout(rect=[0.03, 0.05, 1, 0.95])

    # Add the global labels
    fig.text(0.5, 0.04, 'Configuration', ha='center', fontsize=22)
    fig.text(0.12, 0.5, 'Mean Benchmark Time (ms)', va='center', rotation='vertical', fontsize=22)

    # Save the figure as a PDF
    plt.savefig('all_benchmarks_performance_violin_impact.pdf', bbox_inches='tight')
    plt.savefig('all_benchmarks_performance_violin_impact.png', bbox_inches='tight')
    # plt.show()

# Example usage
benchmark_df_python = parse_all_json_files(PYTHON_DIR)
benchmark_df_python['language'] = 'Python'

benchmark_df_nodejs = parse_all_json_files(NODEJS_DIR)
benchmark_df_nodejs['language'] = 'Node.js'
benchmark_df = pd.concat([benchmark_df_python, benchmark_df_nodejs], ignore_index=True)

aggregated_df = aggregate_benchmark_data(benchmark_df)

plot_all_benchmarks_together(aggregated_df)
plot_all_benchmarks_together_violin(aggregated_df)

create_boxplot(benchmark_df_python, benchmark_df_nodejs, time_metric='benchmark_time')
create_violin_plot(benchmark_df_python, benchmark_df_nodejs, time_metric='benchmark_time')

create_instrumentation_comparison_boxplot(benchmark_df_python, language='Python', time_metric='benchmark_time')
create_instrumentation_comparison_boxplot(benchmark_df_nodejs, language='Node.js', time_metric='benchmark_time')

times_data = pd.concat([benchmark_df_python, benchmark_df_nodejs], ignore_index=True)
create_strip_plot(times_data)

# create_boxplot(benchmark_df_python, benchmark_df_nodejs, time_metric='client_time')
