import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

path = '../results/2024-04-03/json_2024-04-03_16-51.csv'
PLOTS_DIR = "plots"

class K6Statistics:
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path
        self.file_name = csv_file_path.split('/')[-1]
        self.data = pd.read_csv(csv_file_path)

        # Data
        self.throughput_data = self.data[self.data['metric_name'] == 'http_reqs']
        self.performance_data = self.data[self.data['metric_name'] == 'http_req_duration']
        self.requests_per_second = self.data[self.data['metric_name'] == 'http_reqs'][
            'timestamp'].value_counts().sort_index()
        self.http_req_durations = self.data[self.data['metric_name'] == 'http_req_duration']['metric_value']

    def save_or_show_plot(self, save_plot):
        if not os.path.exists(PLOTS_DIR):
            os.makedirs(PLOTS_DIR)
        if save_plot:
            plt.savefig('{}/{}'.format(PLOTS_DIR, self.file_name.replace(".csv", ".png")))
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
        combined_pivot['total_requests'] = combined_pivot[['successful', 'failed']].sum(axis=1)

        # Order the columns
        # column_order = ['successful', 'failed', 'total_requests']
        # combined_pivot = combined_pivot[column_order]

        combined_pivot = combined_pivot.round(3)

        print(combined_pivot)
        if save_csv:
            combined_pivot.to_csv("metrics/{}-detailed-metrics.csv".format(self.file_name.replace(".csv", "")))

    # Throughput
    def plot_throughput(self, save_plot=True):
        plt.figure(figsize=(12, 6))
        plt.plot(self.throughput_data['timestamp'], self.throughput_data['metric_value'].cumsum(), marker='o',
                 linestyle='-',
                 label='Throughput')
        plt.xlabel('Timestamp')
        plt.ylabel('Cumulative Requests')
        plt.title('Throughput Over Time')
        plt.legend()
        plt.grid(True)
        self.save_or_show_plot(save_plot)

    # Performance. Can also select specific scenarios
    def plot_request_performance(self, included_scenarios=None, save_plot=True):

        # Filter out relevant metrics for plotting
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
            self.save_or_show_plot(save_plot)

    # Transfer Rate
    def plot_transfer_rate(self, save_plot=True):
        plt.figure(figsize=(10, 6))
        self.requests_per_second.plot(kind='bar')
        plt.xlabel('Timestamp')
        plt.ylabel('Requests per Second')
        plt.title('Transfer Rate Over Time')
        self.save_or_show_plot(save_plot)

    # HTTP Request Duration
    def plot_http_request_duration(self, save_plot=True):
        plt.figure(figsize=(10, 6))
        durations_summary = pd.DataFrame({
            'Metrics': ['Average', 'P90', 'P95', 'P99'],
            'Duration (ms)': [
                self.http_req_durations.mean(),
                self.http_req_durations.quantile(0.9),
                self.http_req_durations.quantile(0.95),
                self.http_req_durations.quantile(0.99),
            ]
        })

        durations_summary.plot(x='Metrics', y='Duration (ms)', kind='bar', legend=False)
        plt.xticks(rotation=0)
        plt.ylabel('Duration (ms)')
        plt.title('HTTP Request Duration Metrics')
        self.save_or_show_plot(save_plot)

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

    def calculate_overhead(self, scenarios, metrics_of_interest=None):
        """
        Calculate and plot the average values of specified metrics for multiple scenarios, and print a table of these averages.

        Parameters:
        - csv_file: Path to the CSV file containing the data.
        - scenarios: A list of scenarios to compare (e.g., ['python_4096', 'python-otel_4096', 'another_scenario']).
        - metrics_of_interest: List of metrics to compare. If None, a default list is used.
        """
        if metrics_of_interest is None:
            # Longer list
            # metrics_of_interest = ['http_req_blocked', 'http_req_connecting', 'http_req_duration',
            #                        'http_req_receiving', 'http_req_sending', 'http_req_tls_handshaking',
            #                        'http_req_waiting', 'iteration_duration']
            # Shorter list
            metrics_of_interest = ['http_req_duration', 'http_req_waiting', 'iteration_duration']

        averages_list = []
        for scenario in scenarios:
            scenario_df = self.data[(self.data['scenario'] == scenario) & (self.data['metric_name'].isin(metrics_of_interest))]
            averages = scenario_df.groupby('metric_name')['metric_value'].mean().rename(f'Average_{scenario}')
            averages_list.append(averages)

        comparison_df = pd.concat(averages_list, axis=1)

        # Display the DataFrame
        print(comparison_df.round(3))

        # Plotting
        labels = comparison_df.index
        x = np.arange(len(labels))
        width = 0.8 / len(scenarios)

        fig, ax = plt.subplots(figsize=(14, 8))
        for i, scenario in enumerate(scenarios):
            ax.bar(x + i * width, comparison_df[f'Average_{scenario}'], width, label=scenario)

        ax.set_xlabel('Metrics')
        ax.set_ylabel('Average Values (ms)')
        ax.set_title(f'Average Metric Values by Scenario')
        ax.set_xticks(x + width * (len(scenarios) - 1) / 2)
        ax.set_xticklabels(labels, rotation=45, ha="right")
        ax.legend()

        plt.grid(axis='y', linestyle='--')
        fig.tight_layout()

        plt.show()


if __name__ == "__main__":
    stats = K6Statistics(path)

    stats.show_metrics()
    stats.show_total_number_of_requests()
    stats.calculate_overhead(['python_512', 'pythonOtel_512'])
    stats.calculate_overhead(['go_512', 'goOtel_512'])

    # k6.plot_request_performance()
