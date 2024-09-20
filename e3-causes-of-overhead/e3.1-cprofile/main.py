import os
import multiprocessing

from cprofiler import profile_function
from dynamic_html.main import task as dynamic_html_task
from graph_pagerank.main import task as graph_pagerank_task

from utils import save_aggregated_statistics, save_each_run_results, dynamic_html_event, graph_pagerank_event

# OpenTelemetry Libraries
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

OTLP_ENDPOINT = os.getenv("OTLP_ENDPOINT", "http://localhost:4317")
EXPERIMENT_NAME_DYNAMIC_HTML = "dynamic-html"
EXPERIMENT_NAME_GRAPH_PAGERANK = "graph-pagerank"

tracer = None


def run_single_workload(times_dict_list, _experiment_name, _start_mode):
    _event = {}
    global tracer
    # Pre-configure OpenTelemetry for warm start
    if _start_mode == "warm":
        # print("Warm mode, configuring opentelemetry before profiling")
        tracer = configure_opentelemetry()


    # If dynamic html
    if _experiment_name == EXPERIMENT_NAME_DYNAMIC_HTML:
        _event = dynamic_html_event

        @profile_function(times_dict_list, _experiment_name, _start_mode)
        def workload(event):
            if tracer is None:
                # Cold
                local_tracer = configure_opentelemetry()
            else:
                # Warm
                local_tracer = tracer
            span = local_tracer.start_span("workload")
            dynamic_html_task(event, span)
            span.end()
    elif _experiment_name == EXPERIMENT_NAME_GRAPH_PAGERANK:
        _event = graph_pagerank_event

        @profile_function(times_dict_list, _experiment_name, _start_mode)
        def workload(event):
            if tracer is None:
                # Cold
                local_tracer = configure_opentelemetry()
            else:
                # Warm
                local_tracer = tracer

            span = local_tracer.start_span("workload")
            graph_pagerank_task(event, span)
            span.end()
    else:
        def workload():
            return

    workload(_event)


def run_workloads_sequentially(num_runs, experiment_name, start_mode):
    times_dict_list = multiprocessing.Manager().list()

    for i in range(num_runs):
        p = multiprocessing.Process(target=run_single_workload, args=(times_dict_list, experiment_name, start_mode))
        p.start()
        p.join()  # Wait for the process to finish before starting the next one
        print("Finished iteration:", i+1)

    return list(times_dict_list)


def configure_opentelemetry():
    resource = Resource(attributes={"service.name": "e3"})
    provider = TracerProvider(resource=resource)

    otlp_exporter = OTLPSpanExporter(
        endpoint=OTLP_ENDPOINT,
        insecure=True
    )
    span_processor = SimpleSpanProcessor(otlp_exporter)
    provider.add_span_processor(span_processor)

    trace.set_tracer_provider(provider)

    tracer = trace.get_tracer("function")
    return tracer


if __name__ == "__main__":
    # Number of times to run the process
    iterations = int(os.getenv("TEST_RUNS", 50))
    experiment_name = os.getenv("EXPERIMENT_NAME", EXPERIMENT_NAME_DYNAMIC_HTML)
    start_mode = os.getenv("START_MODE", "cold")
    print("Iterations: ", iterations)
    print("Experiment name: ", experiment_name)
    print("Start mode: ", start_mode)

    # Run the workloads and get the execution times
    _times_dict_list = run_workloads_sequentially(iterations, experiment_name, start_mode)

    # Save the results of each run to a CSV file
    save_each_run_results(_times_dict_list,
                          filename=f"output/{experiment_name}_{start_mode}_{iterations}_each_run_results.csv")

    # Save the aggregated statistics to a different CSV file
    save_aggregated_statistics(_times_dict_list,
                               filename=f"output/{experiment_name}_{start_mode}_{iterations}_aggregated_statistics.csv")
