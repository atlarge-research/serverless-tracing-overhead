import os
import json
import numpy as np
import pandas as pd
from utils import get_benchmark_time


def scrub_benchmark_name(benchmark_name):
    # Remove the number in front and keep the benchmark name
    scrubbed_name = benchmark_name.split('.', 1)[1]
    # Remove the words "opentelemetry" and "otel"
    scrubbed_name = scrubbed_name.replace('-opentelemetry', '').replace('-otel', '')
    return scrubbed_name.strip()

def determine_configuration(benchmark_name):
    # Determine the configuration based on the benchmark number
    benchmark_number = int(benchmark_name.split('.')[0])
    if benchmark_number < 600:
        return 'non-instrumented'
    else:
        return 'instrumented'

def parse_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Extracting benchmark and client values
    benchmark_values = []
    client_values = []
    benchmark_name = data.get('config', {}).get('experiments', {}).get('experiments', {}).get('perf-cost', {}).get('benchmark')
    scrubbed_benchmark_name = scrub_benchmark_name(benchmark_name)
    configuration = determine_configuration(benchmark_name)
    language = data.get('config', {}).get('experiments', {}).get('runtime', {}).get('language')

    invocations = data.get('_invocations', {})
    for bench_name, executions in invocations.items():
        for execution_id, execution_data in executions.items():
            times = execution_data.get('times', {})
            benchmark_values.append(get_benchmark_time(times))
            client_values.append(times.get('client'))

    # Convert lists to numpy arrays and from microseconds to milliseconds
    benchmark_values = np.array(benchmark_values) / 1000.0
    client_values = np.array(client_values) / 1000.0

    # Calculate statistics and round to two decimal places
    benchmark_stats = {
        'mean': round(np.mean(benchmark_values), 2),
        'median': round(np.median(benchmark_values), 2),
        'std': round(np.std(benchmark_values), 2),
        'benchmark_name': scrubbed_benchmark_name,
        'configuration': configuration,
        'language': language
    }

    client_stats = {
        'mean': round(np.mean(client_values), 2),
        'median': round(np.median(client_values), 2),
        'std': round(np.std(client_values), 2),
        'benchmark_name': scrubbed_benchmark_name,
        'configuration': configuration,
        'language': language
    }

    return benchmark_stats, client_stats

def parse_all_json_files(directory):
    benchmark_data = []
    client_data = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                benchmark_stats, client_stats = parse_json(file_path)
                benchmark_data.append(benchmark_stats)
                client_data.append(client_stats)

    benchmark_df = pd.DataFrame(benchmark_data)
    client_df = pd.DataFrame(client_data)

    return benchmark_df, client_df

# Paths to the directories
python_dir = 'results-json/python'
nodejs_dir = 'results-json/nodejs'

# Parse JSON files and create dataframes
python_benchmark_df, python_client_df = parse_all_json_files(python_dir)
nodejs_benchmark_df, nodejs_client_df = parse_all_json_files(nodejs_dir)

# Combine dataframes from both directories
benchmark_df = pd.concat([python_benchmark_df, nodejs_benchmark_df], ignore_index=True)
client_df = pd.concat([python_client_df, nodejs_client_df], ignore_index=True)

# Reorder rows by benchmark name
benchmark_df = benchmark_df.sort_values(by='benchmark_name').reset_index(drop=True)
client_df = client_df.sort_values(by='benchmark_name').reset_index(drop=True)

# Display the dataframes
print("Benchmark Times")
print(benchmark_df)
print("\nClient Times")
print(client_df)