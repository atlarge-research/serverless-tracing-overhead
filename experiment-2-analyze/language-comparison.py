import pandas as pd
from utils import parse_all_json_files, PYTHON_DIR, NODEJS_DIR

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

def compare_tracing_overhead(python_dir, nodejs_dir, time_type='benchmark'):
    # Parse JSON files and create dataframes
    benchmark_python_df, client_python_df = parse_all_json_files(python_dir)
    benchmark_nodejs_df, client_nodejs_df = parse_all_json_files(nodejs_dir)

    # Select the appropriate dataframe based on time_type
    if time_type == 'benchmark':
        df = pd.concat([benchmark_python_df, benchmark_nodejs_df], ignore_index=True)
    elif time_type == 'client':
        df = pd.concat([client_python_df, client_nodejs_df], ignore_index=True)
    else:
        raise ValueError("Invalid time_type. Must be either 'benchmark' or 'client'.")

    # Reorder rows by benchmark name
    df = df.sort_values(by='benchmark_name').reset_index(drop=True)

    # Create comparison table
    comparison_df = create_comparison_table(df, time_type)

    # Calculate the differences in tracing overhead between Python and Node.js
    overhead_diff_data = []

    for benchmark_name in comparison_df['benchmark_name'].unique():
        python_data = comparison_df[(comparison_df['benchmark_name'] == benchmark_name) &
                                    (comparison_df['language'] == 'python')]
        nodejs_data = comparison_df[(comparison_df['benchmark_name'] == benchmark_name) &
                                    (comparison_df['language'] == 'nodejs')]

        if not python_data.empty and not nodejs_data.empty:
            python_overhead = python_data['overhead_percentage'].values[0]
            nodejs_overhead = nodejs_data['overhead_percentage'].values[0]
            overhead_diff = python_overhead - nodejs_overhead

            overhead_diff_data.append({
                'benchmark_name': benchmark_name,
                'python_overhead': python_overhead,
                'nodejs_overhead': nodejs_overhead,
                'diff': round(overhead_diff, 2)
            })

    return pd.DataFrame(overhead_diff_data)

# Example usage

benchmark_overhead_diff_df = compare_tracing_overhead(PYTHON_DIR, NODEJS_DIR, "benchmark")
client_overhead_diff_df = compare_tracing_overhead(PYTHON_DIR, NODEJS_DIR, "client")
print("\nBenchmark")
print(benchmark_overhead_diff_df)
print("\nClient")
print(client_overhead_diff_df)
