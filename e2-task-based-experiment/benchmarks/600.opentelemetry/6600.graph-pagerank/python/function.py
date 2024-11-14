import igraph

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.resources import Resource

otlp_exporter = OTLPSpanExporter(
    endpoint="http://<REPLACE_ME>:4317",
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
    span = tracer.start_span("handler")
    ctx = trace.set_span_in_context(span)

    size = event.get('size')
    span.set_attribute("size", size)

    generate_graph_span = tracer.start_span("generate_graph", context=ctx)
    graph = igraph.Graph.Barabasi(size, 10)
    generate_graph_span.end()

    pagerank_span = tracer.start_span("pagerank", context=ctx)
    result = graph.pagerank()
    pagerank_span.end()

    first_node_rank = result[0]
    span.set_attribute("first_node_rank", first_node_rank)

    span.end()
    return {
        'result': first_node_rank
    }
