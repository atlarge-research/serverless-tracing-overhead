const fs = require('fs');
const path = require('path');
const storage = require('./storage');
const { execFile } = require('child_process');
const { promisify } = require('util');
const execFileAsync = promisify(execFile);

const storage_handler = new storage.storage();

const { BasicTracerProvider } = require('@opentelemetry/sdk-trace-base');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-grpc');
const { SimpleSpanProcessor } = require('@opentelemetry/sdk-trace-base');
const opentelemetry = require('@opentelemetry/api');

const tracerProvider = new BasicTracerProvider({
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: '640.video-processing-opentelemetry-nodejs',
  }),
});

const traceExporter = new OTLPTraceExporter({
  url: 'http://192.168.1.109:4317',
});

tracerProvider.addSpanProcessor(new SimpleSpanProcessor(traceExporter));
tracerProvider.register();

const tracer = tracerProvider.getTracer('nodejs-tracer');


const SCRIPT_DIR = path.resolve(__dirname);

async function callFfmpeg(args, ctx) {
  const span = tracer.startSpan('callFfmpeg', undefined, ctx);
  span.setAttribute('args', JSON.stringify(args));
  try {
    const ffmpegPath = path.join(SCRIPT_DIR, 'ffmpeg', 'ffmpeg');
    const { stdout, stderr } = await execFileAsync(ffmpegPath, ['-y', ...args], { stdio: ['ignore', 'pipe', 'pipe'] });
    span.end();
  } catch (error) {
    span.recordException(error);
    span.end();
    throw new Error(`Invocation of ffmpeg failed! ${error.message}`);
  }
}

async function toGif(video, duration, ctx) {
  const span = tracer.startSpan('toGif', undefined, ctx);
  span.setAttribute('video', video);
  span.setAttribute('duration', duration);

  const output = `/tmp/processed-${path.basename(video)}.gif`;
  await callFfmpeg(['-i', video, '-t', `${duration}`, '-vf', 'fps=10,scale=320:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse', '-loop', '0', output], ctx);

  span.end();
  return output;
}

async function watermark(video, duration, ctx) {
  const span = tracer.startSpan('watermark', undefined, ctx);
  span.setAttribute('video', video);
  span.setAttribute('duration', duration);

  const output = `/tmp/processed-${path.basename(video)}`;
  const watermarkFile = path.join(SCRIPT_DIR, 'resources', 'watermark.png');
  await callFfmpeg(['-i', video, '-i', watermarkFile, '-t', `${duration}`, '-filter_complex', 'overlay=main_w/2-overlay_w/2:main_h/2-overlay_h/2', output], ctx);

  span.end();
  return output;
}

async function transcodeMp3(video, duration) {
  return tracer.startActiveSpan('transcode_mp3', { attributes: { 'video': video, 'duration': duration } }, async (span) => {
    span.end();
  });
}

const operations = { 'transcode': transcodeMp3, 'extract-gif': toGif, 'watermark': watermark };

exports.handler = async function(event) {
  const span = tracer.startSpan('handler');
  const ctx = opentelemetry.trace.setSpan(opentelemetry.context.active(), span);

  span.setAttribute('event', JSON.stringify(event));

  try {
    const bucket = event.bucket.bucket;
    const input_prefix = event.bucket.input;
    const output_prefix = event.bucket.output;
    const key = event.object.key;
    const duration = event.object.duration;
    const op = event.object.op;
    const download_path = `/tmp/${key}`;

    span.setAttribute('bucket', bucket);
    span.setAttribute('input_prefix', input_prefix);
    span.setAttribute('output_prefix', output_prefix);
    span.setAttribute('key', key);
    span.setAttribute('duration', duration);
    span.setAttribute('op', op);
    span.setAttribute('download_path', download_path);

    const ffmpegBinary = path.join(SCRIPT_DIR, 'ffmpeg', 'ffmpeg');
    try {
      fs.chmodSync(ffmpegBinary, '755');
    } catch (error) {
      console.error('Error setting executable permissions for ffmpeg:', error.message);
    }

    const downloadSpan = tracer.startSpan("download", undefined, ctx)
    await storage_handler.download(bucket, path.join(input_prefix, key), download_path);
    const downloadSize = fs.statSync(download_path).size;
    downloadSpan.end()
    span.setAttribute('download_size', downloadSize);

    const processSpan = tracer.startSpan("process", undefined, ctx)
    const upload_path = await operations[op](download_path, duration, ctx);
    processSpan.end()

    const uploadSpan = tracer.start("upload", undefined, ctx)
    const filename = path.basename(upload_path);
    const uploadSize = fs.statSync(upload_path).size;
    const uploadKey = await storage_handler.upload(bucket, path.join(output_prefix, filename), upload_path);
    uploadSpan.end()

    span.setAttribute('upload_size', uploadSize);
    span.end();

    return {
      result: {
        bucket: bucket,
        key: uploadKey
      }
    };
  } catch (err) {
    span.recordException(err);
    span.end();
    console.error('Handler error:', err);
    throw err;
  }
};