import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np

# Set a global style for all plots
sns.set_style("whitegrid")
plt.rcParams.update({
    "font.size": 18,
    "axes.titlesize": 20,
    "axes.labelsize": 18,
    "xtick.labelsize": 18,
    "ytick.labelsize": 14,
    "legend.fontsize": 14,
    "figure.titlesize": 18
})

LABEL_SIZE = 20


def boxplot(df, output_file="boxplot.png"):
    # Prepare the data for the box plot with renamed columns
    time_columns = {
        "configuration Time (ms)": "Configuration",
        "task Time (ms)": "Task",
        "export Time (ms)": "Export",
        "instrumentation Time (ms)": "Instrumentation"
    }

    # Melt the DataFrame with the renamed columns
    df_melted = pd.melt(df, id_vars=["Run"], value_vars=list(time_columns.keys()),
                        var_name="Function", value_name="Time (ms)")

    # Apply the renaming
    df_melted["Function"] = df_melted["Function"].map(time_columns)

    # Create the box plot
    plt.figure(figsize=(10, 6))
    sns.boxplot(x="Function", y="Time (ms)", data=df_melted, palette="Set2", showfliers=False, width=0.5)
    # plt.title("Distribution of Function Times Across Runs", fontsize=16, weight='bold')
    plt.xlabel("Task name", fontsize=LABEL_SIZE)
    plt.ylabel("Time (ms)", fontsize=LABEL_SIZE)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the plot to a file
    plt.savefig(output_file)
    plt.close()


def lineplot(df, output_file="lineplot.png"):
    # Create the line chart
    plt.figure(figsize=(12, 8))
    # plt.plot(df["Run"], df["configuration Time (ms)"], label="Configuration Time (ms)", color="blue", marker='o')
    # plt.plot(df["Run"], df["task Time (ms)"], label="Task Time (ms)", color="orange", marker='o')
    # plt.plot(df["Run"], df["export Time (ms)"], label="Export Time (ms)", color="green", marker='o')
    # plt.plot(df["Run"], df["instrumentation Time (ms)"], label="Instrumentation Time (ms)", color="red", marker='o')

    plt.plot(df["Run"], df["configuration Time (ms)"], label="Configuration Time (ms)", color="blue")
    plt.plot(df["Run"], df["task Time (ms)"], label="Task Time (ms)", color="orange")
    plt.plot(df["Run"], df["export Time (ms)"], label="Export Time (ms)", color="green")
    plt.plot(df["Run"], df["instrumentation Time (ms)"], label="Instrumentation Time (ms)", color="red")
    # plt.plot(df["Run"], df["total Time (ms)"], label="Total Time (ms)", color="purple", marker='o')

    # Adding titles and labels
    # plt.title("Time Spent by Each Function Across Runs", fontsize=16, weight='bold')
    plt.xlabel("Run", fontsize=LABEL_SIZE)
    plt.ylabel("Time (ms)", fontsize=LABEL_SIZE)
    plt.legend(loc="best", frameon=True, shadow=True)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Save the plot to a file
    plt.savefig(output_file)
    plt.close()


def stacked_bar_chart(df, output_file="stacked_bar_chart.png"):
    # Extract relevant columns for percentage data
    runs = df["Run"]
    configuration_pct = df["configuration % of Total"]
    task_pct = df["task % of Total"]
    export_pct = df["export % of Total"]
    instrumentation_pct = df["instrumentation % of Total"]

    # Debugging: Print the first few rows to ensure the data is correct
    print("First few rows of the percentage data:")
    print(df.head())

    # Calculate the cumulative bottom positions for the stacking
    bottom_task = configuration_pct
    bottom_export = bottom_task + task_pct
    bottom_instrumentation = bottom_export + export_pct

    # Create the stacked bar chart
    plt.figure(figsize=(12, 8))
    plt.bar(runs, configuration_pct, label="Configuration % of Total", color='#4c72b0')
    plt.bar(runs, task_pct, bottom=bottom_task, label="Task % of Total", color='#55a868')
    plt.bar(runs, export_pct, bottom=bottom_export, label="Export % of Total", color='#c44e52')
    plt.bar(runs, instrumentation_pct, bottom=bottom_instrumentation,
            label="Instrumentation % of Total", color='#8172b2')

    # Adding titles and labels
    # plt.title("Percentage of Total Time by Function Across Runs", fontsize=16, weight='bold')
    plt.xlabel("Run", fontsize=LABEL_SIZE)
    plt.ylabel("Percentage of Total Time", fontsize=LABEL_SIZE)
    plt.legend(loc="upper right", frameon=True, shadow=True)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Save the plot to a file
    plt.savefig(output_file)
    plt.close()


def stacked_area_chart(df, output_file="stacked_area_chart.png"):
    # Take only the first 100 rows, otherwise the chart is unreadable
    df = df.head(100)

    # Calculate total time to normalize
    df['Total Time'] = df["configuration Time (ms)"] + df["task Time (ms)"] + df["export Time (ms)"] + df["instrumentation Time (ms)"]

    # Normalize each function's time by the total time to get percentages
    df['Configuration %'] = df["configuration Time (ms)"] / df['Total Time']
    df['Task %'] = df["task Time (ms)"] / df['Total Time']
    df['Export %'] = df["export Time (ms)"] / df['Total Time']
    df['Instrumentation %'] = df["instrumentation Time (ms)"] / df['Total Time']

    # Prepare data for stacked area plot
    categories = ['Configuration %', 'Task %', 'Export %', 'Instrumentation %']
    plt.figure(figsize=(12, 8))
    plt.stackplot(df["Run"], df[categories].T, labels=['Configuration', 'Task', 'Export', 'Instrumentation'],
                  colors=['blue', 'orange', 'green', 'red'], alpha=0.8)

    plt.xlabel("Iteration", fontsize=LABEL_SIZE)
    plt.ylabel("Percentage of Total Time", fontsize=LABEL_SIZE)

    # Position the legend outside the plot
    plt.legend(loc="upper left", bbox_to_anchor=(1.05, 1), borderaxespad=0., frameon=True, shadow=True)

    plt.tight_layout(rect=[0, 0, 1, 1])  # Adjust the layout to make room for the legend
    plt.savefig(output_file)
    plt.close()


def heatmap_all_times(df, output_file="heatmap_all_times.png"):
    df_heatmap = df[["configuration Time (ms)", "task Time (ms)", "export Time (ms)", "instrumentation Time (ms)"]]

    plt.figure(figsize=(10, 6))
    sns.heatmap(df_heatmap.corr(), annot=True, cmap='coolwarm', vmin=-1, vmax=1)
    plt.title("Correlation Heatmap of Function Times", fontsize=16, weight='bold')
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()


def radar_chart(df, output_file="radar_chart.png"):
    categories = ["Configuration", "Task", "Export", "Instrumentation"]
    num_vars = len(categories)

    # Compute max values for scaling
    max_values = [df["configuration Time (ms)"].max(),
                  df["task Time (ms)"].max(),
                  df["export Time (ms)"].max(),
                  df["instrumentation Time (ms)"].max()]

    # Scale data
    df_scaled = pd.DataFrame()
    df_scaled["Run"] = df["Run"]
    df_scaled["Configuration"] = df["configuration Time (ms)"] / max_values[0]
    df_scaled["Task"] = df["task Time (ms)"] / max_values[1]
    df_scaled["Export"] = df["export Time (ms)"] / max_values[2]
    df_scaled["Instrumentation"] = df["instrumentation Time (ms)"] / max_values[3]

    # Plot radar chart for each run
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]

    for i, row in df_scaled.iterrows():
        values = row.drop('Run').values.flatten().tolist()
        values += values[:1]  # Close the loop
        ax.plot(angles, values, label=f"Run {row['Run']}")
        ax.fill(angles, values, alpha=0.1)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    plt.title("Radar Chart of Function Times Across Runs", fontsize=16, weight='bold')
    plt.legend(loc="best", frameon=True, shadow=True)
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()


if __name__ == "__main__":
    dynamic_html_file = "output/dynamic-html_100000_each_run_results.csv"

    # Save each plot with a different name
    df = pd.read_csv(dynamic_html_file)

    boxplot(df, "plots/boxplot.png")
    lineplot(df, "plots/lineplot.png")
    stacked_area_chart(df, "plots/stacked_area_chart.png")

    # heatmap_all_times(df, "plots/heatmap.png")
    # radar_chart(df, "plots/radar.png")
    # stacked_bar_chart(dynamic_html_file, "plots/stacked_bar_chart.png")
