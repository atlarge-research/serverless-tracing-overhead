import datetime
import igraph


def task(event, span):
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
