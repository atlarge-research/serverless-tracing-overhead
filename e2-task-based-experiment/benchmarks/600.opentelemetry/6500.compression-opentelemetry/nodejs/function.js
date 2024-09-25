const fs = require('fs');
const path = require('path');
const uuid = require('uuid');
const util = require('util');
const archiver = require('archiver');
const storage = require('./storage');
const storage_handler = new storage.storage();


const { BasicTracerProvider } = require('@opentelemetry/sdk-trace-base');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-grpc');
const { SimpleSpanProcessor } = require('@opentelemetry/sdk-trace-base');
const opentelemetry = require('@opentelemetry/api');

const tracerProvider = new BasicTracerProvider({
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: '650.compression-opentelemetry-nodejs',
  }),
});

const traceExporter = new OTLPTraceExporter({
  url: 'http://192.168.1.109:4317',
});

tracerProvider.addSpanProcessor(new SimpleSpanProcessor(traceExporter));
tracerProvider.register();

const tracer = tracerProvider.getTracer('nodejs-tracer');

const mkdir = util.promisify(fs.mkdir);
const stat = util.promisify(fs.stat);
const readdir = util.promisify(fs.readdir);

async function parseDirectory(directory, ctx) {
  const span = tracer.startSpan('parseDirectory', undefined, ctx);
  span.setAttribute('directory', directory);

  let size = 0;
  const files = await readdir(directory);
  span.setAttribute('files', files);
  
  for (const file of files) {
    const filePath = path.join(directory, file);
    const fileStat = await stat(filePath);
    if (fileStat.isFile()) {
      size += fileStat.size;
    }
  }

  span.setAttribute('directory_size', size);
  span.end();
  return size;
}

async function compressDirectory(sourceDir, archivePath, ctx) {
  const span = tracer.startSpan('compressDirectory', undefined, ctx);
  span.setAttribute('source_directory', sourceDir);
  span.setAttribute('archive_path', archivePath);

  return new Promise((resolve, reject) => {
    const output = fs.createWriteStream(archivePath);
    const archive = archiver('zip', { zlib: { level: 9 } });

    output.on('close', () => {
      span.addEvent('archive closed', { archiveSize: archive.pointer() });
      span.end();
      resolve(archive.pointer());
    });

    archive.on('error', (err) => {
      span.recordException(err);
      span.end();
      reject(err);
    });

    archive.pipe(output);
    archive.directory(sourceDir, false);
    archive.finalize();
  });
}

exports.handler = async function(event) {
  const span = tracer.startSpan('handler');
  const ctx = opentelemetry.trace.setSpan(opentelemetry.context.active(), span);

  span.setAttribute('event', JSON.stringify(event));

  try {
    const bucket = event.bucket.bucket;
    const input_prefix = event.bucket.input;
    const output_prefix = event.bucket.output;
    const key = event.object.key;
    const download_path = `/tmp/${key}-${uuid.v4()}`;

    span.setAttribute('bucket', bucket);
    span.setAttribute('input_prefix', input_prefix);
    span.setAttribute('output_prefix', output_prefix);
    span.setAttribute('key', key);
    span.setAttribute('download_path', download_path);

    await mkdir(download_path, { recursive: true });

    const downloadSpan = tracer.startSpan('download', undefined, ctx);
    await storage_handler.downloadDirectory(bucket, path.join(input_prefix, key), download_path);
    downloadSpan.end()

    const size = await parseDirectory(download_path, ctx);
    span.setAttribute("download_size", size)

    const compressSpan = tracer.startSpan('compress', undefined, ctx);
    const archivePath = path.join('/tmp', `${key}.zip`);
    await compressDirectory(download_path, archivePath, ctx);
    compressSpan.end()

    const uploadSpan = tracer.startSpan('upload', undefined, ctx);
    const keyName = await storage_handler.upload(bucket, path.join(output_prefix, `${key}.zip`), archivePath);
    uploadSpan.end()

    span.setAttribute("key_name", keyName);

    span.end();

    return {
      result: {
        bucket: bucket,
        key: keyName
      }
    };
  } catch (err) {
    span.recordException(err);
    span.end();
    console.error('Handler error:', err);
    throw err;
  }
};