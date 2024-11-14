import igraph
from opentelemetry import trace


def task(event, span, tracer):
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

    return {
        'result': first_node_rank
    }
