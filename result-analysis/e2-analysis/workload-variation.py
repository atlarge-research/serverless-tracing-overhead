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

def compare_performance_variation(python_dir, nodejs_dir, time_type='benchmark'):
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

    # Calculate the variation in performance impact across different types of benchmarks
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
                # 'std_overhead_percentage': round(std_overhead, 2),
                # 'min_overhead_percentage': round(min_overhead, 2),
                # 'max_overhead_percentage': round(max_overhead, 2),
                'python_overhead_percentage': round(python_overhead, 2) if python_overhead is not None else None,
                'nodejs_overhead_percentage': round(nodejs_overhead, 2) if nodejs_overhead is not None else None
            })

    variation_df = pd.DataFrame(variation_data)

    return variation_df

benchmark_variation_df = compare_performance_variation(PYTHON_DIR, NODEJS_DIR, 'benchmark')
client_variation_df = compare_performance_variation(PYTHON_DIR, NODEJS_DIR, 'client')

print("\nBenchmark")
print(benchmark_variation_df)
print("\nClient")
print(client_variation_df)