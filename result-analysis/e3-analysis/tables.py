import os
import pandas as pd

ITERATIONS_NUMBER = "100000"


def get_experiment_name(filename):
    split_filename = filename.split("_")
    if split_filename[1] == ITERATIONS_NUMBER:
        experiment_name = split_filename[0]
    else:
        experiment_name = f"{split_filename[0]}-{split_filename[1]}"
    return experiment_name

def create_compact_table(directory):
    table_data = []

    for filename in os.listdir(directory):
        if "aggregated_statistics" in filename and filename.endswith(".csv"):
            experiment_name = get_experiment_name(filename)

            file_path = os.path.join(directory, filename)
            df = pd.read_csv(file_path)

            total_avg_time = df.loc[df['Function'] == 'total', 'Average Time (ms)'].values[0]
            total_median_time = df.loc[df['Function'] == 'total', 'Median Time (ms)'].values[0]

            avg_percent_time = {
                'Configuration': df.loc[df['Function'] == 'configuration', 'Average % of Total Time'].values[0],
                'Task': df.loc[df['Function'] == 'task', 'Average % of Total Time'].values[0],
                'Export': df.loc[df['Function'] == 'export', 'Average % of Total Time'].values[0],
                'Instrumentation': df.loc[df['Function'] == 'instrumentation', 'Average % of Total Time'].values[0],
            }

            table_data.append({
                'Experiment': experiment_name,
                'Avg. Time (ms)': round(total_avg_time, 2),
                'Median (ms)': round(total_median_time, 2),
                'Configuration (%)': round(avg_percent_time['Configuration'], 2),
                'Instrumentation (%)': round(avg_percent_time['Instrumentation'], 2),
                'Export (%)': round(avg_percent_time['Export'], 2),
                'Task (%)': round(avg_percent_time['Task'], 2),
            })

    table_df = pd.DataFrame(table_data)

    table_df = table_df[['Experiment',
                         'Avg. Time (ms)',
                         'Median (ms)',
                         'Configuration (%)',
                         'Instrumentation (%)',
                         'Export (%)',
                         'Task (%)']]

    return table_df
def process_experiment_statistics(directory):
    # List to hold the data from all files
    data_list = []

    # Loop through all files in the directory
    for filename in os.listdir(directory):
        if "aggregated_statistics" in filename and filename.endswith(".csv"):
            # Extract the experiment name from the filename
            experiment_name = get_experiment_name(filename)

            file_path = os.path.join(directory, filename)
            df = pd.read_csv(file_path)

            # Add a column for the experiment name
            df["Experiment"] = experiment_name

            # Append the DataFrame to the list
            data_list.append(df)

    # Concatenate all DataFrames in the list into a single DataFrame
    consolidated_df = pd.concat(data_list, ignore_index=True)

    # Reorder the columns to have 'Experiment' first
    consolidated_df = consolidated_df[['Experiment', 'Function', 'Average Time (ms)', 'Median Time (ms)',
                                       '95th Percentile (ms)', '99th Percentile (ms)', 'Average % of Total Time']]

    return consolidated_df


def save_table(df, output_file):
    os.makedirs("tables", exist_ok=True)
    print(f"Table saved to tables/{output_file}")
    df.to_csv(f"tables/{output_file}", index=False)


if __name__ == "__main__":
    # Specify the directory containing the CSV files
    directory = "output"

    consolidated_df = process_experiment_statistics(directory)
    compact_table_df = create_compact_table(directory)

    # Specify the output file name
    output_file = "consolidated_experiment_statistics.csv"

    # Save the consolidated DataFrame to a CSV file
    save_table(consolidated_df, "consolidated_experiment_statistics.csv")
    save_table(compact_table_df, "compact_table.csv")

