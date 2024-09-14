# Step 1 Validate if the overhead matches with Chapter 3 and 4 results (The percentage)
# 1.1 Take the app (task and request based), profile it and measure the overhead
# 1.2 Check if the results match
import os

# Step 2
# 2.1 Create function where part of the instrumentation is removed
# 2.2 Run experiments per config
# 2.3

# TODO: Simplify the workload function defining part
# TODO: Add request based app as well?
# TODO: Add functions where I remove part of the things out of profiling
    # TODO: Configuration
    # TODO: Instrumentation
    # TODO: Export
# TODO: Run validations (step 1)

# TODO:


import dynamic_html.main as dynamic_html
import graph_pagerank.main as graph_pagerank

import utils
from utils import ExperimentName, get_total_avg_time, save_aggregated_statistics
import multiprocessing
from profiling import profile_function

OTLP_ENDPOINT = "http://localhost:4317"


def run_single_workload(times_dict_list, _experiment_name, _instrumented):
    _event = {}
    # TODO: Graph pagerank
    # TODO: SIMPLIFY THIS

    if _experiment_name == ExperimentName.DYNAMIC_HTML.value:
        _event = utils.DYNAMIC_HTML_EVENT

        if _instrumented:
            @profile_function(times_dict_list, _experiment_name, _instrumented)
            def workload(event):
                local_tracer = utils.configure_opentelemetry(OTLP_ENDPOINT)
                span = local_tracer.start_span("workload")
                dynamic_html.task_instrumented(event, span)
                span.end()
        else:
            @profile_function(times_dict_list, _experiment_name, _instrumented)
            def workload(event):
                dynamic_html.task_non_instrumented(event)

    elif _experiment_name == ExperimentName.GRAPH_PAGERANK.value:
        _event = utils.GRAPH_PAGERANK_EVENT
        if _instrumented:
            @profile_function(times_dict_list, _experiment_name, _instrumented)
            def workload(event):
                local_tracer = utils.configure_opentelemetry(OTLP_ENDPOINT)
                span = local_tracer.start_span("workload")
                graph_pagerank.task_instrumented(event, span)
                span.end()
        else:
            @profile_function(times_dict_list, _experiment_name, _instrumented)
            def workload(event):
                graph_pagerank.task_non_instrumented(event)
    else:
        def workload(event):
            return

    workload(_event)


def run_workloads_sequentially(num_runs, experiment_name, instrumented):
    times_dict_list = multiprocessing.Manager().list()

    for i in range(num_runs):
        p = multiprocessing.Process(target=run_single_workload, args=(times_dict_list, experiment_name, instrumented))
        p.start()
        p.join()  # Wait for the process to finish before starting the next one
        print("Finished iteration:", i + 1)

    return list(times_dict_list)


def step_1_validate(experiment_name, iterations):
    # Run 10k iterations without instrumentation
    # Run 10k iterations with instrumentation
    # Save both total times and get the total overhead

    # INSTRUMENTED
    instrumented_times = run_workloads_sequentially(iterations, experiment_name, instrumented=True)
    instrumented_total_avg_time = get_total_avg_time(instrumented_times)
    save_aggregated_statistics(instrumented_times,
                                     filename=f"output/{experiment_name}/{experiment_name}_{iterations}_instrumented.csv")

    # NON-INSTRUMENTED
    non_instrumented_times = run_workloads_sequentially(iterations, experiment_name, instrumented=False)
    non_instrumented_total_avg_time = get_total_avg_time(non_instrumented_times)
    save_aggregated_statistics(non_instrumented_times,
                                     filename=f"output/{experiment_name}/{experiment_name}_{iterations}_non-instrumented.csv")

    print(f"Total Instrumented time: {instrumented_total_avg_time}")
    print(f"Total Non-instrumented time: {non_instrumented_total_avg_time}")
    instrumentation_overhead = instrumented_total_avg_time / non_instrumented_total_avg_time
    print(f"Overhead percentage: {round((instrumentation_overhead * 100)-100, 2)}%")


if __name__ == '__main__':
    iterations = os.getenv("EXPERIMENT_ITERATIONS", 10)
    # experiment_name = os.getenv("EXPERIMENT_NAME", ExperimentName.DYNAMIC_HTML.value)

    step_1_validate(ExperimentName.DYNAMIC_HTML.value, iterations)
    step_1_validate(ExperimentName.GRAPH_PAGERANK.value, iterations)
