import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

PLOT_DIR = "plots"

plt.rcParams.update({'font.size': 18})


def main():
    file_path = "../results/rps_calibration_results.csv"

    stats = calculate_targetRPS_stats(file_path)
    print(stats)
    plot_targetRPS_stats_error_bars(file_path)
    plot_targetRPS_per_language(file_path)

    plot_aggregated_RPS_across_variations(file_path)
    plot_aggregated_RPS_across_variations_horizontal(file_path)
    plot_aggregated_RPS_across_endpoints(file_path)

    pivot_table, overall = calculate_differences(file_path)
    print(pivot_table)
    print("LANGUAGE COMPARISON OVERALL")
    print(overall)

    plot_language_comparison_boxplot(file_path, "standard")
    plot_language_comparison_boxplot(file_path, "elastic")
    plot_language_comparison_boxplot(file_path, "otel")

    plot_configuration_comparison_boxplot(file_path, "python")
    plot_configuration_comparison_boxplot(file_path, "go")
    plot_configuration_comparison_boxplot(file_path, "java")

    plot_mean_barplot(file_path, "python")
    plot_mean_barplot(file_path, "go")
    plot_mean_barplot(file_path, "java")

    # Compare the Throughput vs Standard, Otel and Elastic APM.

    # Calculate the Average of the five runs
    # Also Min
    # Also Max


def plot_mean_barplot(file_path, language):
    # Load the data
    data = pd.read_csv(file_path)

    # Filter the data for the selected language and configurations (standard, otel, elastic)
    filtered_data = data[(data['language'] == language) & (data['configuration'].isin(['standard', 'otel', 'elastic']))]

    # Ensure the configurations are in the desired order
    order = ['standard', 'otel', 'elastic']
    filtered_data['configuration'] = pd.Categorical(filtered_data['configuration'], categories=order, ordered=True)

    # Define label mapping and colors
    label_mapping = {'standard': 'Standard', 'otel': 'OpenTelemetry', 'elastic': 'Elastic APM'}
    colors = ['lightblue', 'lightcoral', 'lightgreen']
    color_mapping = dict(zip(order, colors))

    # Calculate means and standard deviations
    means = [np.mean(filtered_data[filtered_data['configuration'] == config]['targetRPS'].dropna()) for config in order]
    std_devs = [np.std(filtered_data[filtered_data['configuration'] == config]['targetRPS'].dropna()) for config in order]

    # Create the bar plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar([label_mapping[config] for config in order], means, yerr=std_devs, color=colors, capsize=5)

    # Add annotations for mean values
    for i, mean_val in enumerate(means):
        ax.text(i, mean_val + 0.05 * max(means), f'{mean_val:.2f}', ha='center', va='bottom', fontsize=12)

    # Customize the plot
    ax.set_ylabel('Requests per Second', fontsize=12)
    ax.set_title(f'Mean Target RPS for {language.capitalize()} by Configuration', fontsize=14)

    # Add grid
    ax.yaxis.grid(True, linestyle='--', which='major', color='grey', alpha=0.5)

    # Adjust layout
    plt.tight_layout()

    # Save the plot as a file
    output_file = f'mean_barplot_{language}.pdf'
    plt.savefig(output_file)
    plt.close(fig)

def plot_configuration_comparison_boxplot(file_path, language):
    data = pd.read_csv(file_path)

    filtered_data = data[(data['language'] == language) & (data['configuration'].isin(['standard', 'otel', 'elastic']))]

    order = ['standard', 'otel', 'elastic']
    filtered_data['configuration'] = pd.Categorical(filtered_data['configuration'], categories=order, ordered=True)
    filtered_data = filtered_data.sort_values('configuration')

    label_mapping = {
        'standard': 'Standard',
        'otel': 'OpenTelemetry',
        'elastic': 'Elastic APM'
    }

    colors = ['lightblue', 'lightcoral', 'lightgreen']
    color_mapping = dict(zip(order, colors))

    fig, ax = plt.subplots(figsize=(9, 6))

    box_data = [filtered_data[filtered_data['configuration'] == config]['targetRPS'].dropna() for config in order]
    box = ax.boxplot(box_data, labels=[label_mapping[config] for config in order], patch_artist=True, showfliers=False, widths=(0.2))

    for patch, config in zip(box['boxes'], order):
        patch.set_facecolor(color_mapping[config])
        patch.set_edgecolor('black')

    for median in box['medians']:
        median.set_color('black')
        median.set_linewidth(2)


    for i, config in enumerate(order):
        data = filtered_data[filtered_data['configuration'] == config]['targetRPS'].dropna()
        min_val = data.min()
        max_val = data.max()
        median_val = data.median()

        annotation_fontsize = 12

        # Add annotation for median
        ax.text(i + 1.14, median_val, f'{median_val:.2f}', va='center', fontsize=annotation_fontsize, color='black',
                bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))

        # Lower extreme (min value)
        ax.text(i + 1.10, min_val, f'{min_val:.2f}', va='center', fontsize=annotation_fontsize, color='black',
                bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))
        offset = 0
        if language == "python" and config == "elastic":
            offset = -60
        # Upper extreme (max value)
        ax.text(i + 1.10, max_val + offset, f'{max_val:.2f}', va='center', fontsize=annotation_fontsize, color='black',
                bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))

    ax.set_ylabel('Requests per Second', fontsize=22)

    ax.set_title(f'{language.title()}')

    ax.yaxis.grid(True, linestyle='--', which='major', color='grey', alpha=0.5)

    plt.tight_layout()

    output_file = f'configuration_comparison_{language}_boxplot.pdf'
    plt.savefig(output_file)
    plt.close(fig)

def plot_language_comparison_boxplot(file_path, configuration):
    # Load the data
    data = pd.read_csv(file_path)

    # Filter the data for the selected configuration and Python, Java, and Go only
    filtered_data = data[(data['language'].isin(['python', 'java', 'go'])) & (data['configuration'] == configuration)]

    # Create separate lists for Python, Java, and Go targetRPS values
    python_data = filtered_data[filtered_data['language'] == 'python']['targetRPS'].dropna().tolist()
    java_data = filtered_data[filtered_data['language'] == 'java']['targetRPS'].dropna().tolist()
    go_data = filtered_data[filtered_data['language'] == 'go']['targetRPS'].dropna().tolist()

    # Organize the data into a list for the boxplot
    data_to_plot = [python_data, java_data, go_data]

    # Set up the matplotlib figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # Create the boxplot
    ax.boxplot(data_to_plot, labels=['Python', 'Java', 'Go'])

    # Add plot title and labels
    ax.set_title(f'Comparison of Target RPS between Python, Java, and Go ({configuration})')
    ax.set_xlabel('Language')
    ax.set_ylabel('Target RPS')

    # Save the plot as a file
    plt.tight_layout()
    output_file = f"language_comparison_{configuration}_boxplot.pdf"
    plt.savefig(output_file)
    plt.close()


def plot_aggregated_RPS_across_endpoints(file_path):
    # Calculate statistics
    stats_df = calculate_targetRPS_stats(file_path)

    # Ensure the configurations are in the desired order
    order = ['standard', 'otel', 'elastic']
    stats_df['Configuration'] = pd.Categorical(stats_df['Configuration'], categories=order, ordered=True)
    stats_df = stats_df.sort_values('Configuration')

    # Define colors for each variation and error bars
    error_colors = {
        'standard': 'lightblue',  # blue
        'otel': 'lightcoral',  # orange
        'elastic': 'lightgreen'  # green
    }
    error_colors = {
        'standard': 'lightblue',  # blue
        'otel': 'lightcoral',  # orange
        'elastic': 'lightgreen'  # green
    }

    # Define label mapping
    label_mapping = {
        'standard': 'Standard',
        'otel': 'OpenTelemetry',
        'elastic': 'Elastic APM'
    }

    # Get unique endpoints
    endpoints = stats_df['Endpoint'].unique()

    # Create a figure with 4 subplots
    fig, axs = plt.subplots(2, 2, figsize=(16, 12))
    axs = axs.flatten()

    # Iterate over each endpoint to create subplots
    for ax, endpoint in zip(axs, endpoints):
        # Filter the statistics for the current endpoint
        subset = stats_df[stats_df['Endpoint'] == endpoint]

        # Aggregate the statistics by Configuration (Variation)
        aggregated_stats = subset.groupby('Configuration').agg({
            'Average Target RPS': 'mean',
            'Min Target RPS': 'min',
            'Max Target RPS': 'max'
        }).reset_index()

        # Plot the error bars for average, min, and max target RPS
        variations = aggregated_stats['Configuration'].tolist()
        avg_rps = aggregated_stats['Average Target RPS'].tolist()
        min_rps = aggregated_stats['Min Target RPS'].tolist()
        max_rps = aggregated_stats['Max Target RPS'].tolist()
        positions = range(len(variations))

        # Plot the error bars horizontally
        for pos, avg, min_val, max_val, var in zip(positions, avg_rps, min_rps, max_rps, variations):
            ax.errorbar(avg, pos, xerr=[[avg - min_val], [max_val - avg]], fmt='o', capsize=5,
                        color='black', ecolor=error_colors[var], elinewidth=2, markeredgewidth=2)

        # Labeling
        ax.set_title(f'{endpoint.title()} Endpoint')
        ax.set_yticks(positions)
        ax.set_yticklabels([label_mapping[var] for var in variations])
        ax.set_ylabel('Configuration')
        ax.set_xlabel('Requests per Second')

        # Add grid
        ax.grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()

    # Save plot as PNG file
    plot_filename = 'aggregated_RPS_across_endpoints.pdf'
    plt.savefig(plot_filename)
    plt.close(fig)


def plot_aggregated_RPS_across_variations(file_path):
    # Calculate statistics
    stats_df = calculate_targetRPS_stats(file_path)

    # Ensure the configurations are in the desired order
    order = ['standard', 'otel', 'elastic']
    stats_df['Configuration'] = pd.Categorical(stats_df['Configuration'], categories=order, ordered=True)
    stats_df = stats_df.sort_values('Configuration')

    # Define label mapping
    label_mapping = {
        'standard': 'Non-\nInstrumented',
        'otel': 'OpenTelemetry\nInstrumented',
        'elastic': 'Elastic APM\nInstrumented'
    }

    # Define colors for each configuration
    colors = ['lightblue', 'lightcoral', 'lightgreen']
    color_mapping = dict(zip(order, colors))

    # Create a figure for the boxplot
    fig, ax = plt.subplots(figsize=(10, 6))

    # Create the boxplot
    box_data = [stats_df[stats_df['Configuration'] == config]['Average Target RPS'] for config in order]
    box = ax.boxplot(box_data, labels=[label_mapping[config] for config in order], patch_artist=True, showfliers=True,
                     widths=(0.2))

    # Color the boxes
    for patch, config in zip(box['boxes'], order):
        patch.set_facecolor(color_mapping[config])
        patch.set_edgecolor('black')

    # Color the median lines
    for median in box['medians']:
        median.set_color('black')
        median.set_linewidth(2)

    # Add annotations for min, max, median, and upper whisker values
    for i, config in enumerate(order):
        data = stats_df[stats_df['Configuration'] == config]['Average Target RPS']
        min_val = data.min()
        max_val = data.max()
        median_val = data.median()
        upper_whisker_val = [item.get_ydata()[1] for item in box['whiskers']][i * 2 + 1]

        annotation_fontsize = 14
        # Add annotation for min
        min_vertical_adjustment = 40
        ax.text(i + 1.10, min_val - min_vertical_adjustment, f'{min_val:.2f}', va='center', fontsize=annotation_fontsize, color='black',
                bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))

        # Add annotation for max
        max_vertical_adjustment = 200 if config == 'elastic' else 0
        ax.text(i + 0.66, max_val + max_vertical_adjustment, f'{max_val:.2f}', va='center',
                fontsize=annotation_fontsize, color='black',
                bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))

        # Add annotation for median
        median_vertical_adjustment = 100
        ax.text(i + 0.6, median_val + median_vertical_adjustment, f'{median_val:.2f}', va='center', fontsize=annotation_fontsize,
                color='black',
                bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))

        # Upper whisker
        uw_vertical_adjustment = -100
        ax.text(i + 1.10, upper_whisker_val + uw_vertical_adjustment, f'{upper_whisker_val:.2f}', va='center', fontsize=annotation_fontsize,
                color='black',
                bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))

    # ax.set_xlabel('Variations')
    ax.set_ylabel('Requests per Second', fontsize=22)

    # Add grid
    ax.yaxis.grid(True, linestyle='--', which='major', color='grey', alpha=0.5)

    # plt.tight_layout()

    # Save plot as PNG file
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plot_filename = 'aggregated_RPS_across_variations_boxplot.pdf'
    plt.savefig(plot_filename)
    plt.close(fig)


def plot_aggregated_RPS_across_variations_horizontal(file_path):
    # Calculate statistics
    stats_df = calculate_targetRPS_stats(file_path)

    # Ensure the configurations are in the desired order
    order = ['standard', 'otel', 'elastic']
    stats_df['Configuration'] = pd.Categorical(stats_df['Configuration'], categories=order, ordered=True)
    stats_df = stats_df.sort_values('Configuration')

    # Aggregate the statistics by Configuration (Variation)
    aggregated_stats = stats_df.groupby('Configuration').agg({
        'Average Target RPS': 'mean',
        'Min Target RPS': 'min',
        'Max Target RPS': 'max'
    }).reset_index()

    # Define colors for each variation and error bars
    variation_colors = {
        'standard': '#1f77b4',  # blue
        'otel': '#ff7f0e',  # orange
        'elastic': '#2ca02c'  # green
    }
    error_colors = {
        'standard': 'lightblue',  # blue
        'otel': 'lightcoral',  # orange
        'elastic': 'lightgreen'  # green
    }

    # Define label mapping
    label_mapping = {
        'standard': 'Standard',
        'otel': 'OpenTelemetry',
        'elastic': 'Elastic APM'
    }

    # Create a figure for the aggregated RPS across variations
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot the error bars for average, min, and max target RPS
    variations = aggregated_stats['Configuration'].tolist()
    avg_rps = aggregated_stats['Average Target RPS'].tolist()
    min_rps = aggregated_stats['Min Target RPS'].tolist()
    max_rps = aggregated_stats['Max Target RPS'].tolist()
    positions = range(len(variations))

    # Plot the error bars horizontally
    for pos, avg, min_val, max_val, var in zip(positions, avg_rps, min_rps, max_rps, variations):
        ax.errorbar(avg, pos, xerr=[[avg - min_val], [max_val - avg]], fmt='o', capsize=5,
                    color='black', ecolor=error_colors[var], elinewidth=2, markeredgewidth=2)

    # Labeling
    # ax.set_title('Aggregated RPS Across Variations')
    ax.set_yticks(positions)
    ax.set_yticklabels([label_mapping[var] for var in variations])
    ax.set_ylabel('Variations')
    ax.set_xlabel('Requests per Second')

    # Add grid
    ax.grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()

    # Save plot as PNG file
    plot_filename = 'aggregated_RPS_across_variations_horizontal.pdf'
    plt.savefig(plot_filename)
    plt.close(fig)


def plot_targetRPS_stats_error_bars(file_path):
    # Calculate statistics
    stats_df = calculate_targetRPS_stats(file_path)

    # Ensure the configurations are in the desired order
    order = ['standard', 'otel', 'elastic']
    stats_df['Configuration'] = pd.Categorical(stats_df['Configuration'], categories=order, ordered=True)
    stats_df = stats_df.sort_values('Configuration')

    # Get unique languages and endpoints
    languages = stats_df['Language'].unique()
    endpoints = stats_df['Endpoint'].unique()

    # Define colors for each variation and error bars
    error_colors = {
        'standard': 'lightblue',  # blue
        'otel': 'lightcoral',  # orange
        'elastic': 'lightgreen'  # green
    }
    error_colors = {
        'standard': 'lightblue',  # blue
        'otel': 'lightcoral',  # orange
        'elastic': 'lightgreen'  # green

    }

    # Define label mapping
    label_mapping = {
        'standard': 'Standard',
        'otel': 'OpenTelemetry',
        'elastic': 'Elastic APM'
    }

    # Iterate over each language and endpoint to create separate plots
    for lang in languages:
        for endpoint in endpoints:
            subset = stats_df[(stats_df['Language'] == lang) & (stats_df['Endpoint'] == endpoint)]

            if subset.empty:
                continue

            # Set up the figure and axis
            fig, ax = plt.subplots(figsize=(8, 6))

            # Plot the error bars for average, min, and max targetRPS
            variations = subset['Configuration'].tolist()
            avg_rps = subset['Average Target RPS'].tolist()
            min_rps = subset['Min Target RPS'].tolist()
            max_rps = subset['Max Target RPS'].tolist()
            positions = range(len(variations))

            # Plot the error bars
            for pos, avg, min_val, max_val, var in zip(positions, avg_rps, min_rps, max_rps, variations):
                ax.errorbar(pos, avg, yerr=[[avg - min_val], [max_val - avg]], fmt='o', capsize=5,
                            color='black', ecolor=error_colors[var], elinewidth=2, markeredgewidth=2)

            # Labeling
            # ax.set_title(f'{lang.title()} - {endpoint.title()}')
            ax.set_xticks(positions)
            ax.set_xticklabels([label_mapping[var] for var in variations], rotation=45, ha='right')
            ax.set_xlabel('Applications')
            ax.set_ylabel('Requests per Second')

            # Add legend
            # ax.legend(loc='upper right')

            # Improve overall plot aesthetics
            ax.grid(True, linestyle='--', alpha=0.6)
            plt.tight_layout()

            # Save plot as PNG file
            plot_filename = f'{PLOT_DIR}/{lang}_{endpoint}_targetRPS.pdf'
            plt.savefig(plot_filename)
            plt.close(fig)


def plot_targetRPS_per_language(file_path):
    # Calculate statistics
    stats_df = calculate_targetRPS_stats(file_path)

    # Ensure the configurations are in the desired order
    order = ['standard', 'otel', 'elastic']
    stats_df['Configuration'] = pd.Categorical(stats_df['Configuration'], categories=order, ordered=True)
    stats_df = stats_df.sort_values('Configuration')

    # Get unique endpoints and languages
    endpoints = stats_df['Endpoint'].unique()
    languages = stats_df['Language'].unique()

    # Define colors for each variation and error bars
    error_colors = {
        'standard': 'lightblue',  # blue
        'otel': 'lightcoral',  # orange
        'elastic': 'lightgreen'  # green
    }

    error_colors = {
        'standard': 'lightblue',  # blue
        'otel': 'lightcoral',  # orange
        'elastic': 'lightgreen'  # green

    }

    # Define label mapping
    label_mapping = {
        'standard': 'Standard',
        'otel': 'OpenTelemetry',
        'elastic': 'Elastic APM'
    }

    # Iterate over each language to create separate figures
    for lang in languages:
        # Set up the figure with 2x2 subplots
        fig, axs = plt.subplots(2, 2, figsize=(15, 12))
        # fig.suptitle(f'Target RPS by Endpoint and Configuration for {lang.title()}')

        # Iterate over each endpoint and subplot position
        for idx, endpoint in enumerate(endpoints):
            ax = axs[idx // 2, idx % 2]

            subset = stats_df[(stats_df['Language'] == lang) & (stats_df['Endpoint'] == endpoint)]

            if subset.empty:
                continue

            # Plot the error bars for average, min, and max targetRPS
            variations = subset['Configuration'].tolist()
            avg_rps = subset['Average Target RPS'].tolist()
            min_rps = subset['Min Target RPS'].tolist()
            max_rps = subset['Max Target RPS'].tolist()
            positions = range(len(variations))

            # Plot the error bars
            for pos, avg, min_val, max_val, var in zip(positions, avg_rps, min_rps, max_rps, variations):
                ax.errorbar(pos, avg, yerr=[[avg - min_val], [max_val - avg]], fmt='o', capsize=5,
                            color='black', ecolor=error_colors[var], elinewidth=2, markeredgewidth=2)

            # Labeling
            # ax.set_title(f'{endpoint.title()} Endpoint')
            ax.set_xticks(positions)
            ax.set_xticklabels([label_mapping[var] for var in variations], rotation=45, ha='right')
            ax.set_xlabel('Applications')
            ax.set_ylabel('Requests per Second')

            # Add legend
            # ax.legend(loc='upper right')

            # Improve overall plot aesthetics
            ax.grid(True, linestyle='--', alpha=0.6)

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])

        # Save plot as PNG file
        plot_filename = f'{PLOT_DIR}/{lang}_All_targetRPS.pdf'
        plt.savefig(plot_filename)
        plt.close(fig)


def calculate_targetRPS_stats(file_path):
    # Read the data from the CSV file
    data = pd.read_csv(file_path)

    # Ensure the necessary columns are present
    required_columns = ['language', 'configuration', 'endpoint', 'targetRPS']
    if not all(column in data.columns for column in required_columns):
        raise ValueError(f"Input file must contain the following columns: {', '.join(required_columns)}")

    # Group by language, configuration, and endpoint
    grouped_data = data.groupby(['language', 'configuration', 'endpoint'])

    # Calculate the average, min, and max targetRPS for each group
    stats = grouped_data['targetRPS'].agg(['mean', 'min', 'max']).reset_index()

    # Rename the columns for better readability
    stats.columns = ['Language', 'Configuration', 'Endpoint', 'Average Target RPS', 'Min Target RPS', 'Max Target RPS']

    return stats


def calculate_differences(file_path):
    # Load the data
    data = pd.read_csv(file_path)

    # Calculate the average RPS for each configuration and endpoint
    average_rps = data.groupby(['language', 'configuration', 'endpoint']).targetRPS.mean().reset_index()

    # Pivot the data to have configurations as columns
    pivot_table = average_rps.pivot_table(index=['language', 'endpoint'], columns='configuration',
                                          values='targetRPS').reset_index()

    # Calculate the differences between instrumented (otel and elastic) and non-instrumented (standard)
    pivot_table['otel_vs_standard'] = ((pivot_table['otel'] - pivot_table['standard']) / pivot_table['standard']) * 100
    pivot_table['elastic_vs_standard'] = ((pivot_table['elastic'] - pivot_table['standard']) / pivot_table[
        'standard']) * 100
    pivot_table['otel_vs_elastic'] = ((pivot_table['otel'] - pivot_table['elastic']) / pivot_table['elastic']) * 100

    # Calculate the overall differences across all endpoints
    overall = pivot_table.groupby('language')[['otel', 'elastic', 'standard']].mean().reset_index()
    overall['otel_vs_standard'] = ((overall['otel'] - overall['standard']) / overall['standard']) * 100
    overall['elastic_vs_standard'] = ((overall['elastic'] - overall['standard']) / overall['standard']) * 100
    overall['otel_vs_elastic'] = ((overall['otel'] - overall['elastic']) / overall['elastic']) * 100

    return pivot_table, overall


if __name__ == '__main__':
    main()
