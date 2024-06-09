const Mustache = require('mustache');
const fs = require('fs');
const path = require('path');
const { NodeTracerProvider } = require('@opentelemetry/node');
const { SimpleSpanProcessor } = require('@opentelemetry/tracing');
const { CollectorTraceExporter } = require('@opentelemetry/exporter-collector-grpc');
const { trace } = require('@opentelemetry/api');
const { Resource } = require('@opentelemetry/resources');

const provider = new NodeTracerProvider({
  resource: new Resource({
    'service.name': '610.dynamic-html-opentelemetry-nodejs',
  }),
});
const exporter = new CollectorTraceExporter({
  url: 'http://192.168.1.101:4317',
});
provider.addSpanProcessor(new SimpleSpanProcessor(exporter));
provider.register();

const tracer = trace.getTracer('tracer');

function random(b, e) {
  return Math.round(Math.random() * (e - b) + b);
}

exports.handler = async function (event) {
  return tracer.startActiveSpan('handler', { attributes: { 'handler.event.username': event.username, 'handler.event.random_len': event.random_len } }, async (span) => {

    var random_numbers = new Array(event.random_len);
    for (var i = 0; i < event.random_len; ++i) {
      random_numbers[i] = random(0, 100);
    }

    var input = {
      cur_time: new Date().toLocaleString(),
      username: event.username,
      random_numbers: random_numbers,
    };
    span.setAttribute('username', event.username)

    var file = path.resolve(__dirname, 'templates', 'template.html');
    return new Promise((resolve, reject) => {
      fs.readFile(file, 'utf-8', (err, data) => {
        if (err) {
          span.recordException(err);
          span.setStatus({ code: 2, message: 'File read error' });
          span.setAttribute('error', true);
          span.end();
          reject(err);
        } else {
          const rendered = Mustache.render(data, input);
          span.setAttribute('rendered.length', rendered.length);
          span.end();
          resolve(rendered);
        }
      });
    });
  });
};
