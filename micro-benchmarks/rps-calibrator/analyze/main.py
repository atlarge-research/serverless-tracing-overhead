import pandas as pd
import matplotlib.pyplot as plt

PLOT_DIR = "plots"

def main():
    file_path = "../results/rps_calibration_results.csv"

    stats = calculate_targetRPS_stats(file_path)
    print(stats)
    # plot_targetRPS_stats_error_bars(file_path)
    # plot_targetRPS_per_language(file_path)

    table, overall = calculate_differences(file_path)
    print(table)
    print(overall)

    table = generate_aggregated_http_req_duration_stats_endpoint_variation(file_path)

    # Compare the Throughput vs Standard, Otel and Elastic APM.

    # Calculate the Average of the five runs
    # Also Min
    # Also Max


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
    variation_colors = {
        'standard': '#1f77b4',  # blue
        'otel': '#ff7f0e',      # orange
        'elastic': '#2ca02c'    # green
    }
    error_colors = {
        'standard': '#1f77b4',  # blue
        'otel': '#ff7f0e',      # orange
        'elastic': '#2ca02c'    # green
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
            # ax.set_title(f'{lang.title()} - {endpoint.title()}', fontsize=14)
            ax.set_xticks(positions)
            ax.set_xticklabels([label_mapping[var] for var in variations], rotation=45, ha='right', fontsize=10)
            ax.set_xlabel('Applications', fontsize=12)
            ax.set_ylabel('Requests per Second', fontsize=12)

            # Add legend
            # ax.legend(loc='upper right', fontsize=10)

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
    variation_colors = {
        'standard': '#1f77b4',  # blue
        'otel': '#ff7f0e',  # orange
        'elastic': '#2ca02c'  # green
    }
    error_colors = {
        'standard': '#1f77b4',  # blue
        'otel': '#ff7f0e',  # orange
        'elastic': '#2ca02c'  # green
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
        # fig.suptitle(f'Target RPS by Endpoint and Configuration for {lang.title()}', fontsize=16)

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
            # ax.set_title(f'{endpoint.title()} Endpoint', fontsize=14)
            ax.set_xticks(positions)
            ax.set_xticklabels([label_mapping[var] for var in variations], rotation=45, ha='right', fontsize=10)
            ax.set_xlabel('Applications', fontsize=12)
            ax.set_ylabel('Requests per Second', fontsize=12)

            # Add legend
            # ax.legend(loc='upper right', fontsize=10)

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
    pivot_table = average_rps.pivot_table(index=['language', 'endpoint'], columns='configuration', values='targetRPS').reset_index()

    # Calculate the differences between instrumented (otel and elastic) and non-instrumented (standard)
    pivot_table['otel_vs_standard'] = ((pivot_table['otel'] - pivot_table['standard']) / pivot_table['standard']) * 100
    pivot_table['elastic_vs_standard'] = ((pivot_table['elastic'] - pivot_table['standard']) / pivot_table['standard']) * 100
    pivot_table['otel_vs_elastic'] = ((pivot_table['otel'] - pivot_table['elastic']) / pivot_table['elastic']) * 100

    # Calculate the overall differences across all endpoints
    overall = pivot_table.groupby('language')[['otel', 'elastic', 'standard']].mean().reset_index()
    overall['otel_vs_standard'] = ((overall['otel'] - overall['standard']) / overall['standard']) * 100
    overall['elastic_vs_standard'] = ((overall['elastic'] - overall['standard']) / overall['standard']) * 100
    overall['otel_vs_elastic'] = ((overall['otel'] - overall['elastic']) / overall['elastic']) * 100

    return pivot_table, overall

# def plot(file_path):
#     # Load the data
#     df = pd.read_csv(file_path)
#
#     # Calculate averages
#     avg_standard = df[df['configuration'] == 'standard'].groupby('endpoint')['targetRPS'].mean()
#     avg_otel = df[df['configuration'] == 'otel'].groupby('endpoint')['targetRPS'].mean()
#     avg_elastic = df[df['configuration'] == 'elastic'].groupby('endpoint')['targetRPS'].mean()
#
#     # Calculate percentage differences
#     otel_vs_standard = ((avg_otel - avg_standard) / avg_standard * 100).to_dict()
#     elastic_vs_standard = ((avg_elastic - avg_standard) / avg_standard * 100).to_dict()
#     otel_vs_elastic = ((avg_otel - avg_elastic) / avg_elastic * 100).to_dict()
#
#     # Prepare data for plotting
#     data = {
#         'Endpoint': list(otel_vs_standard.keys()),
#         'Otel vs Standard (%)': list(otel_vs_standard.values()),
#         'Elastic vs Standard (%)': list(elastic_vs_standard.values()),
#         'Otel vs Elastic (%)': list(otel_vs_elastic.values())
#     }
#     plot_df = pd.DataFrame(data)
#
#     # Plotting
#     fig, axes = plt.subplots(3, 1, figsize=(14, 18))
#
#     # Otel vs Standard
#     plot_df.plot(kind='bar', x='Endpoint', y='Otel vs Standard (%)', ax=axes[0], color='blue', legend=False)
#     axes[0].set_title('Otel vs Standard (%)')
#     axes[0].set_ylabel('Percentage Difference')
#     axes[0].grid(True, linestyle='--', alpha=0.7)
#
#     # Elastic vs Standard
#     plot_df.plot(kind='bar', x='Endpoint', y='Elastic vs Standard (%)', ax=axes[1], color='orange', legend=False)
#     axes[1].set_title('Elastic vs Standard (%)')
#     axes[1].set_ylabel('Percentage Difference')
#     axes[1].grid(True, linestyle='--', alpha=0.7)
#
#     # Otel vs Elastic
#     plot_df.plot(kind='bar', x='Endpoint', y='Otel vs Elastic (%)', ax=axes[2], color='green', legend=False)
#     axes[2].set_title('Otel vs Elastic (%)')
#     axes[2].set_ylabel('Percentage Difference')
#     axes[2].grid(True, linestyle='--', alpha=0.7)
#
#     plt.tight_layout()
#     # plt.show()
#
#     plt.savefig('output.png')



if __name__ == '__main__':
    main()