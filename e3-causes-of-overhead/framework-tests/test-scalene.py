from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

# Dynamic HTML
import os
from jinja2 import Template
from datetime import datetime
from random import sample

# Profiler
from scalene import scalene_profiler
size_generators = {
    'test': 10,
    'small': 1000,
    'large': 100000
}
SCRIPT_DIR = ""
event = {
    'username': 'testname',
    'random_len': size_generators["small"],
}



def configure_opentelemetry():
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
    return tracer

tracer = configure_opentelemetry()

span = tracer.start_span("dynamic_html")

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

span.end()

