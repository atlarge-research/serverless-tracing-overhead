import pandas as pd
from utils import parse_all_json_files, PYTHON_DIR, NODEJS_DIR

python_benchmark_df, python_client_df = parse_all_json_files(PYTHON_DIR)
nodejs_benchmark_df, nodejs_client_df = parse_all_json_files(NODEJS_DIR)

benchmark_df = pd.concat([python_benchmark_df, nodejs_benchmark_df], ignore_index=True)
client_df = pd.concat([python_client_df, nodejs_client_df], ignore_index=True)

def get_comparison_df(df):
    comparison_data = []

    for language in df['language'].unique():
        for benchmark_name in df['benchmark_name'].unique():
            non_instrumented = df[(df['benchmark_name'] == benchmark_name) &
                                            (df['configuration'] == 'non-instrumented') &
                                            (df['language'] == language)]
            instrumented = df[(benchmark_df['benchmark_name'] == benchmark_name) &
                                        (df['configuration'] == 'instrumented') &
                                        (df['language'] == language)]

            if not non_instrumented.empty and not instrumented.empty:
                non_instrumented_mean = non_instrumented['mean'].values[0]
                instrumented_mean = instrumented['mean'].values[0]
                overhead_percentage = ((instrumented_mean - non_instrumented_mean) / non_instrumented_mean) * 100

                comparison_data.append({
                    'benchmark_name': benchmark_name,
                    'language': language,
                    'non_instrumented_mean': non_instrumented_mean,
                    'instrumented_mean': instrumented_mean,
                    'overhead_percentage': round(overhead_percentage, 2)
                })

    return pd.DataFrame(comparison_data)

# Display the comparison dataframe
benchmark_comparison_df = get_comparison_df(benchmark_df)
client_comparison_df = get_comparison_df(client_df)
print("\nBenchmark")
print(benchmark_comparison_df)
print("\nClient")
print(client_comparison_df)