import datetime
import igraph
import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.resources import Resource

otlp_exporter = OTLPSpanExporter(
    endpoint="http://192.168.1.109:4317",
    insecure=True
)

span_processor = SimpleSpanProcessor(otlp_exporter)

resource = Resource(attributes={
    "service.name": "660.graph-pagerank-opentelemetry"
})
trace.set_tracer_provider(TracerProvider(resource=resource))
trace.get_tracer_provider().add_span_processor(span_processor)

# Get a tracer
tracer = trace.get_tracer("handler")

def handler(event):
    with tracer.start_as_current_span("handler") as span:
        size = event.get('size')
        span.set_attribute("size", size)

        graph_generating_begin = datetime.datetime.now()
        graph = igraph.Graph.Barabasi(size, 10)
        graph_generating_end = datetime.datetime.now()

        graph_generating_time = (graph_generating_end - graph_generating_begin) / datetime.timedelta(microseconds=1)
        span.add_event("Graph generation completed", {
            "graph_generating_time": graph_generating_time
        })
        span.set_attribute("graph_generating_time", graph_generating_time)

        process_begin = datetime.datetime.now()
        result = graph.pagerank()
        process_end = datetime.datetime.now()

        process_time = (process_end - process_begin) / datetime.timedelta(microseconds=1)


        span.add_event("PageRank computation completed", {
            "compute_time": process_time
        })

        span.set_attribute("compute_time", process_time)

        return {
            'result': result[0],
            'measurement': {
                'graph_generating_time': graph_generating_time,
                'compute_time': process_time
            }
        }
