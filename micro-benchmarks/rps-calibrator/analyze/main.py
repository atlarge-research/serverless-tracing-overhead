import pandas as pd
import matplotlib.pyplot as plt

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

    table, overall = calculate_differences(file_path)
    print(table)
    print(overall)

    # Compare the Throughput vs Standard, Otel and Elastic APM.

    # Calculate the Average of the five runs
    # Also Min
    # Also Max


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
    plot_filename = 'aggregated_RPS_across_endpoints.png'
    plt.savefig(plot_filename)
    plt.close(fig)


def plot_aggregated_RPS_across_variations(file_path):
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

    # Plot the error bars
    for pos, avg, min_val, max_val, var in zip(positions, avg_rps, min_rps, max_rps, variations):
        ax.errorbar(pos, avg, yerr=[[avg - min_val], [max_val - avg]], fmt='o', capsize=5,
                    color='black', ecolor=error_colors[var], elinewidth=2, markeredgewidth=2)

        # Determine text alignment and position
        if var in ['standard', 'otel']:
            ha = 'left'
            text_x = pos + 0.05  # Slightly to the right
        else:
            ha = 'right'
            text_x = pos - 0.05  # Slightly to the left

        # Add annotation for average RPS
        ax.text(text_x, avg, f'{avg:.2f}', ha=ha, va='center', fontsize=10, color='black',
                bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))

        # Add annotation for min and max RPS
        ax.text(text_x, min_val, f'{min_val:.2f}', ha=ha, va='center', fontsize=10, color='black',
                bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))
        ax.text(text_x, max_val, f'{max_val:.2f}', ha=ha, va='center', fontsize=10, color='black',
                bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))

    # Labeling
    # ax.set_title('Aggregated RPS Across Variations')
    ax.set_xticks(positions)
    ax.set_xticklabels([label_mapping[var] for var in variations], rotation=45, ha='right')
    ax.set_xlabel('Variations')
    ax.set_ylabel('Requests per Second')

    # Add grid
    ax.grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()

    # Save plot as PNG file
    plot_filename = 'aggregated_RPS_across_variations.png'
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
    plot_filename = 'aggregated_RPS_across_variations_horizontal.png'
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
            plot_filename = f'{PLOT_DIR}/{lang}_{endpoint}_targetRPS.png'
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
        plot_filename = f'{PLOT_DIR}/{lang}_All_targetRPS.png'
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
