const fs = require('fs'),
      path = require('path'),
      request = require('request'),
      storage = require('./storage');

let storage_handler = new storage.storage();

const { NodeTracerProvider } = require('@opentelemetry/node');
const { SimpleSpanProcessor } = require('@opentelemetry/tracing');
const { CollectorTraceExporter } = require('@opentelemetry/exporter-collector-grpc');
const { trace } = require('@opentelemetry/api');
const { Resource } = require('@opentelemetry/resources');

const provider = new NodeTracerProvider({
  resource: new Resource({
    'service.name': '620.uploader-opentelemetry-nodejs',
  }),
});
const exporter = new CollectorTraceExporter({
  url: 'http://192.168.1.104:4317',
});
provider.addSpanProcessor(new SimpleSpanProcessor(exporter));
provider.register();

const tracer = trace.getTracer('tracer');

function streamToPromise(stream) {
  return new Promise(function(resolve, reject) {
    stream.on("close", () =>  {
      resolve();
    });
    stream.on("error", reject);
  })
}

exports.handler = async function(event) {
  return tracer.startActiveSpan('handler', { attributes: { 'event.bucket': event.bucket.bucket, 'event.url': event.object.url } }, async (span) => {
    try {
      let bucket = event.bucket.bucket;
      let output_prefix = event.bucket.output;
      let url = event.object.url;
      let upload_key = path.basename(url);
      let download_path = path.join('/tmp', upload_key);

      span.setAttributes({
        'bucket': bucket,
        'output_prefix': output_prefix,
        'url': url,
        'download_path': download_path,
        'upload_key': upload_key,
      });

      var file = fs.createWriteStream(download_path);
      request(url).pipe(file);

      let downloadStart = Date.now();
      let promise = streamToPromise(file);
      var keyName;
      let upload = promise.then(
        async () => {
          let downloadEnd = Date.now();
          let downloadTime = downloadEnd - downloadStart;
          let fileSize = fs.statSync(download_path).size;

          span.addEvent('Download completed', {
            'file.size': fileSize,
            'download.time_ms': downloadTime,
          });

          let uploadStart = Date.now();
          [keyName, promise] = storage_handler.upload(bucket, path.join(output_prefix, upload_key), download_path);
          await promise;
          let uploadEnd = Date.now();
          let uploadTime = uploadEnd - uploadStart;

          span.addEvent('Upload completed', {
            'upload.keyName': keyName,
            'upload.time_ms': uploadTime,
          });

          span.setAttributes({
            'download.size': fileSize,
            'download.time_ms': downloadTime,
            'upload.time_ms': uploadTime,
          });
        }
      );
      await upload;
      span.end();
      return {bucket: bucket, url: url, key: keyName}
    } catch (err) {
      span.recordException(err);
      span.setStatus({ code: 2, message: 'Handler error' });
      span.end();
      throw err;
    }
  });
};