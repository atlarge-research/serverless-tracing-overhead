import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({'font.size': 18})


def filter_http_req_duration_in_directory(input_directory, output_file):
    # Initialize an empty DataFrame to store the results
    all_filtered_data = pd.DataFrame()

    # Loop through each file in the input directory
    for filename in os.listdir(input_directory):
        if filename.endswith(".csv"):
            file_path = os.path.join(input_directory, filename)
            print(f"Processing file: {file_path}")

            # Read the CSV file
            df = pd.read_csv(file_path)

            # Filter the rows where 'metric_name' is 'http_req_duration'
            filtered_df = df[df['metric_name'] == 'http_req_duration']

            # Append the filtered data to the cumulative DataFrame
            all_filtered_data = pd.concat([all_filtered_data, filtered_df], ignore_index=True)

    # Write the combined filtered data to the output CSV file
    all_filtered_data.to_csv(output_file, index=False)
    print(f"All filtered data has been written to: {output_file}")


def get_scenarios(data, cpu_data):
    tags_dicts = []
    for extra_tags in data['extra_tags']:
        tag_dict = {}
        if isinstance(extra_tags, str):
            pairs = extra_tags.split('&')
            for pair in pairs:
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    tag_dict[key] = value
        tags_dicts.append(tag_dict)

    data['tags_dict'] = tags_dicts

    # Create a unique identifier based on 'testName', 'appName', 'rps', and 'endpoint'
    unique_ids = []
    for tag_dict in tags_dicts:
        unique_id = "_".join([
            tag_dict.get('testName', ''),
            tag_dict.get('appName', ''),
            tag_dict.get('rps', ''),
            tag_dict.get('endpoint', ''),
            tag_dict.get('language', ''),
        ])
        unique_ids.append(unique_id)

    data['unique_id'] = unique_ids

    # Find the first and last timestamp for each unique identifier
    test_times = data.groupby('unique_id')['timestamp'].agg(['min', 'max'])

    # Create a list of scenarios with relevant details
    scenarios = []
    for unique_id, times in test_times.iterrows():
        # Check if the unique_id is empty
        if unique_id == "____":
            continue
        components = unique_id.split('_')
        test_name, app_name, rps, endpoint, language = components

        # Find a matching container name based on 'appName'
        matching_container = cpu_data[cpu_data['Container'].str.contains(app_name, na=False)]

        # Determine the container name
        container_name = matching_container['Container'].iloc[0] if not matching_container.empty else "Unknown"

        # Create the scenario dictionary
        scenario = {
            "scenario_name": test_name,
            "start_time": times['min'],
            "end_time": times['max'],
            "test_duration": times['max'] - times['min'],
            "container_name": container_name,
            "app_name": app_name,
            "endpoint": endpoint,
            "rps": rps,
            "language": language
        }

        scenarios.append(scenario)
    return scenarios


def generate_http_req_duration_stats(df):
    # columns = ['Language', 'Variation', 'Endpoint', 'Average', 'Median', 'P90', 'P95', 'P99', 'Max', 'Min']

    tags = df['extra_tags'].str.split('&').apply(lambda x: dict(tag.split('=') for tag in x))
    df['language'] = tags.apply(lambda x: x.get('language'))
    df['testName'] = tags.apply(lambda x: x.get('testName'))
    df['endpoint'] = tags.apply(lambda x: x.get('endpoint'))
    df['variation'] = df['testName'].str.extract(r'(standard|elastic|otel)')

    summary = df.groupby(['language', 'variation', 'endpoint'])['metric_value'].agg(
        avg=lambda x: round(x.mean(), 2),
        med=lambda x: round(x.median(), 2),
        p95=lambda x: round(x.quantile(0.95), 2),
        p99=lambda x: round(x.quantile(0.99), 2)
    ).reset_index()

    return summary


def create_statistics_table_languages(df):
    tags = df['extra_tags'].str.split('&').apply(lambda x: dict(tag.split('=') for tag in x))
    df['language'] = tags.apply(lambda x: x.get('language'))
    df['testName'] = tags.apply(lambda x: x.get('testName'))
    df['endpoint'] = tags.apply(lambda x: x.get('endpoint'))
    df['variation'] = df['testName'].str.extract(r'(standard|elastic|otel)')

    # Define a helper function to calculate the statistics
    def calculate_statistics(data):
        return {
            'median': data.median(),
            'mean': data.mean(),
            # 'p90': data.quantile(0.90),
            'p95': data.quantile(0.95),
            'p99': data.quantile(0.99),
            # 'max': data.max(),
            # 'min': data.min()
        }

    # Initialize an empty list to store the results
    results = []
    print(df['language'].unique())

    # Iterate over each language
    for language in df['language'].unique():
        print(language)
        # Filter the dataframe for the current language
        df_lang = df[df['language'] == language]

        # Calculate statistics for each configuration
        stats_standard = calculate_statistics(df_lang[df_lang['variation'] == 'standard']['metric_value'])
        stats_elastic = calculate_statistics(df_lang[df_lang['variation'] == 'elastic']['metric_value'])
        stats_otel = calculate_statistics(df_lang[df_lang['variation'] == 'otel']['metric_value'])

        # Append the results to the list
        results.append(['Standard', language.capitalize(), stats_standard['median'], stats_standard['mean'],
                        stats_standard['p95'], stats_standard['p99']])
        results.append(
            ['Elastic', language.capitalize(),
             stats_elastic['median'],
             stats_elastic['mean'],
             stats_elastic['p95'],
             stats_elastic['p99']])
        results.append(['Otel', language.capitalize(), stats_otel['median'], stats_otel['mean'],
                        stats_otel['p95'], stats_otel['p99']])

    # Create a dataframe to display the results
    stats_df = pd.DataFrame(results,
                            columns=['Configuration', 'Language', 'Median', 'Mean', 'P95',
                                     'P99'])

    stats_df = stats_df.round(2)

    return stats_df


def create_statistics_table(df):
    tags = df['extra_tags'].str.split('&').apply(lambda x: dict(tag.split('=') for tag in x))
    df['language'] = tags.apply(lambda x: x.get('language'))
    df['testName'] = tags.apply(lambda x: x.get('testName'))
    df['endpoint'] = tags.apply(lambda x: x.get('endpoint'))
    df['variation'] = df['testName'].str.extract(r'(standard|elastic|otel)')

    # Define a helper function to calculate the statistics
    def calculate_statistics(data):
        return {
            'median': data.median(),
            'avg': data.mean(),
            # 'max_val': data.max(),
            # 'min_val': data.min(),
            # 'p75': data.quantile(0.75),
            # 'p90': data.quantile(0.90),
            'p95': data.quantile(0.95),
            'p99': data.quantile(0.99)
        }

    # Calculate statistics for each configuration
    stats_standard = calculate_statistics(df[df['variation'] == 'standard']['metric_value'])
    stats_elastic = calculate_statistics(df[df['variation'] == 'elastic']['metric_value'])
    stats_otel = calculate_statistics(df[df['variation'] == 'otel']['metric_value'])

    # Create a dataframe to display the results
    stats_df = pd.DataFrame({
        'Configuration': ['Standard', 'Elastic', 'Otel'],
        'Median': [stats_standard['median'], stats_elastic['median'], stats_otel['median']],
        'Avg': [stats_standard['avg'], stats_elastic['avg'], stats_otel['avg']],
        # 'P90': [stats_standard['p90'], stats_elastic['p90'], stats_otel['p90']],
        'P95': [stats_standard['p95'], stats_elastic['p95'], stats_otel['p95']],
        'P99': [stats_standard['p99'], stats_elastic['p99'], stats_otel['p99']],
        # 'Max Value': [stats_standard['max_val'], stats_elastic['max_val'], stats_otel['max_val']],
        # 'Min Value': [stats_standard['min_val'], stats_elastic['min_val'], stats_otel['min_val']]
    })

    stats_df = stats_df.round(2)

    return stats_df


def plot_endpoint_boxplots(df):
    tags = df['extra_tags'].str.split('&').apply(lambda x: dict(tag.split('=') for tag in x))
    df['language'] = tags.apply(lambda x: x.get('language'))
    df['testName'] = tags.apply(lambda x: x.get('testName'))
    df['endpoint'] = tags.apply(lambda x: x.get('endpoint'))
    df['variation'] = df['testName'].str.extract(r'(standard|elastic|otel)')

    # Get the unique endpoints
    endpoints = df['endpoint'].unique()

    # Create a figure with subplots for each endpoint
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    axs = axs.flatten()

    # Colors for the boxplots
    colors = ['lightblue', 'lightcoral', 'lightgreen']

    # Define a helper function to annotate the medians and means
    def annotate_median(ax, data, position, endpoint):
        median = data.median()

        ax.annotate(f'Median: {median:.2f}',
                    xy=(position, median),
                    xytext=(position + 0.35, median),
                    bbox=dict(boxstyle='round,pad=0.3', edgecolor='black', facecolor='white'),
                    color='black',
                    ha='center',
                    va='center',
                    fontsize='14')

    def annotate_mean(ax, data, position):
        mean = data.mean()
        ax.plot(position, mean, 'ro')  # Add red point for mean
        # ax.annotate(f'Mean: {mean:.2f}',
        #             xy=(position, mean),
        #             xytext=(position + 0.35, mean),
        #             bbox=dict(boxstyle='round,pad=0.3', edgecolor='black', facecolor='yellow'),
        #             color='black',
        #             ha='center',
        #             va='center')

    # Plot each endpoint
    for i, endpoint in enumerate(endpoints):
        ax = axs[i]

        # Filter data for each endpoint
        data_standard = \
            df[(df['endpoint'] == endpoint) & (df['variation'] == 'standard')][
                'metric_value']
        data_otel = df[(df['endpoint'] == endpoint) & (df['variation'] == 'otel')][
            'metric_value']
        data_elastic = df[(df['endpoint'] == endpoint) & (df['variation'] == 'elastic')][
            'metric_value']

        # Combined boxplot for the current endpoint
        boxplot_data = [data_standard.dropna(), data_otel.dropna(), data_elastic.dropna()]
        bplot = ax.boxplot(boxplot_data, labels=['Non-\nInstrumented', 'OpenTelemetry\nInstrumented',
                                                 'Elastic APM\nInstrumented'], patch_artist=True,
                           showfliers=False)

        # Set colors
        for patch, color in zip(bplot['boxes'], colors):
            patch.set_facecolor(color)

        for median in bplot['medians']:
            median.set_color('black')

        # Add grid
        ax.yaxis.grid(True, linestyle='--', which='major', color='grey', alpha=0.5)

        annotate_median(ax, data_standard, 1, endpoint)
        annotate_median(ax, data_otel, 2, endpoint)
        annotate_median(ax, data_elastic, 3, endpoint)

        # annotate_mean(ax, data_standard, 1)
        # annotate_mean(ax, data_elastic, 2)
        # annotate_mean(ax, data_otel, 3)

        # Set titles and labels
        ax.set_title(f'Endpoint: {endpoint}')
        ax.set_ylabel('Request Duration (ms)', fontsize=18)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plot_name = "aggregated_plot_endpoints.pdf"
    plt.savefig(plot_name)
    plt.savefig(plot_name.replace("pdf", "png"))
    plt.close(fig)


def merge_csv_files(file1, file2, output_file):
    # Read the CSV files into DataFrames
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Filter out rows from the first file that contain "nodejs" in the 'language' or 'appName' column
    df1_filtered = df1[~df1['extra_tags'].str.contains("language=nodejs|appName=nodejs", na=False)]

    # Filter rows from the second file that contain "nodejs" in the 'language' or 'appName' column
    df2_nodejs = df2[df2['extra_tags'].str.contains("language=nodejs|appName=nodejs", na=False)]

    # Combine the filtered DataFrames
    combined_df = pd.concat([df1_filtered, df2_nodejs], ignore_index=True)

    # Write the combined DataFrame to a new CSV file
    combined_df.to_csv(output_file, index=False)
    print(f"Results merged and written to {output_file}")


if __name__ == '__main__':
    ## Clean Data
    # input_directory = '../results/k6-files-nodejs'  # Replace with your directory path
    # output_file = 'http_req_duration_combined-nodejs.csv'  # Specify the output file name
    # filter_http_req_duration_in_directory(input_directory, output_file)

    output_file1 = 'http_req_duration_combined.csv'
    output_file2 = 'http_req_duration_combined-nodejs.csv'

    merge_csv_files(output_file1, output_file2, 'merged_results.csv')

    # Analyze
    data = pd.read_csv('merged_results.csv')

    print("Table 1:")
    # table_1 = generate_http_req_duration_stats(data, scenarios)
    table_1 = generate_http_req_duration_stats(data)
    print(table_1)
    #
    print("Table 2:")
    table_2 = create_statistics_table(data)
    print(table_2)
    #
    print("Table 3:")
    table_3 = create_statistics_table_languages(data)
    print(table_3)
    #
    print("Plots:")
    plot_endpoint_boxplots(data)
