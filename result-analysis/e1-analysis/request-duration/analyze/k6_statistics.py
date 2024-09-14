import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

plt.rcParams.update({'font.size': 18})


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

        self.metric_name_mapping = {
            'http_req_blocked': 'HTTP Request Blocked',
            'http_req_connecting': 'HTTP Request Connecting',
            'http_req_duration': 'HTTP Request Duration',
            'http_req_receiving': 'HTTP Request Receiving',
            'http_req_sending': 'HTTP Request Sending',
            'http_req_tls_handshaking': 'HTTP Request TLS Handshaking',
            'http_req_waiting': 'HTTP Request Waiting',
            'iteration_duration': 'Iteration Duration'
        }

    def save_or_show_plot(self, plot_name, save_plot=True):
        if save_plot:
            if not os.path.exists(self.plots_dir):
                os.makedirs(self.plots_dir)
            plt.savefig('{}/{}'.format(self.plots_dir, plot_name))
        else:
            plt.show()

    def show_total_number_of_requests(self, save_csv=True):
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

            # ax.set_title(f'Request Performance Metrics for Scenario: {scenario}')
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

    def show_metrics_scenarios(self, scenarios, directory, save_csv=True):
        metrics = [
            'http_req_blocked', 'http_req_connecting', 'http_req_duration',
            'http_req_receiving', 'http_req_sending', 'http_req_tls_handshaking',
            'http_req_waiting', 'iteration_duration', 'http_reqs', 'http_req_failed',
        ]

        for scenario in scenarios:
            print(f"Scenario: {scenario['scenario_name']}")
            filtered_data = self.data[
                (self.data['timestamp'] >= scenario['start_time']) &
                (self.data['timestamp'] <= scenario['end_time'])
                ]

            stats = []
            for metric in metrics:
                metric_data = filtered_data[filtered_data['metric_name'] == metric]['metric_value']
                if not metric_data.empty:
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
                else:
                    stats.append({
                        'metric': metric, 'avg': 'N/A', 'max': 'N/A', 'med': 'N/A',
                        'min': 'N/A', 'p90': 'N/A', 'p95': 'N/A', 'p99': 'N/A',
                    })

            stats_df = pd.DataFrame(stats)
            print(stats_df)

            if save_csv:
                scenario_file_name = f"{self.file_name}_{scenario['scenario_name']}.csv"
                filename = f"{directory}/{scenario_file_name}"
                if not os.path.isdir(directory):
                    os.makedirs(directory)
                stats_df.to_csv(filename)
                print(f"Metrics saved to metrics/{scenario_file_name}")

    import matplotlib.pyplot as plt
    import numpy as np

    def plot_overhead(self, scenarios, plot_name=None, metrics_of_interest=None, save_plot=True):
        if metrics_of_interest is None:
            metrics_of_interest = ['http_req_duration']

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

        # Colors for the scenarios
        colors = []
        for scenario in scenarios:
            if 'java' in scenario:
                colors.append('darkred')
            elif 'python' in scenario:
                colors.append('gold')
            elif 'go' in scenario:
                colors.append('darkblue')
            else:
                colors.append('grey')  # Default color

        # Format the scenario names
        formatted_scenarios = [scenario.replace('-', ' ').title() for scenario in scenarios]

        # Plotting
        fig, ax = plt.subplots(figsize=(14, 8))
        positions = np.arange(1, len(scenarios) + 1)  # Positioning of boxplots

        for i, metric in enumerate(metrics_of_interest):
            # Create subplots for each metric if there are multiple metrics
            if len(metrics_of_interest) > 1:
                ax = fig.add_subplot(1, len(metrics_of_interest), i + 1)

            # Plotting boxplot without outliers and with specified colors
            boxplots = ax.boxplot(metric_data[metric], positions=positions, widths=0.6, patch_artist=True,
                                  showfliers=False)
            for patch, color in zip(boxplots['boxes'], colors):
                patch.set_facecolor(color)
                patch.set_edgecolor('black')  # Adding edge color to boxes

            # Beautifying boxplot elements
            for element in ['whiskers', 'caps', 'medians']:
                plt.setp(boxplots[element], color='black')

            # ax.set_title(f'{self.metric_name_mapping[metric]} Across Scenarios')
            ax.set_xticklabels(formatted_scenarios, rotation=45, ha="right")
            ax.set_xlabel('Applications')
            ax.set_ylabel(f'{self.metric_name_mapping[metric]} (ms)')

        # Adding overall plot adjustments and grid
        plt.grid(axis='y', linestyle='--', linewidth=0.7)
        plt.tight_layout()

        if plot_name is None:
            plot_name = self.file_name + "overhead"
        plot_name += ".png"
        self.save_or_show_plot(plot_name, save_plot)

    def plot_overhead_horizontal(self, scenarios, plot_name=None, metrics_of_interest=None, save_plot=True):
        if metrics_of_interest is None:
            metrics_of_interest = ['http_req_duration']

        # Prepare data for boxplotting
        metric_data = {}
        for metric in metrics_of_interest:
            metric_data[metric] = []

        # Collecting all metric values for each scenario
        for scenario_name in scenarios:
            scenario_df = self.data[
                (self.data['scenario'] == scenario_name) & (self.data['metric_name'].isin(metrics_of_interest))]
            for metric in metrics_of_interest:
                if metric in scenario_df['metric_name'].values:
                    metric_values = scenario_df[scenario_df['metric_name'] == metric]['metric_value'].tolist()
                    metric_data[metric].append(metric_values)
                else:
                    metric_data[metric].append([])  # Append an empty list if no data for this metric

        # Colors for the endpoints
        endpoint_colors = {
            'json': 'darkblue',
            'db': 'green',
            'updates': 'darkred',
            'queries': 'gold',
        }
        colors = []
        for scenario_name in scenarios:
            for endpoint in endpoint_colors:
                if endpoint in scenario_name:
                    colors.append(endpoint_colors[endpoint])
                    break
            else:
                colors.append('grey')  # Default color if no endpoint matches

        # Format the scenario names
        formatted_scenarios = [scenario_name.replace('-', ' ').title() for scenario_name in scenarios]

        # Plotting
        fig, ax = plt.subplots(figsize=(14, 8))
        positions = np.arange(1, len(scenarios) + 1)  # Positioning of boxplots

        for i, metric in enumerate(metrics_of_interest):
            # Create subplots for each metric if there are multiple metrics
            if len(metrics_of_interest) > 1:
                ax = fig.add_subplot(1, len(metrics_of_interest), i + 1)

            # Plotting boxplot without outliers and with specified colors
            boxplots = ax.boxplot(metric_data[metric], positions=positions, widths=0.6, patch_artist=True,
                                  showfliers=False, vert=False)
            for patch, color in zip(boxplots['boxes'], colors):
                patch.set_facecolor(color)
                patch.set_edgecolor('black')  # Adding edge color to boxes

            # Beautifying boxplot elements
            for element in ['whiskers', 'caps', 'medians']:
                plt.setp(boxplots[element], color='black')

            ax.set_title(self.metric_name_mapping.get(metric, metric).replace('_', ' ').title())
            ax.set_yticklabels(formatted_scenarios)
            ax.set_ylabel('Scenarios')
            ax.set_xlabel(f'{self.metric_name_mapping.get(metric, metric)} Values (ms)')

        # Adding overall plot adjustments and grid
        plt.grid(axis='x', linestyle='--', linewidth=0.7)
        plt.tight_layout()

        if plot_name is None:
            plot_name = self.file_name + "overhead_horizontal"
        plot_name += ".png"
        self.save_or_show_plot(plot_name, save_plot)

    def plot_overhead_horizontal_endpoints(self, scenarios, plot_name=None, metrics_of_interest=None, save_plot=True):
        if metrics_of_interest is None:
            metrics_of_interest = ['http_req_duration']

        # Prepare data for boxplotting
        metric_data = {}
        for metric in metrics_of_interest:
            metric_data[metric] = {endpoint: [] for endpoint in ['json', 'db', 'updates', 'queries']}

        # Collecting all metric values for each scenario
        for scenario_name in scenarios:
            scenario_df = self.data[
                (self.data['scenario'] == scenario_name) & (self.data['metric_name'].isin(metrics_of_interest))]
            for metric in metrics_of_interest:
                if metric in scenario_df['metric_name'].values:
                    metric_values = scenario_df[scenario_df['metric_name'] == metric]['metric_value'].tolist()
                    for endpoint in metric_data[metric]:
                        if endpoint in scenario_name:
                            metric_data[metric][endpoint].append((scenario_name, metric_values))
                            break

        # Colors for the endpoints
        endpoint_colors = {
            'json': 'darkblue',
            'db': 'green',
            'updates': 'darkred',
            'queries': 'gold',
        }

        # Create a figure with 4 subplots
        fig, axs = plt.subplots(2, 2, figsize=(16, 12))
        axs = axs.flatten()

        # Function to format scenario names
        def format_scenario_name(name):
            parts = name.split('-')
            if 'otel' in parts:
                return 'OpenTelemetry'
            elif 'elastic' in parts:
                return 'Elastic APM'
            else:
                return 'Standard'

        # Order for sorting
        order = ['Standard', 'OpenTelemetry', 'Elastic APM']

        # Plotting
        for ax, (endpoint, color) in zip(axs, endpoint_colors.items()):
            for i, metric in enumerate(metrics_of_interest):
                # Extract the metric values and scenario names for the current endpoint
                scenario_names, metric_values = zip(*metric_data[metric][endpoint]) if metric_data[metric][
                    endpoint] else ([], [])

                # Function to get the order index
                def get_order_index(name):
                    formatted_name = format_scenario_name(name)
                    for i, key in enumerate(order):
                        if key in formatted_name:
                            return i
                    return len(order)  # Default to last position if no match found

                # Sort the scenario names and metric values by the desired order
                sorted_data = sorted(zip(scenario_names, metric_values), key=lambda x: get_order_index(x[0]))
                scenario_names, metric_values = zip(*sorted_data) if sorted_data else ([], [])

                # Plotting boxplot without outliers and with specified colors
                positions = np.arange(1, len(scenario_names) + 1)
                boxplots = ax.boxplot(metric_values, positions=positions, widths=0.6, patch_artist=True,
                                      showfliers=False, vert=False)
                for patch in boxplots['boxes']:
                    patch.set_facecolor(color)
                    patch.set_edgecolor('black')  # Adding edge color to boxes

                # Beautifying boxplot elements
                for element in ['whiskers', 'caps', 'medians']:
                    plt.setp(boxplots[element], color='black')

                # Set the title using the mapped metric name
                ax.set_title(f'{endpoint.title()} Endpoint')
                ax.set_yticks(positions)
                ax.set_yticklabels([format_scenario_name(name) for name in scenario_names])
                ax.set_ylabel('Applications')
                ax.set_xlabel(f'{self.metric_name_mapping.get(metric, metric)} (ms)')

                # Adding grid lines
                ax.grid(axis='x', linestyle='--', linewidth=0.7)

        # Adding overall plot adjustments and grid
        plt.tight_layout()

        if plot_name is None:
            plot_name = self.file_name + "overhead_horizontal_endpoints"
        plot_name += ".png"
        plt.savefig(plot_name)
        if not save_plot:
            plt.show()
        plt.close(fig)

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

        ax.set_xlabel("Test Duration (seconds)")
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

    def plot_aggregated_results_by_variation_and_endpoint(self, scenario_list, plot_name="aggregated_plot.png",
                                                          save_plot=True):
        # Define the endpoints, variations, and colors
        endpoints = ['json', 'db', 'queries', 'updates']
        variations = ['standard', 'otel', 'elastic']
        variation_colors = {
            'standard': '#1f77b4',  # blue
            'otel': '#ff7f0e',  # orange
            'elastic': '#2ca02c'  # green
        }

        # Prepare data for boxplotting
        metric_data = {endpoint: {variation: [] for variation in variations} for endpoint in endpoints}

        # Filter the DataFrame for the http_req_duration metric
        filtered_df = self.data[self.data['metric_name'] == 'http_req_duration']

        # Collecting all metric values for each endpoint and variation
        for scenario in scenario_list:
            endpoint = scenario['endpoint']
            variation = scenario['scenario_name'].split('-')[1]
            if endpoint in endpoints and variation in variations:
                scenario_df = filtered_df[filtered_df['scenario'] == scenario['scenario_name']]
                metric_values = scenario_df['metric_value'].astype(float).tolist()
                metric_data[endpoint][variation].extend(metric_values)

        # Create a figure with 4 subplots
        fig, axs = plt.subplots(2, 2, figsize=(16, 12))
        axs = axs.flatten()

        # Plotting
        for ax, endpoint in zip(axs, endpoints):
            positions = np.arange(1, len(variations) + 1)
            data_to_plot = [metric_data[endpoint][variation] for variation in variations]

            # Plotting boxplot with outliers included
            boxplots = ax.boxplot(data_to_plot, positions=positions, widths=0.6, patch_artist=True, showfliers=False,
                                  vert=False)
            for patch, color in zip(boxplots['boxes'], [variation_colors[var] for var in variations]):
                patch.set_facecolor(color)
                patch.set_edgecolor('black')  # Adding edge color to boxes

            # Beautifying boxplot elements
            for element in ['whiskers', 'caps', 'medians', 'fliers']:
                plt.setp(boxplots[element], color='black')

            # Set the title using the endpoint name
            ax.set_title(f'{endpoint.title()} Endpoint')
            ax.set_yticks(positions)
            ax.set_yticklabels([variation.capitalize() for variation in variations])
            ax.set_xlabel('HTTP Request Duration (ms)')
            ax.set_ylabel('Variations')


            # Adding grid lines
            ax.grid(axis='x', linestyle='--', linewidth=0.7)

            # Annotate median values
            medians = [np.median(data) for data in data_to_plot]
            for pos, median, variation in zip(positions, medians, variations):
                ax.text(median, pos, f'{median:.2f}', va='center', ha='left', color='black',
                        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))

        # Adding overall plot adjustments and grid
        plt.tight_layout()

        # Save plot as PNG file
        plt.savefig(plot_name)
        if not save_plot:
            plt.show()
        plt.close(fig)

    def generate_http_req_duration_stats(self, scenario_list):
        # Define the columns for the output table
        columns = ['Language', 'Variation', 'Endpoint', 'Average', 'Max', 'Median', 'Min', 'P90', 'P95', 'P99']

        # Initialize a list to hold the data for the table
        data = []

        # Filter the DataFrame for the http_req_duration metric
        filtered_df = self.data[self.data['metric_name'] == 'http_req_duration']

        # Collecting all metric values for each scenario
        for scenario in scenario_list:
            language = scenario['language']
            endpoint = scenario['endpoint']
            variation = scenario['scenario_name'].split('-')[1]

            scenario_df = filtered_df[filtered_df['scenario'] == scenario['scenario_name']]
            if not scenario_df.empty:
                metric_values = scenario_df['metric_value'].astype(float)
                avg = metric_values.mean()
                max_val = metric_values.max()
                med = np.median(metric_values)
                # metric_values.median()
                min_val = metric_values.min()
                p90 = metric_values.quantile(0.90)
                p95 = metric_values.quantile(0.95)
                p99 = metric_values.quantile(0.99)

                data.append([language, variation, endpoint, avg, max_val, med, min_val, p90, p95, p99])

        # Create a DataFrame for the table
        stats_df = pd.DataFrame(data, columns=columns)

        # Pivot the table to get a cleaner format with each language as a row
        pivot_table = stats_df.pivot_table(index=['Language', 'Variation', 'Endpoint'],
                                           values=['Average', 'Max', 'Median', 'Min', 'P90', 'P95', 'P99'])

        return pivot_table



    def generate_aggregated_http_req_duration_stats(self, scenario_list):
        # Define the columns for the output table
        columns = ['Variation', 'Endpoint', 'Average', 'Max', 'Median', 'Min', 'P90', 'P95', 'P99']

        # Initialize a list to hold the data for the table
        data = []

        # Filter the DataFrame for the http_req_duration metric
        filtered_df = self.data[self.data['metric_name'] == 'http_req_duration']

        # Collecting all metric values for each scenario
        for scenario in scenario_list:
            endpoint = scenario['endpoint']
            variation = scenario['scenario_name'].split('-')[1]

            scenario_df = filtered_df[filtered_df['scenario'] == scenario['scenario_name']]
            if not scenario_df.empty:
                metric_values = scenario_df['metric_value'].astype(float)
                avg = metric_values.mean()
                max_val = metric_values.max()
                med = np.median(metric_values)
                min_val = metric_values.min()
                p90 = metric_values.quantile(0.90)
                p95 = metric_values.quantile(0.95)
                p99 = metric_values.quantile(0.99)

                data.append([variation, endpoint, avg, max_val, med, min_val, p90, p95, p99])

        # Create a DataFrame for the table
        stats_df = pd.DataFrame(data, columns=columns)

        # Aggregate the statistics by variation and endpoint
        aggregated_stats = stats_df.groupby(['Variation', 'Endpoint']).agg({
            'Average': 'mean',
            'Max': 'max',
            'Median': 'median',
            'Min': 'min',
            'P90': 'mean',
            'P95': 'mean',
            'P99': 'mean'
        }).reset_index()

        return aggregated_stats

    # def generate_aggregated_http_req_duration_stats_variation(self, scenario_list):
    #     # Define the columns for the output table
    #     columns = ['Variation', 'Average', 'Max', 'Median', 'Min', 'P90', 'P95', 'P99']
    #
    #     # Initialize a list to hold the data for the table
    #     data = []
    #
    #     # Filter the DataFrame for the http_req_duration metric
    #     filtered_df = self.data[self.data['metric_name'] == 'http_req_duration']
    #
    #     # Collecting all metric values for each scenario
    #     for scenario in scenario_list:
    #         variation = scenario['scenario_name'].split('-')[1]
    #
    #         scenario_df = filtered_df[filtered_df['scenario'] == scenario['scenario_name']]
    #         if not scenario_df.empty:
    #             metric_values = scenario_df['metric_value'].astype(float)
    #             avg = metric_values.mean()
    #             max_val = metric_values.max()
    #             med = np.median(metric_values)
    #             min_val = metric_values.min()
    #             p90 = metric_values.quantile(0.90)
    #             p95 = metric_values.quantile(0.95)
    #             p99 = metric_values.quantile(0.99)
    #
    #             data.append([variation, avg, max_val, med, min_val, p90, p95, p99])
    #
    #     # Create a DataFrame for the table
    #     stats_df = pd.DataFrame(data, columns=columns)
    #     print("Table Data (before aggregation):")
    #     print(stats_df)
    #
    #     # Aggregate the statistics by variation
    #     aggregated_stats = stats_df.groupby('Variation').agg({
    #         'Average': 'mean',
    #         'Max': 'max',
    #         'Median': 'median',
    #         'Min': 'min',
    #         'P90': 'mean',
    #         'P95': 'mean',
    #         'P99': 'mean'
    #     }).reset_index()
    #
    #     print("Aggregated Table Data:")
    #     print(aggregated_stats)
    #
    #     return aggregated_stats
    #
    # def plot_aggregated_results_across_variations(self, scenario_list, plot_name="aggregated_variations_plot.png",
    #                                               save_plot=True):
    #     # Define the variations and their colors
    #     variations = ['standard', 'otel', 'elastic']
    #     variation_colors = {
    #         'standard': '#1f77b4',  # blue
    #         'otel': '#ff7f0e',  # orange
    #         'elastic': '#2ca02c'  # green
    #     }
    #
    #     # Prepare data for aggregation and plotting
    #     metric_data = {variation: [] for variation in variations}
    #
    #     # Filter the DataFrame for the http_req_duration metric
    #     filtered_df = self.data[self.data['metric_name'] == 'http_req_duration']
    #
    #     # Collecting all metric values for each variation
    #     for scenario in scenario_list:
    #         variation = scenario['scenario_name'].split('-')[1]
    #         if variation in variations:
    #             scenario_df = filtered_df[filtered_df['scenario'] == scenario['scenario_name']]
    #             metric_values = scenario_df['metric_value'].astype(float).tolist()
    #             metric_data[variation].extend(metric_values)
    #
    #     print("Plot Data (before plotting):")
    #     for variation, values in metric_data.items():
    #         print(f"{variation}: {values[:10]}...")  # Print first 10 values for brevity
    #
    #     # Create a figure
    #     fig, ax = plt.subplots(figsize=(10, 8))
    #
    #     # Plotting
    #     positions = np.arange(1, len(variations) + 1)
    #     data_to_plot = [metric_data[variation] for variation in variations]
    #
    #     # Plotting boxplot without outliers and with specified colors
    #     boxplots = ax.boxplot(data_to_plot, positions=positions, widths=0.6, patch_artist=True, showfliers=False,
    #                           vert=False)
    #     for patch, color in zip(boxplots['boxes'], [variation_colors[var] for var in variations]):
    #         patch.set_facecolor(color)
    #         patch.set_edgecolor('black')  # Adding edge color to boxes
    #
    #     # Beautifying boxplot elements
    #     for element in ['whiskers', 'caps', 'medians']:
    #         plt.setp(boxplots[element], color='black')
    #
    #     # Annotate median values
    #     medians = [np.median(data) for data in data_to_plot]
    #     for pos, median, variation in zip(positions, medians, variations):
    #         ax.text(median, pos, f'{median:.2f}', va='center', ha='left', fontsize=10, color='black',
    #                 bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))
    #
    #     # Set the title and labels
    #     ax.set_title('Aggregated HTTP Request Duration Across Variations')
    #     ax.set_yticks(positions)
    #     ax.set_yticklabels([variation.capitalize() for variation in variations])
    #     ax.set_xlabel('HTTP Request Duration (ms)')
    #     ax.set_ylabel('Variations')
    #
    #     # Adding grid lines
    #     ax.grid(axis='x', linestyle='--', linewidth=0.7)
    #
    #     # Adding overall plot adjustments and grid
    #     plt.tight_layout()
    #
    #     # Save plot as PNG file
    #     plt.savefig(plot_name)
    #     if not save_plot:
    #         plt.show()
    #     plt.close(fig)

    #######
    def aggregate_http_req_duration_stats(self, data, scenario_list):
        # Define the columns for the output DataFrame
        columns = ['Variation', 'Average', 'Max', 'Median', 'Min', 'P90', 'P95', 'P99']

        # Initialize a list to hold the data
        aggregated_data = []

        # Filter the DataFrame for the http_req_duration metric
        filtered_df = data[data['metric_name'] == 'http_req_duration']

        # Collecting all metric values for each scenario
        for scenario in scenario_list:

            variation = scenario['scenario_name'].split('-')[1]

            scenario_df = filtered_df[filtered_df['scenario'] == scenario['scenario_name']]
            if not scenario_df.empty:
                metric_values = scenario_df['metric_value'].astype(float)
                avg = metric_values.mean()
                max_val = metric_values.max()
                med = np.median(metric_values)
                min_val = metric_values.min()
                p90 = metric_values.quantile(0.90)
                p95 = metric_values.quantile(0.95)
                p99 = metric_values.quantile(0.99)

                aggregated_data.append([variation, avg, max_val, med, min_val, p90, p95, p99])

        # Create a DataFrame for the aggregated data
        aggregated_stats_df = pd.DataFrame(aggregated_data, columns=columns)

        # Aggregate the statistics by variation
        final_aggregated_stats = aggregated_stats_df.groupby('Variation').agg({
            'Average': 'mean',
            'Max': 'max',
            'Median': 'median',
            'Min': 'min',
            'P90': 'mean',
            'P95': 'mean',
            'P99': 'mean'
        }).reset_index()

        return final_aggregated_stats

    def generate_aggregated_http_req_duration_stats_variation(self, scenario_list):
        # Aggregate the data using the shared function
        aggregated_stats = self.aggregate_http_req_duration_stats(self.data, scenario_list)

        print("Aggregated Table Data:")
        print(aggregated_stats)

        return aggregated_stats

    def plot_aggregated_results_across_variations(self, scenario_list, plot_name="aggregated_variations_plot.png",
                                                  save_plot=True):
        # Aggregate the data using the shared function
        aggregated_stats = self.aggregate_http_req_duration_stats(self.data, scenario_list)

        print("Aggregated Plot Data:")
        print(aggregated_stats)

        # Prepare data for plotting
        variations = aggregated_stats['Variation'].tolist()
        variation_colors = {
            'standard': '#1f77b4',  # blue
            'otel': '#ff7f0e',  # orange
            'elastic': '#2ca02c'  # green
        }
        data_to_plot = []

        for variation in variations:
            variation_data = self.data[(self.data['metric_name'] == 'http_req_duration') &
                                       (self.data['scenario'].str.contains(variation))]['metric_value'].astype(
                float).tolist()
            data_to_plot.append(variation_data)

        # Create a figure
        fig, ax = plt.subplots(figsize=(10, 8))

        # Plotting
        positions = np.arange(1, len(variations) + 1)

        # Plotting boxplot without outliers and with specified colors
        boxplots = ax.boxplot(data_to_plot, positions=positions, widths=0.6, patch_artist=True, showfliers=False,
                              vert=False)
        for patch, color in zip(boxplots['boxes'], [variation_colors[var] for var in variations]):
            patch.set_facecolor(color)
            patch.set_edgecolor('black')  # Adding edge color to boxes

        # Beautifying boxplot elements
        for element in ['whiskers', 'caps', 'medians']:
            plt.setp(boxplots[element], color='black')

        # Annotate median values
        medians = [np.median(data) for data in data_to_plot]
        for pos, median, variation in zip(positions, medians, variations):
            ax.text(median, pos, f'{median:.2f}', va='center', ha='left', color='black',
                    bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))

        # Set the title and labels
        ax.set_title('Aggregated HTTP Request Duration Across Variations')
        ax.set_yticks(positions)
        ax.set_yticklabels(
            [variation.capitalize().replace('Otel', 'OpenTelemetry').replace('Elastic', 'Elastic APM') for variation in
             variations])
        ax.set_xlabel('HTTP Request Duration (ms)')
        ax.set_ylabel('Variations')

        # Adding grid lines
        ax.grid(axis='x', linestyle='--', linewidth=0.7)

        # Adding overall plot adjustments and grid
        plt.tight_layout()

        # Save plot as PNG file
        plt.savefig(plot_name)
        if not save_plot:
            plt.show()
        plt.close(fig)

    def create_boxplots(self):
        # Load the dataset
        # Filter the dataframe for the metric_name 'http_req_duration'
        df_duration = self.data[self.data['metric_name'] == 'http_req_duration']

        # Ensure the 'metadata' column is of string type
        df_duration['extra_tags'] = df_duration['extra_tags'].astype(str)

        # Extract the configurations from the 'extra_tags' column
        df_duration['configuration'] = df_duration['extra_tags'].str.extract(r'(standard|elastic|otel)')

        # Prepare the data for plotting
        data_standard = df_duration[df_duration['configuration'] == 'standard']['metric_value']
        data_elastic = df_duration[df_duration['configuration'] == 'elastic']['metric_value']
        data_otel = df_duration[df_duration['configuration'] == 'otel']['metric_value']

        # Create a figure with one boxplot
        fig, ax = plt.subplots(figsize=(12, 8))

        # Colors for the boxplots
        colors = ['lightblue', 'lightgreen', 'lightcoral']

        # Define a helper function to annotate the medians
        def annotate_median(ax, data, position):
            median = data.median()
            ax.annotate(f'{median:.2f}',
                        xy=(median, position),
                        xytext=(median, position + 0.275),
                        bbox=dict(boxstyle='round,pad=0.3', edgecolor='black', facecolor='white'),
                        color='black',
                        ha='center',
                        va='center')

        # Combined boxplot for all configurations without outliers
        boxplot_data = [data_standard.dropna(), data_elastic.dropna(), data_otel.dropna()]
        bplot = ax.boxplot(boxplot_data, vert=False, labels=['Standard', 'Elastic', 'Otel'], patch_artist=True,
                           showfliers=False)

        # Set colors for each box
        for patch, color in zip(bplot['boxes'], colors):
            patch.set_facecolor(color)

        for median in bplot['medians']:
            median.set_color('black')

        # Annotate the medians
        annotate_median(ax, data_standard, 1)
        annotate_median(ax, data_elastic, 2)
        annotate_median(ax, data_otel, 3)

        # Set titles and labels
        # ax.set_title('HTTP Request Duration by Configuration', fontsize=16, fontweight='bold')
        ax.set_ylabel('Configuration')
        ax.set_xlabel('Request Duration (ms)')

        # Add grid lines
        ax.xaxis.grid(True, linestyle='--', which='major', color='grey', alpha=0.7)
        ax.yaxis.grid(True, linestyle='--', which='major', color='grey', alpha=0.7)

        plt.tight_layout()
        plot_name = "aggregated_plot.png"
        plt.savefig(plot_name)
        plt.close(fig)

    def create_statistics_table(self):
        # Load the dataset

        # Filter the dataframe for the metric_name 'http_req_duration'
        df_duration = self.data[self.data['metric_name'] == 'http_req_duration']

        # Ensure the 'extra_tags' column is of string type
        df_duration['extra_tags'] = df_duration['extra_tags'].astype(str)

        # Extract the configurations from the 'extra_tags' column
        df_duration['configuration'] = df_duration['extra_tags'].str.extract(r'(standard|elastic|otel)')

        # Define a helper function to calculate the statistics
        def calculate_statistics(data):
            return {
                'median': data.median(),
                'avg': data.mean(),
                'max_val': data.max(),
                'min_val': data.min(),
                'p75': data.quantile(0.75),
                'p90': data.quantile(0.90),
                'p95': data.quantile(0.95),
                'p99': data.quantile(0.99)
            }

        # Calculate statistics for each configuration
        stats_standard = calculate_statistics(df_duration[df_duration['configuration'] == 'standard']['metric_value'])
        stats_elastic = calculate_statistics(df_duration[df_duration['configuration'] == 'elastic']['metric_value'])
        stats_otel = calculate_statistics(df_duration[df_duration['configuration'] == 'otel']['metric_value'])

        # Create a dataframe to display the results
        stats_df = pd.DataFrame({
            'Configuration': ['Standard', 'Elastic', 'Otel'],
            'Median': [stats_standard['median'], stats_elastic['median'], stats_otel['median']],
            'Avg': [stats_standard['avg'], stats_elastic['avg'], stats_otel['avg']],
            'Max Value': [stats_standard['max_val'], stats_elastic['max_val'], stats_otel['max_val']],
            'Min Value': [stats_standard['min_val'], stats_elastic['min_val'], stats_otel['min_val']],
            'P90': [stats_standard['p90'], stats_elastic['p90'], stats_otel['p90']],
            'P95': [stats_standard['p95'], stats_elastic['p95'], stats_otel['p95']],
            'P99': [stats_standard['p99'], stats_elastic['p99'], stats_otel['p99']]
        })

        stats_df = stats_df.round(2)

        return stats_df

    def create_statistics_table_by_endpoint(self):
        # Load the dataset
        df = self.data

        # Filter the dataframe for the metric_name 'http_req_duration'
        df_duration = df[df['metric_name'] == 'http_req_duration']

        # Ensure the 'metadata' column is of string type
        df_duration['extra_tags'] = df_duration['extra_tags'].astype(str)

        # Extract the configurations from the 'extra_tags' column
        df_duration['configuration'] = df_duration['extra_tags'].str.extract(r'(standard|elastic|otel)')

        # Extract the endpoint from the URL
        df_duration['endpoint'] = df_duration['url'].str.extract(r'(http://[^/]+(/[^?]*))')[1]

        # Group by endpoint and configuration
        grouped = df_duration.groupby(['endpoint', 'configuration'])

        # Calculate statistics for each group
        stats = grouped['metric_value'].agg(
            # count='count',
            mean='mean',
            # std='std',
            min='min',
            # q25=lambda x: x.quantile(0.25),
            median='median',
            # q75=lambda x: x.quantile(0.75),
            q90=lambda x: x.quantile(0.90),
            q95=lambda x: x.quantile(0.95),
            q99=lambda x: x.quantile(0.99),
            max='max'
        ).reset_index()

        stats = stats.round(2)

        # Rename columns for better readability
        stats.columns = [
            'Endpoint',
            'Configuration',
            # 'Count',
            'Mean',
            # 'Std Dev',
            'Min',
            # '25th Percentile',
            'Median',
            # '75th Percentile',
            'p90',
            'p95',
            'p99',
            'Max'
        ]

        return stats

    def plot_endpoint_boxplots(self):
        # Load the dataset
        df = self.data

        # Filter the dataframe for the metric_name 'http_req_duration'
        df_duration = df[df['metric_name'] == 'http_req_duration']

        # Ensure the 'metadata' column is of string type
        df_duration['extra_tags'] = df_duration['extra_tags'].astype(str)

        # Extract the configurations from the 'extra_tags' column
        df_duration['configuration'] = df_duration['extra_tags'].str.extract(r'(standard|elastic|otel)')

        # Extract the endpoint from the URL
        df_duration['endpoint'] = df_duration['url'].str.extract(r'(http://[^/]+(/[^?]*))')[1]

        # Get the unique endpoints
        endpoints = df_duration['endpoint'].unique()

        # Create a figure with subplots for each endpoint
        fig, axs = plt.subplots(2, 2, figsize=(15, 10))
        axs = axs.flatten()

        # Colors for the boxplots
        colors = ['lightblue', 'lightgreen', 'lightcoral']

        # Define a helper function to annotate the medians
        def annotate_median(ax, data, position):
            median = data.median()
            ax.annotate(f'{median:.2f}',
                        xy=(position, median),
                        xytext=(position + 0.35, median),
                        bbox=dict(boxstyle='round,pad=0.3', edgecolor='black', facecolor='white'),
                        color='black',
                        ha='center',
                        va='center')

        # Plot each endpoint
        for i, endpoint in enumerate(endpoints):
            ax = axs[i]

            # Filter data for each endpoint
            data_standard = \
            df_duration[(df_duration['endpoint'] == endpoint) & (df_duration['configuration'] == 'standard')][
                'metric_value']
            data_elastic = \
            df_duration[(df_duration['endpoint'] == endpoint) & (df_duration['configuration'] == 'elastic')][
                'metric_value']
            data_otel = df_duration[(df_duration['endpoint'] == endpoint) & (df_duration['configuration'] == 'otel')][
                'metric_value']

            # Combined boxplot for the current endpoint
            boxplot_data = [data_standard.dropna(), data_elastic.dropna(), data_otel.dropna()]
            bplot = ax.boxplot(boxplot_data, labels=['Non-\nInstrumented', 'Elastic APM\nInstrumented',
                                                     'OpenTelemetry\nInstrumented'], patch_artist=True,
                               showfliers=False)

            # Set colors
            for patch, color in zip(bplot['boxes'], colors):
                patch.set_facecolor(color)

            for median in bplot['medians']:
                median.set_color('black')

            # Add grid
            ax.yaxis.grid(True, linestyle='--', which='major', color='grey', alpha=0.5)

            # Annotate the medians
            annotate_median(ax, data_standard, 1)
            annotate_median(ax, data_elastic, 2)
            annotate_median(ax, data_otel, 3)

            # Set titles and labels
            ax.set_title(f'Endpoint: {endpoint}')
            ax.set_ylabel('Request Duration (ms)', fontsize=22)

        # fig.suptitle('HTTP Request Duration by Endpoint and Configuration')
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plot_name = "aggregated_plot_endpoints.png"
        plt.savefig(plot_name)
        plt.close(fig)

    def create_statistics_table_by_language(self):
        # Load the dataset
        df = self.data

        # Filter the dataframe for the metric_name 'http_req_duration'
        df_duration = df[df['metric_name'] == 'http_req_duration']

        # Ensure the 'metadata' column is of string type
        df_duration['extra_tags'] = df_duration['extra_tags'].astype(str)

        # Extract the programming language from the 'extra_tags' column
        df_duration['language'] = df_duration['extra_tags'].str.extract(r'language=(python|java|go)')[0]

        # Extract the endpoint from the URL
        df_duration['endpoint'] = df_duration['url'].str.extract(r'(http://[^/]+(/[^?]*))')[1]

        # Group by language
        grouped = df_duration.groupby(['language'])

        # Calculate statistics for each group
        stats = grouped['metric_value'].agg(
            mean='mean',
            min='min',
            median='median',
            q90=lambda x: x.quantile(0.90),
            q95=lambda x: x.quantile(0.95),
            q99=lambda x: x.quantile(0.99),
            max='max'
        ).reset_index()

        stats = stats.round(2)

        # Rename columns for better readability
        stats.columns = [
            'Language',
            'Mean',
            'Min',
            'Median',
            'p90',
            'p95',
            'p99',
            'Max'
        ]

        return stats

    def create_statistics_table_languages(self):
        # Load the dataset
        # Assuming self.data is a pandas DataFrame already loaded with the necessary data

        # Filter the dataframe for the metric_name 'http_req_duration'
        df_duration = self.data[self.data['metric_name'] == 'http_req_duration']

        # Ensure the 'extra_tags' column is of string type
        df_duration['extra_tags'] = df_duration['extra_tags'].astype(str)

        # Extract the configurations from the 'extra_tags' column
        df_duration['configuration'] = df_duration['extra_tags'].str.extract(r'(standard|elastic|otel)')

        # Extract the programming languages from the 'extra_tags' column
        df_duration['language'] = df_duration['extra_tags'].str.extract(r'(go|java|python)')

        # Define a helper function to calculate the statistics
        def calculate_statistics(data):
            return {
                'median': data.median(),
                'mean': data.mean(),
                'max': data.max(),
                'min': data.min(),
                'p90': data.quantile(0.90),
                'p95': data.quantile(0.95),
                'p99': data.quantile(0.99)
            }

        # Initialize an empty list to store the results
        results = []

        # Iterate over each language
        for language in df_duration['language'].unique():
            # Filter the dataframe for the current language
            df_lang = df_duration[df_duration['language'] == language]

            # Calculate statistics for each configuration
            stats_standard = calculate_statistics(df_lang[df_lang['configuration'] == 'standard']['metric_value'])
            stats_elastic = calculate_statistics(df_lang[df_lang['configuration'] == 'elastic']['metric_value'])
            stats_otel = calculate_statistics(df_lang[df_lang['configuration'] == 'otel']['metric_value'])

            # Append the results to the list
            results.append(['Standard', language.capitalize(), stats_standard['median'], stats_standard['mean'],
                            stats_standard['max'], stats_standard['min'], stats_standard['p90'], stats_standard['p95'],
                            stats_standard['p99']])
            results.append(
                ['Elastic', language.capitalize(), stats_elastic['median'], stats_elastic['mean'], stats_elastic['max'],
                 stats_elastic['min'], stats_elastic['p90'], stats_elastic['p95'], stats_elastic['p99']])
            results.append(['Otel', language.capitalize(), stats_otel['median'], stats_otel['mean'], stats_otel['max'],
                            stats_otel['min'], stats_otel['p90'], stats_otel['p95'], stats_otel['p99']])

        # Create a dataframe to display the results
        stats_df = pd.DataFrame(results,
                                columns=['Configuration', 'Language', 'Median', 'Mean', 'Max', 'Min', 'P90', 'P95',
                                         'P99'])

        stats_df = stats_df.round(2)

        return stats_df

