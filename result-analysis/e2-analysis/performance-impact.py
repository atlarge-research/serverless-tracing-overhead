import pandas as pd
from utils_performance import parse_all_json_files, aggregate_times_data, PYTHON_DIR, NODEJS_DIR

def create_aggregated_table():
    # Parse JSON files and create dataframes
    times_data_python = parse_all_json_files(PYTHON_DIR)
    times_data_nodejs = parse_all_json_files(NODEJS_DIR)
    times_data = pd.concat([times_data_python, times_data_nodejs], ignore_index=True)

    # Aggregate times data
    aggregated_data = aggregate_times_data(times_data)
    print(aggregated_data)

    # Calculate p99 values for the grouped data
    p99_aggregated_data = aggregated_data.groupby(['benchmark_name', 'configuration']).quantile(0.99).reset_index()

    # Pivot the data to have instrumented and non-instrumented as columns
    pivoted_data = p99_aggregated_data.pivot(index='benchmark_name', columns='configuration')

    # Flatten the MultiIndex columns
    pivoted_data.columns = ['_'.join(col).strip() for col in pivoted_data.columns.values]

    # Reset index to turn the pivoted index back into a column
    pivoted_data.reset_index(inplace=True)

    # Reorganize the DataFrame to include metric types
    benchmark_columns = ['benchmark_name', 'benchmark_time_mean_instrumented', 'benchmark_time_p99_instrumented',
                         'benchmark_time_mean_non-instrumented', 'benchmark_time_p99_non-instrumented']
    client_columns = ['benchmark_name', 'client_time_mean_instrumented', 'client_time_p99_instrumented',
                      'client_time_mean_non-instrumented', 'client_time_p99_non-instrumented']

    benchmark_df = pivoted_data[benchmark_columns].copy()
    benchmark_df['Metric'] = 'Benchmark Time'

    client_df = pivoted_data[client_columns].copy()
    client_df['Metric'] = 'Client Time'

    benchmark_df.columns = ['Benchmark Name', 'Mean (Instrumented)', 'P99 (Instrumented)',
                            'Mean (Non-Instrumented)', 'P99 (Non-Instrumented)', 'Metric']
    client_df.columns = ['Benchmark Name', 'Mean (Instrumented)', 'P99 (Instrumented)',
                         'Mean (Non-Instrumented)', 'P99 (Non-Instrumented)', 'Metric']

    combined_df = pd.concat([benchmark_df, client_df], ignore_index=True)

    return combined_df

# Generate the table
aggregated_table = create_aggregated_table()
print(aggregated_table.to_string(index=False))

# Save the table to a CSV file
aggregated_table.to_csv('aggregated_benchmark_client_times.csv', index=False)
