import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

path = '../results/2024-03-27/python_2024-03-27_00-37.csv'


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

    def save_show_plot(self, save_plot):
        if save_plot:
            plt.savefig('plots/{}'.format(self.file_name))
        else:
            plt.show()

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
        self.save_show_plot(save_plot)

    # Performance
    def plot_performance(self, save_plot=True):
        plt.figure(figsize=(12, 6))
        plt.plot(self.performance_data['timestamp'], self.performance_data['metric_value'], marker='x', linestyle='-',
                 label='Request Duration')
        plt.xlabel('Timestamp')
        plt.ylabel('Request Duration (Unit)')
        plt.title('App Performance Over Time')
        plt.legend()
        plt.grid(True)
        self.save_show_plot(save_plot)

    # Transfer Rate
    def plot_transfer_rate(self, save_plot=True):
        plt.figure(figsize=(10, 6))
        self.requests_per_second.plot(kind='bar')
        plt.xlabel('Timestamp')
        plt.ylabel('Requests per Second')
        plt.title('Transfer Rate Over Time')
        self.save_show_plot(save_plot)

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
        self.save_show_plot(save_plot)

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


if __name__ == "__main__":
    k6 = K6Statistics(path)

    k6.show_metrics()
