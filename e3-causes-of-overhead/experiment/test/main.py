from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

# Dynamic HTML
import os
from jinja2 import Template
from datetime import datetime
from random import sample

import time
import cProfile
import pstats
from io import StringIO


# Convert pstats to microseconds
def f8(x):
    # ret = "%8.3f" % x
    # if ret != '   0.000':
    #     return ret
    return "%6d" % (x * 10000000)

pstats.f8 = f8

def profile_function(func):
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()

        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        profiler.disable()

        # Save the profiling results to a .prof file
        prof_filename = f"{func.__name__}.prof"
        profiler.dump_stats(prof_filename)
        print(f"Saved profiling results to {prof_filename}")

        s = StringIO()
        sortby = 'tottime'
        ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)
        ps.print_stats()
        full_stats = s.getvalue()

        # Filter results for OpenTelemetry related stuff
        filtered_stats = "\n".join(
            line for line in full_stats.split('\n')
            if 'opentelemetry' in line or 'tracer' in line or line.strip().startswith(('ncalls', 'filename'))
        )

        print(filtered_stats)

        otel_total_time = 0.0
        total_time = 0.0
        for line in full_stats.split('\n'):
            parts_2 = line.split()
            if len(parts_2) > 3:
                try:
                    total_time += float(parts_2[1])
                except ValueError:
                    continue
            if 'opentelemetry' in line or 'tracer' in line:
                parts = line.split()
                if len(parts) > 3:
                    try:
                        otel_total_time += float(parts[1])  # Use the total time column
                    except ValueError:
                        continue

        print(f"Otel total time: {otel_total_time}")
        print(f"Total time: {total_time}")
        total_time_2 = end_time - start_time
        print(f"Manually measured total time: {total_time_2 * 1_000_000}")
        # Print the total time taken
        # total_time = (end_time - start_time) * 1_000  # Convert to milliseconds
        total_time /= 1_000
        otel_total_time /= 1_000  # Convert to milliseconds
        otel_percentage = (otel_total_time / total_time) * 100 if total_time > 0 else 0
        print(f"Total time taken: {total_time:.4f} ms")
        print(f"Total time spent on OpenTelemetry: {otel_total_time:.4f} ms ({otel_percentage:.2f}%)")

        return result
    return wrapper


def setup_opentelemetry():
    resource = Resource(attributes={"service.name": "test-profiler"})
    provider = TracerProvider(resource=resource)

    otlp_exporter = OTLPSpanExporter(
        endpoint="http://localhost:4317",
        insecure=True
    )
    span_processor = SimpleSpanProcessor(otlp_exporter)
    provider.add_span_processor(span_processor)

    trace.set_tracer_provider(provider)

    tracer = trace.get_tracer("function")
    return tracer


@profile_function
def run_loop(iterations):
    tracer = setup_opentelemetry()
    with tracer.start_as_current_span("run_loop") as span:
        total = 0
        for i in range(iterations):
            with tracer.start_as_current_span("loop_iteration"):
                total += i * i
                span.set_attribute("total", total)
                span.add_event("Computed", {
                    "total": total,
                    "i": i
                })
        return total


if __name__ == "__main__":
    result = run_loop(1)