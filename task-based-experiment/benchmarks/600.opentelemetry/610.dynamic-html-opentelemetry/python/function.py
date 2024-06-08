from datetime import datetime                                                   
from random import sample  
from os import path
from time import time                                                           
import os
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.resources import Resource

from jinja2 import Template

SCRIPT_DIR = path.abspath(path.join(path.dirname(__file__)))


resource = Resource(attributes={
    "service.name": "610.dynamic-html-opentelemetry"
})

trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer("function")

# Setup the OTLP exporter to send traces to the collector using HTTP
otlp_exporter = OTLPSpanExporter(
    endpoint="http://192.168.1.101:4317",
    insecure=True
)

# Setup the span processor with the exporter
span_processor = SimpleSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)


def handler(event):
    with tracer.start_as_current_span("handler") as span:
        # start timing
        name = event.get('username')
        size = event.get('random_len')
        cur_time = datetime.now()
        
        # Add attributes to the span
        span.set_attribute("username", name)
        span.set_attribute("random_len", size)
        
        random_numbers = sample(range(0, 1000000), size)
        template_path = os.path.join(SCRIPT_DIR, 'templates', 'template.html')
        
        # Read and render template
        with open(template_path, 'r') as file:
            template = Template(file.read())
        
        html = template.render(username=name, cur_time=cur_time, random_numbers=random_numbers)
        
        # Set additional attributes if needed
        span.set_attribute("template_path", template_path)
        span.set_attribute("render_time", str(cur_time))
        
        # end timing and return result
        return {'result': html}
