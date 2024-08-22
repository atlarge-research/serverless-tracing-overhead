import os
import multiprocessing

from cprofiler import profile_function
from dynamic_html.main import task as dynamic_html_task
from graph_pagerank.main import task as graph_pagerank_task

from utils import save_aggregated_statistics, save_each_run_results, dynamic_html_event

# OpenTelemetry Libraries
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

OTLP_ENDPOINT = os.getenv("OTLP_ENDPOINT", "http://localhost:4317")
EXPERIMENT_NAME_DYNAMIC_HTML = "dynamic-html"
EXPERIMENT_NAME_GRAPH_PAGERANK = "graph-pagerank"


def run_single_workload(times_dict_list, experiment_name):
    _event = {}
    # If dynamic html
    if experiment_name == EXPERIMENT_NAME_DYNAMIC_HTML:
        _event = dynamic_html_event

        @profile_function(times_dict_list)
        def workload(event):
            tracer = configure_opentelemetry()

            span = tracer.start_span("workload")
            dynamic_html_task(event, span)
            span.end()
    elif experiment_name == EXPERIMENT_NAME_GRAPH_PAGERANK:
        @profile_function(times_dict_list)
        def workload(event):
            tracer = configure_opentelemetry()

            span = tracer.start_span("workload")
            graph_pagerank_task(event, span)
            span.end()
    else:
        def workload():
            return

    workload(_event)


def run_workloads_sequentially(num_runs, experiment_name="dynamic-html"):
    times_dict_list = multiprocessing.Manager().list()

    for _ in range(num_runs):
        p = multiprocessing.Process(target=run_single_workload, args=(times_dict_list, experiment_name))
        p.start()
        p.join()  # Wait for the process to finish before starting the next one

    return list(times_dict_list)


def configure_opentelemetry():
    resource = Resource(attributes={"service.name": "e3-dynamic-html"})
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
    _iterations = int(os.getenv("TEST_RUNS", 100))
    _experiment_name = os.getenv("EXPERIMENT_NAME", EXPERIMENT_NAME_DYNAMIC_HTML)

    # Run the workloads and get the execution times
    _times_dict_list = run_workloads_sequentially(_iterations, _experiment_name)

    # Save the results of each run to a CSV file
    save_each_run_results(_times_dict_list,
                          filename=f"output/{_experiment_name}_{_iterations}_each_run_results.csv")

    # Save the aggregated statistics to a different CSV file
    save_aggregated_statistics(_times_dict_list,
                               filename=f"output/{_experiment_name}_{_iterations}_aggregated_statistics.csv")
