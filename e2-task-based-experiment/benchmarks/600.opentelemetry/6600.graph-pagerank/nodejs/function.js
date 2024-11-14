const createGraph = require('ngraph.graph');
const pagerank = require('ngraph.pagerank');

const { BasicTracerProvider } = require('@opentelemetry/sdk-trace-base');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-grpc');
const { SimpleSpanProcessor } = require('@opentelemetry/sdk-trace-base');
const opentelemetry = require('@opentelemetry/api');

const tracerProvider = new BasicTracerProvider({
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: '660.graph-pagerank-opentelemetry-nodejs',
  }),
});

const traceExporter = new OTLPTraceExporter({
  url: 'http://<REPLACE_ME>:4317',
});

tracerProvider.addSpanProcessor(new SimpleSpanProcessor(traceExporter));
tracerProvider.register();

const tracer = tracerProvider.getTracer('nodejs-tracer');

function generateBarabasiAlbertGraph(size, m) {
    const graph = createGraph();

    for (let i = 0; i < m; i++) {
        graph.addNode(i);
        for (let j = 0; j < i; j++) {
            graph.addLink(i, j);
        }
    }

    for (let i = m; i < size; i++) {
        graph.addNode(i);
        let targets = [];
        let totalDegree = 0;
        graph.forEachNode(node => {
            totalDegree += (graph.getLinks(node.id) || []).length;
        });

        graph.forEachNode(node => {
            const degree = (graph.getLinks(node.id) || []).length;
            const probability = degree / totalDegree;
            if (Math.random() < probability && targets.length < m) {
                targets.push(node.id);
            }
        });

        while (targets.length < m) {
            let randomNode;
            do {
                randomNode = Math.floor(Math.random() * i);
            } while (targets.includes(randomNode));
            targets.push(randomNode);
        }

        targets.forEach(target => {
            graph.addLink(i, target);
        });
    }

    return graph;
}

exports.handler = async function(event) {
    const span = tracer.startSpan('handler');
    const ctx = opentelemetry.trace.setSpan(opentelemetry.context.active(), span);

    const size = event.size;
    span.setAttribute('size', size);

    const generateGraphSpan = tracer.startSpan('generate_graph', undefined, ctx);
    const graph = generateBarabasiAlbertGraph(size, 10);
    generateGraphSpan.end()

    const pagerankSpan = tracer.startSpan('pagerank', undefined, ctx);
    const result = pagerank(graph);
    pagerankSpan.end()

    const firstNodeRank = result['0'] || 0;
    span.setAttribute("first_node_rank", firstNodeRank);

    span.end();
    return {
        result: firstNodeRank
    };
};
