import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import os

# Set a global style for all plots
sns.set_style("whitegrid")
plt.rcParams.update({
    "font.size": 20,
    "axes.titlesize": 22,
    "axes.labelsize": 22,
    "xtick.labelsize": 20,
    "ytick.labelsize": 20,
    "legend.fontsize": 20,
    "figure.titlesize": 20
})

LABEL_SIZE = 20


def boxplot(df, output_file="boxplot.png"):
    time_columns = {
        "configuration Time (ms)": "Configuration",
        "task Time (ms)": "Task",
        "export Time (ms)": "Export",
        "instrumentation Time (ms)": "Instrumentation"
    }

    df_melted = pd.melt(df, id_vars=["Run"], value_vars=list(time_columns.keys()),
                        var_name="Function", value_name="Time (ms)")

    df_melted["Function"] = df_melted["Function"].map(time_columns)

    plt.figure(figsize=(10, 6))
    sns.boxplot(x="Function", y="Time (ms)", data=df_melted, palette="Set2", showfliers=False, width=0.5)
    plt.xlabel("Task name", fontsize=LABEL_SIZE)
    plt.ylabel("Time (ms)", fontsize=LABEL_SIZE)
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig(output_file, bbox_inches='tight')
    plt.close()


def lineplot(df, output_file="lineplot.png"):
    # Create the line chart
    plt.figure(figsize=(12, 8))
    # plt.plot(df["Run"], df["configuration Time (ms)"], label="Configuration Time (ms)", color="blue", marker='o')
    # plt.plot(df["Run"], df["task Time (ms)"], label="Task Time (ms)", color="orange", marker='o')
    # plt.plot(df["Run"], df["export Time (ms)"], label="Export Time (ms)", color="green", marker='o')
    # plt.plot(df["Run"], df["instrumentation Time (ms)"], label="Instrumentation Time (ms)", color="red", marker='o')
    plt.plot(df["Run"], df["configuration Time (ms)"], label="Configuration Time (ms)", color="mediumslateblue")
    plt.plot(df["Run"], df["instrumentation Time (ms)"], label="Instrumentation Time (ms)", color="mediumseagreen")
    plt.plot(df["Run"], df["export Time (ms)"], label="Export Time (ms)", color="coral")
    plt.plot(df["Run"], df["task Time (ms)"], label="Task Time (ms)", color="lightskyblue")

    plt.xlabel("Run", fontsize=LABEL_SIZE)
    plt.ylabel("Time (ms)", fontsize=LABEL_SIZE)
    plt.legend(loc="best", frameon=True, shadow=True)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()

    plt.savefig(output_file, bbox_inches='tight')
    plt.close()


def stacked_bar_chart(df, output_file="stacked_bar_chart.png"):
    runs = df["Run"]
    configuration_pct = df["configuration % of Total"]
    task_pct = df["task % of Total"]
    export_pct = df["export % of Total"]
    instrumentation_pct = df["instrumentation % of Total"]

    bottom_task = configuration_pct
    bottom_export = bottom_task + task_pct
    bottom_instrumentation = bottom_export + export_pct

    plt.figure(figsize=(12, 8))
    plt.bar(runs, configuration_pct, label="Configuration % of Total", color='#4c72b0')
    plt.bar(runs, task_pct, bottom=bottom_task, label="Task % of Total", color='#55a868')
    plt.bar(runs, export_pct, bottom=bottom_export, label="Export % of Total", color='#c44e52')
    plt.bar(runs, instrumentation_pct, bottom=bottom_instrumentation,
            label="Instrumentation % of Total", color='#8172b2')

    plt.xlabel("Run", fontsize=LABEL_SIZE)
    plt.ylabel("Percentage of Total Time", fontsize=LABEL_SIZE)
    plt.legend(loc="upper right", frameon=True, shadow=True)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()

    plt.savefig(output_file, bbox_inches='tight')
    plt.close()


def stacked_area_chart(df, output_file="stacked_area_chart.png"):
    # df = df.head(250)
    start = 100
    end = 200
    range_size = end - start
    range_list = range(0, range_size)

    df = df.loc[start:end-1]

    df['Total Time'] = df["configuration Time (ms)"] + df["instrumentation Time (ms)"] + df["export Time (ms)"] + df["task Time (ms)"]

    df['Configuration %'] = df["configuration Time (ms)"] / df['Total Time']
    df['Instrumentation %'] = df["instrumentation Time (ms)"] / df['Total Time']
    df['Export %'] = df["export Time (ms)"] / df['Total Time']
    df['Task %'] = df["task Time (ms)"] / df['Total Time']

    categories = ['Configuration %', 'Instrumentation %', 'Export %', 'Task %']
    plt.figure(figsize=(12, 8))
    plt.stackplot(range_list, df[categories].T, labels=['Configuration', 'Instrumentation', 'Export', 'Task'],
                  colors=['mediumslateblue', 'mediumseagreen', 'coral', 'lightskyblue'], alpha=0.8)

    plt.xlabel("Iteration", fontsize=LABEL_SIZE)
    plt.ylabel("Percentage of Total Time", fontsize=LABEL_SIZE)

    plt.xlim(0, range_size)
    plt.ylim(0, 1)
    plt.xticks(ticks=range(0, range_size + 1, 20), labels=range(0, range_size + 1, 20))

    plt.legend(loc="upper left", bbox_to_anchor=(1.01, 1), borderaxespad=0., frameon=True, shadow=True)

    plt.tight_layout(rect=[0, 0, 1, 1])  # Adjust the layout to make room for the legend
    plt.savefig(output_file, bbox_inches='tight')
    plt.close()


def heatmap_all_times(df, output_file="heatmap_all_times.png"):
    df_heatmap = df[["configuration Time (ms)", "task Time (ms)", "export Time (ms)", "instrumentation Time (ms)"]]

    plt.figure(figsize=(10, 6))
    sns.heatmap(df_heatmap.corr(), annot=True, cmap='coolwarm', vmin=-1, vmax=1)
    plt.title("Correlation Heatmap of Function Times", fontsize=16, weight='bold')
    plt.tight_layout()
    plt.savefig(output_file, bbox_inches='tight')
    plt.close()


def radar_chart(df, output_file="radar_chart.png"):
    categories = ["Configuration", "Task", "Export", "Instrumentation"]
    num_vars = len(categories)

    max_values = [df["configuration Time (ms)"].max(),
                  df["task Time (ms)"].max(),
                  df["export Time (ms)"].max(),
                  df["instrumentation Time (ms)"].max()]

    df_scaled = pd.DataFrame()
    df_scaled["Run"] = df["Run"]
    df_scaled["Configuration"] = df["configuration Time (ms)"] / max_values[0]
    df_scaled["Task"] = df["task Time (ms)"] / max_values[1]
    df_scaled["Export"] = df["export Time (ms)"] / max_values[2]
    df_scaled["Instrumentation"] = df["instrumentation Time (ms)"] / max_values[3]

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
    plt.savefig(output_file, bbox_inches='tight')
    plt.close()

def two_stacked_area_charts(df1, df2, output_file="stacked_area_charts.png"):
    start = 100
    end = 200
    range_size = end - start
    range_list = range(0, range_size)

    df1 = df1.loc[start:end - 1]
    df1['Total Time'] = df1["configuration Time (ms)"] + df1["instrumentation Time (ms)"] + df1["export Time (ms)"] + \
                        df1["task Time (ms)"]
    df1['Configuration %'] = df1["configuration Time (ms)"] / df1['Total Time']
    df1['Instrumentation %'] = df1["instrumentation Time (ms)"] / df1['Total Time']
    df1['Export %'] = df1["export Time (ms)"] / df1['Total Time']
    df1['Task %'] = df1["task Time (ms)"] / df1['Total Time']

    df2 = df2.loc[start:end - 1]
    df2['Total Time'] = df2["configuration Time (ms)"] + df2["instrumentation Time (ms)"] + df2["export Time (ms)"] + \
                        df2["task Time (ms)"]
    df2['Configuration %'] = df2["configuration Time (ms)"] / df2['Total Time']
    df2['Instrumentation %'] = df2["instrumentation Time (ms)"] / df2['Total Time']
    df2['Export %'] = df2["export Time (ms)"] / df2['Total Time']
    df2['Task %'] = df2["task Time (ms)"] / df2['Total Time']

    categories = ['Configuration %', 'Instrumentation %', 'Export %', 'Task %']

    fig, axes = plt.subplots(1, 2, figsize=(16, 8), sharey=True)

    axes[0].stackplot(range_list, df1[categories].T,
                      colors=['mediumslateblue', 'mediumseagreen', 'coral', 'lightskyblue'], alpha=0.8)
    axes[0].set_xlabel("Iteration", fontsize=24)
    axes[0].set_ylabel("Percentage of Total Time", fontsize=24)
    axes[0].set_xlim(0, range_size)
    axes[0].set_ylim(0, 1)
    axes[0].set_xticks(ticks=range(0, range_size + 1, 20))

    axes[1].stackplot(range_list, df2[categories].T,
                      colors=['mediumslateblue', 'mediumseagreen', 'coral', 'lightskyblue'], alpha=0.8)
    axes[1].set_xlabel("Iteration", fontsize=24)
    axes[1].set_xlim(0, range_size)
    axes[1].set_ylim(0, 1)
    axes[1].set_xticks(ticks=range(0, range_size + 1, 20))

    fig.legend(labels=['Configuration', 'Instrumentation', 'Export', 'Task'],
               loc='upper center', ncol=4, frameon=True, shadow=True, bbox_to_anchor=(0.5, 1.0))

    plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust the layout to fit everything properly
    plt.savefig(output_file, bbox_inches='tight')
    plt.close()

def plot_all(filename, name):
    df = pd.read_csv(filename)

    os.makedirs(f"plots/{name}", exist_ok=True)

    # boxplot(df, f"plots/{name}/{name}_boxplot.pdf")
    # lineplot(df, f"plots/{name}/{name}_lineplot.pdf")
    stacked_area_chart(df, f"plots/{name}/{name}_stacked_area_chart.pdf")


if __name__ == "__main__":
    dynamic_html_cold_file = "output/dynamic-html_cold_100000_each_run_results.csv"
    dynamic_html_warm_file = "output/dynamic-html_warm_100000_each_run_results.csv"
    graph_pagerank_cold_file = "output/graph-pagerank_cold_100000_each_run_results.csv"
    graph_pagerank_warm_file = "output/graph-pagerank_warm_100000_each_run_results.csv"
    db_file = "output/db_100000_each_run_results.csv"
    updates_file = "output/updates_100000_each_run_results.csv"

    plot_all(dynamic_html_cold_file, "dynamic-html-cold")
    plot_all(dynamic_html_warm_file, "dynamic-html-warm")
    plot_all(graph_pagerank_cold_file, "graph-pagerank-cold")
    plot_all(graph_pagerank_warm_file, "graph-pagerank-warm")
    plot_all(db_file, "db")
    plot_all(updates_file, "updates")

    df1 = pd.read_csv(dynamic_html_cold_file)
    df2 = pd.read_csv(db_file)
    two_stacked_area_charts(df1, df2, "plots/two-stacked-area-charts.pdf")

