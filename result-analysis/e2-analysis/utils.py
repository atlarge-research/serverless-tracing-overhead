import os
import json
import numpy as np
import pandas as pd

# Some records are reported as 0
def get_benchmark_time(times):
    value = times.get('benchmark')
    if value == 0:
        value = 1000
    return value

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
    benchmark_name = data.get('config', {}).get('experiments', {}).get('experiments', {}).get('perf-cost', {}).get(
        'benchmark')
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


def create_comparison_table(df, time_type='benchmark'):
    comparison_data = []

    for language in df['language'].unique():
        for benchmark_name in df['benchmark_name'].unique():
            non_instrumented = df[(df['benchmark_name'] == benchmark_name) &
                                  (df['configuration'] == 'non-instrumented') &
                                  (df['language'] == language)]
            instrumented = df[(df['benchmark_name'] == benchmark_name) &
                              (df['configuration'] == 'instrumented') &
                              (df['language'] == language)]

            if not non_instrumented.empty and not instrumented.empty:
                non_instrumented_mean = non_instrumented[f'mean'].values[0]
                instrumented_mean = instrumented[f'mean'].values[0]
                overhead_percentage = ((instrumented_mean - non_instrumented_mean) / non_instrumented_mean) * 100

                comparison_data.append({
                    'benchmark_name': benchmark_name,
                    'language': language,
                    'non_instrumented_mean': non_instrumented_mean,
                    'instrumented_mean': instrumented_mean,
                    'overhead_percentage': round(overhead_percentage, 2)
                })

    return pd.DataFrame(comparison_data)

def compare_performance_variation(python_dir, nodejs_dir, time_type='benchmark'):
    benchmark_python_df, client_python_df = parse_all_json_files(python_dir)
    benchmark_nodejs_df, client_nodejs_df = parse_all_json_files(nodejs_dir)

    if time_type == 'benchmark':
        df = pd.concat([benchmark_python_df, benchmark_nodejs_df], ignore_index=True)
    elif time_type == 'client':
        df = pd.concat([client_python_df, client_nodejs_df], ignore_index=True)
    else:
        raise ValueError("Invalid time_type. Must be either 'benchmark' or 'client'.")

    df = df.sort_values(by='benchmark_name').reset_index(drop=True)

    comparison_df = create_comparison_table(df, time_type)

    variation_data = []

    for benchmark_name in comparison_df['benchmark_name'].unique():
        benchmark_data = comparison_df[comparison_df['benchmark_name'] == benchmark_name]

        if not benchmark_data.empty:
            mean_overhead = benchmark_data['overhead_percentage'].mean()
            std_overhead = benchmark_data['overhead_percentage'].std()
            min_overhead = benchmark_data['overhead_percentage'].min()
            max_overhead = benchmark_data['overhead_percentage'].max()

            python_overhead = benchmark_data[benchmark_data['language'] == 'python']['overhead_percentage'].values[0] if not benchmark_data[benchmark_data['language'] == 'python'].empty else None
            nodejs_overhead = benchmark_data[benchmark_data['language'] == 'nodejs']['overhead_percentage'].values[0] if not benchmark_data[benchmark_data['language'] == 'nodejs'].empty else None

            variation_data.append({
                'benchmark_name': benchmark_name,
                'mean_overhead_percentage': round(mean_overhead, 2),
                'std_overhead_percentage': round(std_overhead, 2),
                'min_overhead_percentage': round(min_overhead, 2),
                'max_overhead_percentage': round(max_overhead, 2),
                'python_overhead_percentage': round(python_overhead, 2) if python_overhead is not None else None,
                'nodejs_overhead_percentage': round(nodejs_overhead, 2) if nodejs_overhead is not None else None
            })

    variation_df = pd.DataFrame(variation_data)

    return variation_df


# Paths to the directories
PYTHON_DIR = 'results-json-newer/python'
NODEJS_DIR = 'results-json-newer/nodejs'


# Reorder rows by benchmark name
# benchmark_df = benchmark_df.sort_values(by='benchmark_name').reset_index(drop=True)
# client_df = client_df.sort_values(by='benchmark_name').reset_index(drop=True)
