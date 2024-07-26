import time
import cProfile
import pstats
from io import StringIO
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

# Setup OpenTelemetry
resource = Resource(attributes={"service.name": "test-profiler"})
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer("function")

# Setup the span processor with the exporter
otlp_exporter = OTLPSpanExporter(
    endpoint="http://localhost:4317",
    insecure=True
)
span_processor = SimpleSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)


# Convert pstats to microseconds
def f8(x):
    ret = "%8.3f" % x
    if ret != '   0.000':
        return ret
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
        for line in full_stats.split('\n'):
            if 'opentelemetry' in line or 'tracer' in line:
                parts = line.split()
                if len(parts) > 3:
                    try:
                        otel_total_time += float(parts[1])  # Use the total time column
                    except ValueError:
                        continue

        print(otel_total_time)
        # Print the total time taken
        total_time = (end_time - start_time) * 1_000  # Convert to milliseconds
        otel_total_time /= 1_000  # Convert to milliseconds
        otel_percentage = (otel_total_time / total_time) * 100 if total_time > 0 else 0
        print(f"Total time taken: {total_time:.4f} ms")
        print(f"Total time spent on OpenTelemetry: {otel_total_time:.4f} ms ({otel_percentage:.2f}%)")

        return result
    return wrapper

@profile_function
def run_loop(iterations):
    with tracer.start_as_current_span("run_loop") as span:
        total = 0
        for i in range(iterations):
            with tracer.start_as_current_span("loop_iteration"):
                time.sleep(0.001)  # 1 ms
                total += i * i
                span.set_attribute("total", total)
                span.add_event("Computed", {
                    "total": total,
                    "i": i
                })
        return total

SCRIPT_DIR = ""

size_generators = {
    'test': 10,
    'small': 1000,
    'large': 100000
}

@profile_function
def dynamic_html(event):
    with tracer.start_as_current_span("dynamic_html") as span:
        name = event.get('username')
        size = event.get('random_len')
        cur_time = datetime.now()

        span.set_attribute("username", name)
        span.set_attribute("random_len", size)

        random_numbers = sample(range(0, 1000000), size)
        template_path = os.path.join(SCRIPT_DIR, 'templates', 'template.html')

        with open(template_path, 'r') as file:
            template = Template(file.read())

        html = template.render(username=name, cur_time=cur_time, random_numbers=random_numbers)

        span.set_attribute("template_path", template_path)
        span.set_attribute("render_time", str(cur_time))

        return {'result': html}

if __name__ == "__main__":
    # result = run_loop(10)

    input_config = {
        'username': 'testname',
        'random_len': size_generators["small"],
    }

    result = dynamic_html(input_config)
    # print(f"Total result: {result}")
