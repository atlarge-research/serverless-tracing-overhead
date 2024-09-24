const sharp = require('sharp');
const path = require('path');
const storage = require('./storage');

const { BasicTracerProvider } = require('@opentelemetry/sdk-trace-base');
const { Resource } = require('@opentelemetry/resources');
const { SEMRESATTRS_SERVICE_NAME } = require('@opentelemetry/semantic-conventions');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-grpc');
const { SimpleSpanProcessor } = require('@opentelemetry/sdk-trace-base');
const opentelemetry = require('@opentelemetry/api');

const tracerProvider = new BasicTracerProvider({
  resource: new Resource({
    [SEMRESATTRS_SERVICE_NAME]: '630.thumbnailer-opentelemetry-nodejs',
  }),
});

const traceExporter = new OTLPTraceExporter({
  url: 'http://192.168.1.109:4317',
});

tracerProvider.addSpanProcessor(new SimpleSpanProcessor(traceExporter));
tracerProvider.register();

const tracer = tracerProvider.getTracer('nodejs-tracer');

let storage_handler = new storage.storage();

exports.handler = async function(event) {
  const span = tracer.startSpan('handler');
  const ctx = opentelemetry.trace.setSpan(opentelemetry.context.active(), span);

  const bucket = event.bucket.bucket;
  const input_prefix = event.bucket.input;
  const output_prefix = event.bucket.output;
  const key = event.object.key;
  const width = event.object.width;
  const height = event.object.height;

  let pos = key.lastIndexOf('.');
  let upload_key = key.substr(0, pos < 0 ? key.length : pos) + '.png';

  span.setAttribute("bucket", bucket)
  span.setAttribute("input_prefix", input_prefix)
  span.setAttribute("output_prefix", output_prefix)
  span.setAttribute("key", key)
  span.setAttribute("width", width)
  span.setAttribute("height", height)

  const sharp_resizer = sharp().resize(width, height).png();
  let read_promise = storage_handler.downloadStream(bucket, path.join(input_prefix, key));

  let [writeStream, promise, uploadName] = storage_handler.uploadStream(bucket, path.join(output_prefix, upload_key));
  span.setAttribute("upload.uploadName", uploadName);

  const downloadSpan = tracer.startSpan("download", undefined, ctx)
  read_promise.then(
    (input_stream) => {
      input_stream.pipe(sharp_resizer).pipe(writeStream);
    }
  ).catch((err) => {
    span.recordException(err);
    downloadSpan.end()
    span.end();
  });
  downloadSpan.end()

  const uploadSpan = tracer.startSpan("download", undefined, ctx)
  await promise.then(() => {
    uploadSpan.end()
  }).catch((err) => {
    uploadSpan.end()
    span.recordException(err);
  });

  span.end();
  return { bucket: output_prefix, key: uploadName };
};