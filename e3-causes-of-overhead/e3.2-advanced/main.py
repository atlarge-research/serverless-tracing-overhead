# Step 1 Validate if the overhead matches with Chapter 3 and 4 results (The percentage)
# 1.1 Take the app (task and request based), profile it and measure the overhead
# 1.2 Check if the results match
# ! Did cold starts in Chapter 4 so cold starts here only as well

# Step 2
# ...

import dynamic_html.main as dynamic_html

import utils
import multiprocessing
from profiling import profile_function


OTLP_ENDPOINT = "http://localhost:4317"


def run_single_workload(times_dict_list, _experiment_name, _instrumented):
    _event = utils.DYNAMIC_HTML_EVENT
    local_tracer = utils.configure_opentelemetry(OTLP_ENDPOINT)

    # TODO: SIMPLIFY THIS
    # Instrumented
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

    workload(_event)


def run_workloads_sequentially(num_runs, experiment_name, instrumented):
    times_dict_list = multiprocessing.Manager().list()

    for i in range(num_runs):
        p = multiprocessing.Process(target=run_single_workload, args=(times_dict_list, experiment_name, instrumented))
        p.start()
        p.join()  # Wait for the process to finish before starting the next one
        print("Finished iteration:", i+1)

    return list(times_dict_list)


def step_1_validate(experiment_name, iterations):
    # Run 10k iterations without instrumentation
    # Run 10k iterations with instrumentation
    # Save both total times and get the total overhead
    
    # INSTRUMENTED
    instrumented_times = run_workloads_sequentially(iterations, experiment_name, instrumented=True)
    print(instrumented_times)
    for times_dict in instrumented_times:
        total_time = times_dict["total"]
        print(total_time)

    utils.save_aggregated_statistics(instrumented_times,
                                     f"output/{experiment_name}/{experiment_name}_{iterations}_instrumented.csv")

    # NON-INSTRUMENTED
    # non_instrumented_times = run_workloads_sequentially(iterations, experiment_name, instrumented=False)
    #
    # for times_dict in non_instrumented_times:
    #     total_time = times_dict["total"]
    #     print(total_time)
    #
    # utils.save_aggregated_statistics(non_instrumented_times,
    #                                  f"output/{experiment_name}/{experiment_name}_{iterations}_non_instrumented.csv")



if __name__ == '__main__':
    # TODO: Env variables
    iterations = 1
    experiment_name = "dynamic-html"

    step_1_validate(experiment_name, iterations)

    # _times_dict_list = utils.run_workloads_sequentially(iterations, experiment_name, start_mode)