import math

import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np


class K6Statistics:
    def __init__(self, csv_file_path, cpu_file_path=None, plots_dir="plots"):
        self.csv_file_path = csv_file_path
        self.cpu_file_path = cpu_file_path
        self.plots_dir = plots_dir
        self.file_name = csv_file_path.split('/')[-1]

        # Read the data
        self.data = pd.read_csv(csv_file_path)
        if self.cpu_file_path is not None:
            self.cpu_data = pd.read_csv(cpu_file_path)
            # Change the percentage to float
            self.cpu_data['CPU_Percentage'] = self.cpu_data['CPU_Percentage'].str.rstrip('%').astype('float')

    def save_or_show_plot(self, plot_name, save_plot=True):
        if save_plot:
            if not os.path.exists(self.plots_dir):
                os.makedirs(self.plots_dir)
            plt.savefig('{}/{}'.format(self.plots_dir, plot_name))
        else:
            plt.show()

    def show_total_number_of_requests(self, save_csv=True):
        # metrics_of_interest = ['http_reqs', 'http_req_failed', 'http_req_blocked', 'http_req_connecting',
        #                        'http_req_duration', 'http_req_receiving', 'http_req_sending',
        #                        'http_req_tls_handshaking', 'http_req_waiting', 'iteration_duration']
        metrics_of_interest = [
            'http_reqs',
            'http_req_duration',
            'http_req_waiting', 'iteration_duration'
        ]
        http_reqs_df = self.data[self.data['metric_name'].isin(metrics_of_interest)]

        # Assuming status codes 200-299 indicate success
        http_reqs_df['request_outcome'] = 'failed'  # Default to failed
        http_reqs_df.loc[self.data['status'].between(200, 299, inclusive='both'), 'request_outcome'] = 'successful'

        aggregated_metrics = http_reqs_df.groupby(['scenario', 'metric_name'])['metric_value'].mean().unstack()

        # Aggregate successful and failed requests separately
        success_failure_summary = http_reqs_df[http_reqs_df['metric_name'].isin(['http_reqs', 'http_req_failed'])]
        requests_summary = success_failure_summary.groupby(['scenario', 'request_outcome'])[
            'metric_value'].sum().unstack().fillna(0)

        # Combine aggregated metrics with the success/failure summary
        combined_pivot = pd.concat([requests_summary, aggregated_metrics], axis=1)

        # Calculate total requests for each scenario
        try:
            combined_pivot['total_requests'] = combined_pivot[['successful', 'failed']].sum(axis=1)
        except KeyError:
            combined_pivot['total_requests'] = combined_pivot[['successful']].sum(axis=1)

        # Order the columns
        # column_order = ['successful', 'failed', 'total_requests']
        # combined_pivot = combined_pivot[column_order]

        combined_pivot = combined_pivot.round(3)

        print(combined_pivot)
        if save_csv:
            combined_pivot.to_csv("metrics/{}-detailed-metrics.csv".format(self.file_name.replace(".csv", "")))

    # Throughput
    def plot_throughput(self, save_plot=True):
        throughput_data = self.data[self.data['metric_name'] == 'http_reqs']

        plt.figure(figsize=(12, 6))
        plt.plot(throughput_data['timestamp'], throughput_data['metric_value'].cumsum(), marker='o',
                 linestyle='-',
                 label='Throughput')
        plt.xlabel('Timestamp')
        plt.ylabel('Cumulative Requests')
        plt.title('Throughput Over Time')
        plt.legend()
        plt.grid(True)
        plot_name = self.file_name + "-throughput.png"
        self.save_or_show_plot(plot_name, save_plot)

    # Performance. Can also select specific scenarios
    def plot_request_performance(self, metrics_of_interest=None, included_scenarios=None, save_plot=True):

        # Filter out relevant metrics for plotting
        if metrics_of_interest is None:
            metrics_of_interest = [
                'http_req_duration', 'http_req_blocked', 'http_req_connecting',
                'http_req_sending', 'http_req_waiting', 'http_req_receiving'
            ]
        filtered_df = self.data[self.data['metric_name'].isin(metrics_of_interest)]

        # Convert timestamp to datetime for better x-axis labels
        filtered_df['timestamp'] = pd.to_datetime(filtered_df['timestamp'], unit='s')

        # Filter the Dataframe to include only specified scenarios
        if included_scenarios is not None:
            filtered_df = filtered_df[filtered_df['scenario'].isin(included_scenarios)]

        # Group by scenario and then plot each metric within each scenario
        for scenario, scenario_df in filtered_df.groupby('scenario'):
            fig, ax = plt.subplots(figsize=(12, 8))

            for metric in metrics_of_interest:
                metric_df = scenario_df[scenario_df['metric_name'] == metric]
                if not metric_df.empty:
                    ax.plot(metric_df['timestamp'], metric_df['metric_value'], label=metric)

            ax.set_title(f'Request Performance Metrics for Scenario: {scenario}')
            ax.set_xlabel('Time')
            ax.set_ylabel('Metric Value')
            ax.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()

            # Show the plot
            plot_name = self.file_name + "-request-performance.png"
            self.save_or_show_plot(plot_name, save_plot)

    # Transfer Rate
    def plot_transfer_rate(self, save_plot=True):
        requests_per_second = self.data[self.data['metric_name'] == 'http_reqs'][
            'timestamp'].value_counts().sort_index()

        plt.figure(figsize=(10, 6))
        requests_per_second.plot(kind='bar')
        plt.xlabel('Timestamp')
        plt.ylabel('Requests per Second')
        plt.title('Transfer Rate Over Time')
        plot_name = self.file_name + "-transfer-rate.png"
        self.save_or_show_plot(plot_name, save_plot)

    # HTTP Request Duration
    def plot_http_request_duration(self, save_plot=True):
        http_req_durations = self.data[self.data['metric_name'] == 'http_req_duration']['metric_value']

        plt.figure(figsize=(10, 6))
        durations_summary = pd.DataFrame({
            'Metrics': ['Average', 'P90', 'P95', 'P99'],
            'Duration (ms)': [
                http_req_durations.mean(),
                http_req_durations.quantile(0.9),
                http_req_durations.quantile(0.95),
                http_req_durations.quantile(0.99),
            ]
        })

        durations_summary.plot(x='Metrics', y='Duration (ms)', kind='bar', legend=False)
        plt.xticks(rotation=0)
        plt.ylabel('Duration (ms)')
        plt.title('HTTP Request Duration Metrics')
        plot_name = self.file_name + "-http-request-duration.png"
        self.save_or_show_plot(plot_name, save_plot)

    def show_metrics(self, save_csv=True):
        metrics = [
            'http_req_blocked', 'http_req_connecting', 'http_req_duration',
            'http_req_receiving', 'http_req_sending', 'http_req_tls_handshaking',
            'http_req_waiting', 'iteration_duration'
        ]

        stats = []

        for metric in metrics:
            metric_data = self.data[self.data['metric_name'] == metric]['metric_value']
            stats.append({
                'metric': metric,
                'avg': f"{metric_data.mean():.6f}ms",
                'max': f"{metric_data.max():.6f}ms",
                'med': f"{metric_data.median():.6f}ms",
                'min': f"{metric_data.min():.6f}ms",
                'p90': f"{metric_data.quantile(0.9):.6f}ms",
                'p95': f"{metric_data.quantile(0.95):.6f}ms",
                'p99': f"{metric_data.quantile(0.99):.6f}ms",
            })

        stats_df = pd.DataFrame(stats)
        print(stats_df)
        if save_csv:
            stats_df.to_csv("metrics/{}".format(self.file_name))

    def plot_overhead(self, scenarios, plot_name=None, metrics_of_interest=None, save_plot=True):
        if metrics_of_interest is None:
            metrics_of_interest = ['iteration_duration']

        # Prepare data for boxplotting
        metric_data = {}
        for metric in metrics_of_interest:
            metric_data[metric] = []

        # Collecting all metric values for each scenario
        for scenario in scenarios:
            scenario_df = self.data[
                (self.data['scenario'] == scenario) & (self.data['metric_name'].isin(metrics_of_interest))]
            for metric in metrics_of_interest:
                if metric in scenario_df['metric_name'].values:
                    metric_values = scenario_df[scenario_df['metric_name'] == metric]['metric_value'].tolist()
                    metric_data[metric].append(metric_values)
                else:
                    metric_data[metric].append([])  # Append an empty list if no data for this metric

        # Plotting
        fig, ax = plt.subplots(figsize=(14, 8))
        positions = np.arange(1, len(scenarios) + 1)  # Positioning of boxplots

        for i, metric in enumerate(metrics_of_interest):
            # Create subplots for each metric if there are multiple metrics
            if len(metrics_of_interest) > 1:
                ax = fig.add_subplot(1, len(metrics_of_interest), i + 1)

            # Plotting boxplot
            ax.boxplot(metric_data[metric], positions=positions, widths=0.6, patch_artist=True)
            ax.set_title(f'{metric} Across Scenarios')
            ax.set_xticklabels(scenarios, rotation=45, ha="right")
            ax.set_xlabel('Scenarios')
            ax.set_ylabel(f'{metric} Values (ms)')

        # Adding overall plot adjustments and grid
        plt.grid(axis='y', linestyle='--')
        plt.tight_layout()

        if plot_name is None:
            plot_name = self.file_name + "overhead"
        plot_name += ".png"
        self.save_or_show_plot(plot_name, save_plot)

    def show_overhead(self, scenarios, plot_name=None, metrics_of_interest=None, save_plot=True):
        """
        Calculate and plot the average values of specified metrics for multiple scenarios, and print a table of these averages.

        Parameters:
        - csv_file: Path to the CSV file containing the data.
        - scenarios: A list of scenarios to compare (e.g., ['python_4096', 'python-otel_4096', 'another_scenario']).
        - metrics_of_interest: List of metrics to compare. If None, a default list is used.
        """
        if metrics_of_interest is None:
            # Longer list
            metrics_of_interest = ['http_req_blocked', 'http_req_connecting', 'http_req_duration',
                                   'http_req_receiving', 'http_req_sending', 'http_req_tls_handshaking',
                                   'http_req_waiting', 'iteration_duration']
            # Shorter list
            # metrics_of_interest = ['http_req_duration', 'iteration_duration']

        averages_list = []
        for scenario in scenarios:
            scenario_df = self.data[
                (self.data['scenario'] == scenario) & (self.data['metric_name'].isin(metrics_of_interest))]
            averages = scenario_df.groupby('metric_name')['metric_value'].mean().rename(f'Average_{scenario}')
            averages_list.append(averages)

        comparison_df = pd.concat(averages_list, axis=1)

        # Display the DataFrame
        print(comparison_df.round(3))

    def get_scenarios(self):
        tags_dicts = []
        for extra_tags in self.data['extra_tags']:
            tag_dict = {}
            if isinstance(extra_tags, str):
                pairs = extra_tags.split('&')
                for pair in pairs:
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        tag_dict[key] = value
            tags_dicts.append(tag_dict)

        self.data['tags_dict'] = tags_dicts

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

        self.data['unique_id'] = unique_ids

        # Find the first and last timestamp for each unique identifier
        test_times = self.data.groupby('unique_id')['timestamp'].agg(['min', 'max'])

        # Create a list of scenarios with relevant details
        scenarios = []
        for unique_id, times in test_times.iterrows():
            # Check if the unique_id is empty
            if unique_id == "____":
                continue
            components = unique_id.split('_')
            test_name, app_name, rps, endpoint, language = components

            # Find a matching container name based on 'appName'
            matching_container = self.cpu_data[self.cpu_data['Container'].str.contains(app_name, na=False)]

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

    def get_tags(self, tag_string):
        parsed_dict = {}
        pairs = tag_string.split('&')
        for pair in pairs:
            key, value = pair.split('=')

            parsed_dict[key] = value
        return parsed_dict

    def plot_cpu_usage_by_endpoints(self, container_name, scenarios, plot_name=None, save_plot=True):
        cpu_df = self.cpu_data

        fig, ax = plt.subplots(figsize=(10, 6))

        # Get all unique endpoints for this container
        container_scenarios = [s for s in scenarios if s['container_name'] == container_name]
        unique_endpoints = {s['endpoint'] for s in container_scenarios}

        # Plot each endpoint's CPU usage with normalized time
        for endpoint in unique_endpoints:
            # Get the relevant scenario to find start and end times
            scenario = next(s for s in container_scenarios if s['endpoint'] == endpoint)

            start_time = scenario['start_time']
            end_time = scenario['end_time']

            # Filter the data for the specific container and time range
            container_df = cpu_df[
                (cpu_df['Container'] == container_name) &
                (cpu_df['Timestamp'] >= start_time) &
                (cpu_df['Timestamp'] <= end_time)
                ]

            # Normalize the time to a common range (0-60 seconds)
            if not container_df.empty:
                container_df['Normalized_Time'] = (
                        (container_df['Timestamp'] - start_time) / (end_time - start_time) * 60
                )

                # Plot the CPU usage with normalized time
                ax.plot(container_df['Normalized_Time'], container_df['CPU_Percentage'], label=endpoint)

        # Add a horizontal dashed line at the 80% CPU usage mark
        ax.axhline(80, color='red', linestyle='--', linewidth=1, label='80% Threshold')

        ax.set_xlabel("Normalized Time (seconds)")
        plt.ylabel('CPU Usage (%)')
        plt.title('CPU Usage Over Time')

        plt.legend()

        # Adjusting Y-tick rates for better readability
        plt.locator_params(axis='y', nbins=10)

        if plot_name is None:
            plot_name = self.file_name + "cpu_usage"
        plot_name += ".png"
        self.save_or_show_plot(plot_name, save_plot)

    def plot_cpu_usage_by_scenarios(self, scenarios, language, endpoint, plot_name=None, save_plot=True):
        """
        Plots the CPU usage for scenarios that share the same language and endpoint across different container names.

        Parameters:
        - scenarios: List of scenario dictionaries containing 'container_name', 'endpoint', 'language', etc.
        - language: The specific programming language to filter by (e.g., "go").
        - endpoint: The specific endpoint to plot across multiple containers.
        - cpu_df: DataFrame containing the CPU usage data.
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        # Filter scenarios by language and endpoint
        relevant_scenarios = [s for s in scenarios if s['language'] == language and s['endpoint'] == endpoint]

        # Plot each unique container's CPU usage for the specified endpoint and language
        for scenario in relevant_scenarios:
            container_name = scenario['container_name']
            start_time = scenario['start_time']
            end_time = scenario['end_time']

            # Filter the CPU data for this container and time range
            container_df = self.cpu_data[
                (self.cpu_data['Container'] == container_name) &
                (self.cpu_data['Timestamp'] >= start_time) &
                (self.cpu_data['Timestamp'] <= end_time)
                ]

            # Normalize the time to a common scale (0 to 60 seconds)
            if not container_df.empty:
                container_df['Normalized_Time'] = (
                        (container_df['Timestamp'] - start_time) / (end_time - start_time) * 60
                )

                # Plot the CPU usage with normalized time, labeled by container name
                ax.plot(container_df['Normalized_Time'], container_df['CPU_Percentage'], label=container_name)

        # Add a horizontal dashed line at the 80% CPU usage mark
        ax.axhline(80, color='red', linestyle='--', linewidth=1, label='80% Threshold')

        ax.set_xlabel("Normalized Time (seconds)")
        ax.set_ylabel("CPU Usage (%)")
        ax.set_title(f"CPU Usage for '{endpoint}' Endpoint in '{language}'")
        ax.legend()
        plt.grid(axis='y', linestyle='--')

        if plot_name is None:
            plot_name = self.file_name + "cpu_usage_scenarios"
        plot_name += ".png"
        self.save_or_show_plot(plot_name, save_plot)
