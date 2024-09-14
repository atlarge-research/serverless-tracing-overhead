const fs = require('fs');
const path = require('path');
const request = require('request');
const storage = require('./storage');

const { BasicTracerProvider } = require('@opentelemetry/sdk-trace-base');
const { Resource } = require('@opentelemetry/resources');
const { SEMRESATTRS_SERVICE_NAME } = require('@opentelemetry/semantic-conventions');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-grpc');
const { SimpleSpanProcessor } = require('@opentelemetry/sdk-trace-base');
const opentelemetry = require('@opentelemetry/api');

const tracerProvider = new BasicTracerProvider({
  resource: new Resource({
    [SEMRESATTRS_SERVICE_NAME]: '620.uploader-opentelemetry-nodejs',
  }),
});

const traceExporter = new OTLPTraceExporter({
  url: 'http://192.168.1.109:4317',
});

tracerProvider.addSpanProcessor(new SimpleSpanProcessor(traceExporter));
tracerProvider.register();

const tracer = tracerProvider.getTracer('nodejs-tracer');

let storage_handler = new storage.storage();

function streamToPromise(stream, parentSpan) {
  const ctx = opentelemetry.trace.setSpan(
    opentelemetry.context.active(),
    parentSpan,
  );

  const span = tracer.startSpan('streamToPromise', undefined, ctx);

  return new Promise(function(resolve, reject) {
    stream.on("close", () =>  {
      span.addEvent('Stream closed');
      span.end();
      resolve();
    });
    stream.on("error", (err) => {
      span.recordException(err);
      span.end();
      reject(err);
    });
  });
}

exports.handler = async function(event) {
  const span = tracer.startSpan('handler');

  let bucket = event.bucket.bucket;
  let output_prefix = event.bucket.output;
  let url = event.object.url;
  let upload_key = path.basename(url);
  let download_path = path.join('/tmp', upload_key);

  span.setAttributes({
    'bucket': bucket,
    'output_prefix': output_prefix,
    'url': url,
    'upload_key': upload_key,
    'download_path': download_path,
  });

  var file = fs.createWriteStream(download_path);
  span.addEvent('File write stream created');

  request(url).pipe(file);
  span.addEvent('Request piped to file');

  let promise = streamToPromise(file, span);
  var keyName;
  let upload = promise.then(
    async () => {
      [keyName, promise] = storage_handler.upload(bucket, path.join(output_prefix, upload_key), download_path);
      span.addEvent('File upload started');
      await promise;
      span.addEvent('File upload completed');
      span.setAttribute('key_name', keyName);
    }
  );

  await upload;
  span.end();

  return {bucket: bucket, url: url, key: keyName};
};
