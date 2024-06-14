const sharp = require('sharp'),
			path = require('path'),
      storage = require('./storage');

let storage_handler = new storage.storage();

const { NodeTracerProvider } = require('@opentelemetry/node');
const { SimpleSpanProcessor } = require('@opentelemetry/tracing');
const { CollectorTraceExporter } = require('@opentelemetry/exporter-collector-grpc');
const { trace } = require('@opentelemetry/api');
const { Resource } = require('@opentelemetry/resources');

const provider = new NodeTracerProvider({
  resource: new Resource({
    'service.name': '630.thumbnailer-opentelemetry-nodejs',
  }),
});
const exporter = new CollectorTraceExporter({
  url: 'http://192.168.1.104:4317',
});
provider.addSpanProcessor(new SimpleSpanProcessor(exporter));
provider.register();

const tracer = trace.getTracer('tracer');

exports.handler = async function(event) {
  return tracer.startActiveSpan('handler', { attributes: { 'event.bucket': event.bucket.bucket, 'event.key': event.object.key } }, async (span) => {
    try {
      let bucket = event.bucket.bucket;
      let input_prefix = event.bucket.input;
      let output_prefix = event.bucket.output;
      let key = event.object.key;
      let width = event.object.width;
      let height = event.object.height;
      let pos = key.lastIndexOf('.');
      let upload_key = key.substr(0, pos < 0 ? key.length : pos) + '.png';

      span.setAttributes({
        'bucket': bucket,
        'input_prefix': input_prefix,
        'output_prefix': output_prefix,
        'key': key,
        'width': width,
        'height': height,
        'upload_key': upload_key,
      });

      const sharp_resizer = sharp().resize(width, height).png();
      let read_promise = storage_handler.downloadStream(bucket, path.join(input_prefix, key));
      let [writeStream, promise, uploadName] = storage_handler.uploadStream(bucket, path.join(output_prefix, upload_key));

      let downloadStart = Date.now();
      read_promise.then((input_stream) => {
        input_stream.pipe(sharp_resizer).pipe(writeStream);
      });

      await promise;

      let downloadEnd = Date.now();
      let downloadTime = downloadEnd - downloadStart;

      span.addEvent('Image processing completed', {
        'download.time_ms': downloadTime,
      });

      span.setAttributes({
        'download.time_ms': downloadTime,
        'upload.keyName': uploadName,
      });

      span.end();
      return {
        bucket: output_prefix,
        key: uploadName
      };
    } catch (err) {
      span.recordException(err);
      span.setStatus({ code: 2, message: 'Handler error' });
      span.end();
      throw err;
    }
  });
};
