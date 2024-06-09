const fs = require('fs');
const path = require('path');
const uuid = require('uuid');
const util = require('util');
const archiver = require('archiver');
const storage = require('./storage');
const storage_handler = new storage.storage();

const { NodeTracerProvider } = require('@opentelemetry/node');
const { SimpleSpanProcessor } = require('@opentelemetry/tracing');
const { CollectorTraceExporter } = require('@opentelemetry/exporter-collector-grpc');
const { trace } = require('@opentelemetry/api');
const { Resource } = require('@opentelemetry/resources');

const provider = new NodeTracerProvider({
  resource: new Resource({
    'service.name': '650.compression-opentelemetry',
  }),
});
const exporter = new CollectorTraceExporter({
  url: 'http://192.168.1.101:4317',
});
provider.addSpanProcessor(new SimpleSpanProcessor(exporter));
provider.register();

const tracer = trace.getTracer('tracer');

const mkdir = util.promisify(fs.mkdir);
const stat = util.promisify(fs.stat);
const readdir = util.promisify(fs.readdir);

async function parseDirectory(directory) {
  return tracer.startActiveSpan('parse_directory', async (span) => {
    let size = 0;
    console.log('Parsing directory:', directory);
    const files = await readdir(directory);
    for (const file of files) {
      const filePath = path.join(directory, file);
      const fileStat = await stat(filePath);
      if (fileStat.isFile()) {
        size += fileStat.size;
        console.log('File:', filePath, 'Size:', fileStat.size);
      }
    }
    span.setAttribute('directory_size', size);
    span.end();
    return size;
  });
}

async function compressDirectory(sourceDir, archivePath) {
  return new Promise((resolve, reject) => {
    const output = fs.createWriteStream(archivePath);
    const archive = archiver('zip', { zlib: { level: 9 } });

    output.on('close', () => {
      console.log(`Archive ${archivePath} created successfully, size: ${archive.pointer()} bytes`);
      resolve(archive.pointer());
    });

    archive.on('error', (err) => {
      console.error('Error creating archive:', err);
      reject(err);
    });

    archive.pipe(output);
    archive.directory(sourceDir, false);
    archive.finalize();
  });
}

exports.handler = async function(event) {
  return tracer.startActiveSpan('handler', { attributes: { 'event.bucket': event.bucket.bucket, 'event.key': event.object.key } }, async (span) => {
    try {
      const bucket = event.bucket.bucket;
      const input_prefix = event.bucket.input;
      const output_prefix = event.bucket.output;
      const key = event.object.key;
      const download_path = `/tmp/${key}-${uuid.v4()}`;
      await mkdir(download_path, { recursive: true });

      span.setAttributes({
        'bucket': bucket,
        'input_prefix': input_prefix,
        'output_prefix': output_prefix,
        'key': key,
        'download_path': download_path,
      });

      console.log('Event attributes set:', { bucket, input_prefix, output_prefix, key, download_path });

      const s3DownloadBegin = Date.now();
      console.log('Starting S3 download...');
      await storage_handler.downloadDirectory(bucket, path.join(input_prefix, key), download_path);
      const s3DownloadStop = Date.now();
      const downloadTime = (s3DownloadStop - s3DownloadBegin) / 1000;
      span.addEvent('S3 download completed', { 'download_time': downloadTime });
      console.log('S3 download completed in', downloadTime, 'seconds');

      const size = await parseDirectory(download_path);
      span.setAttribute('download_size', size);
      console.log('Directory size:', size);

      const compressBegin = Date.now();
      console.log('Starting compression...');
      const archivePath = path.join('/tmp', `${key}.zip`);
      const archiveSize = await compressDirectory(download_path, archivePath);
      const compressEnd = Date.now();
      const processTime = (compressEnd - compressBegin) / 1000;
      span.addEvent('Compression completed', { 'process_time': processTime });
      console.log('Compression completed in', processTime, 'seconds');

      const s3UploadBegin = Date.now();
      console.log('Starting S3 upload...');
      const keyName = await storage_handler.upload(bucket, path.join(output_prefix, `${key}.zip`), archivePath);
      const s3UploadStop = Date.now();
      const uploadTime = (s3UploadStop - s3UploadBegin) / 1000;
      span.addEvent('S3 upload completed', { 'upload_time': uploadTime });
      console.log('S3 upload completed in', uploadTime, 'seconds');

      span.setAttribute('upload_size', archiveSize);

      span.end();
      console.log('Span ended.');

      return {
        result: {
          bucket: bucket,
          key: keyName
        },
        measurement: {
          download_time: downloadTime,
          download_size: size,
          upload_time: uploadTime,
          upload_size: archiveSize,
          compute_time: processTime
        }
      };
    } catch (err) {
      span.recordException(err);
      span.setStatus({ code: 2, message: 'Handler error' });
      span.end();
      console.error('Error:', err);
      throw err;
    }
  });
};
