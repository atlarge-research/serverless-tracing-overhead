import os
import csv
import numpy as np
from enum import Enum
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

OTLP_ENDPOINT = os.getenv("OTLP_ENDPOINT", "http://localhost:4317")


class ExperimentName(Enum):
    DYNAMIC_HTML = "dynamic-html"
    GRAPH_PAGERANK = "graph-pagerank"


DYNAMIC_HTML_SIZE_GENERATORS = {
    'test': 10,
    'small': 1000,
    'large': 100000
}
DYNAMIC_HTML_EVENT = {
    'username': 'testname',
    'random_len': DYNAMIC_HTML_SIZE_GENERATORS['test']
}
GRAPH_PAGERANK_SIZE_GENERATORS = {
    'test' : 10,
    'small' : 10000,
    'large': 100000
}

GRAPH_PAGERANK_EVENT = {
    'size': GRAPH_PAGERANK_SIZE_GENERATORS['small']
}


def configure_opentelemetry(otlp_endpoint):
    resource = Resource(attributes={"service.name": "e3-2"})
    provider = TracerProvider(resource=resource)

    otlp_exporter = OTLPSpanExporter(
        endpoint=otlp_endpoint,
        insecure=True
    )
    span_processor = SimpleSpanProcessor(otlp_exporter)
    provider.add_span_processor(span_processor)

    trace.set_tracer_provider(provider)

    tracer = trace.get_tracer("function")
    return tracer


def save_aggregated_statistics(times_dict_list, filename="aggregated_statistics.csv"):
    aggregated_times = {key: [] for key in times_dict_list[0]}
    percentage_of_total = {key: [] for key in times_dict_list[0]}

    for times_dict in times_dict_list:
        total_time = times_dict["total"]
        for key, value in times_dict.items():
            aggregated_times[key].append(value)
            percentage_of_total[key].append((value / total_time) * 100)

    if not os.path.exists(filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)

        # Write the header row
        writer.writerow(
            ["Function", "Average Time (ms)", "Median Time (ms)", "95th Percentile (ms)", "99th Percentile (ms)",
             "Average % of Total Time"])

        # Write the aggregated statistics for each function
        for func_name, times in aggregated_times.items():
            times_array = np.array(times)
            avg_time = np.mean(times_array)
            med_time = np.median(times_array)
            percentile_95 = np.percentile(times_array, 95)
            percentile_99 = np.percentile(times_array, 99)
            avg_percentage = np.mean(percentage_of_total[func_name])

            writer.writerow([
                func_name,
                f"{avg_time:.6f}",
                f"{med_time:.6f}",
                f"{percentile_95:.6f}",
                f"{percentile_99:.6f}",
                f"{avg_percentage:.2f}"
            ])

    print(f"Aggregated statistics saved to {filename}")


def get_total_avg_time(times_dict_list):
    aggregated_total_time = {"total": []}

    for times_dict in times_dict_list:
        total_time = times_dict["total"]
        aggregated_total_time["total"].append(total_time)

    avg_time = np.mean(np.array(aggregated_total_time["total"]))

    return avg_time
