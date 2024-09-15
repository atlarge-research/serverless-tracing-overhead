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
    benchmark_times = []
    for bench_name, executions in invocations.items():
        for execution_id, execution_data in executions.items():
            times = execution_data.get('times', {})
            benchmark_times.append({
                'benchmark_name': scrubbed_benchmark_name,
                'configuration': configuration,
                'language': language,
                'benchmark_time': get_benchmark_time(times) / 1000.0  # Convert to milliseconds
            })

    return pd.DataFrame(benchmark_times)

def parse_all_json_files(directory):
    all_benchmark_times = pd.DataFrame()

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                benchmark_times_df = parse_json(file_path)
                all_benchmark_times = pd.concat([all_benchmark_times, benchmark_times_df], ignore_index=True)

    return all_benchmark_times

def aggregate_benchmark_data(df):
    return df.groupby(['benchmark_name', 'configuration', 'language']).agg(
        mean_benchmark_time=pd.NamedAgg(column='benchmark_time', aggfunc='mean'),
        std_benchmark_time=pd.NamedAgg(column='benchmark_time', aggfunc='std')
    ).reset_index()
