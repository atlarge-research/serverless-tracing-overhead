import os
import json
import pandas as pd
from utils import get_benchmark_time

PYTHON_DIR = 'results-json/python'
NODEJS_DIR = 'results-json/nodejs'

def scrub_benchmark_name(benchmark_name):
    scrubbed_name = benchmark_name.split('.', 1)[1]
    scrubbed_name = scrubbed_name.replace('-opentelemetry', '').replace('-otel', '')
    return scrubbed_name.strip()

def determine_configuration(benchmark_name):
    benchmark_number = int(benchmark_name.split('.')[0])
    if benchmark_number < 600:
        return 'non-instrumented'
    else:
        return 'instrumented'

def parse_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    benchmark_name = data.get('config', {}).get('experiments', {}).get('experiments', {}).get('perf-cost', {}).get('benchmark')
    scrubbed_benchmark_name = scrub_benchmark_name(benchmark_name)
    configuration = determine_configuration(benchmark_name)
    language = data.get('config', {}).get('experiments', {}).get('runtime', {}).get('language')

    invocations = data.get('_invocations', {})
    times_data = []
    for bench_name, executions in invocations.items():
        for execution_id, execution_data in executions.items():
            times = execution_data.get('times', {})
            times_data.append({
                'benchmark_name': scrubbed_benchmark_name,
                'configuration': configuration,
                'language': language,
                'benchmark_time': get_benchmark_time(times) / 1000.0,  # Convert to milliseconds
                'client_time': times.get('client') / 1000.0  # Convert to milliseconds
            })

    return pd.DataFrame(times_data)

def parse_all_json_files(directory):
    all_times_data = pd.DataFrame()

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                times_data_df = parse_json(file_path)
                all_times_data = pd.concat([all_times_data, times_data_df], ignore_index=True)

    return all_times_data

def aggregate_times_data(df):
    aggregation = {
        'benchmark_time': ['mean', 'std'],
        'client_time': ['mean', 'std']
    }
    agg_df = df.groupby(['benchmark_name', 'configuration']).agg(aggregation).reset_index()
    agg_df.columns = ['benchmark_name', 'configuration', 'benchmark_time_mean', 'benchmark_time_std', 'client_time_mean', 'client_time_std']

    # Round the results to two decimals
    agg_df = agg_df.round({'benchmark_time_mean': 2, 'benchmark_time_std': 2, 'client_time_mean': 2, 'client_time_std': 2})

    return agg_df
