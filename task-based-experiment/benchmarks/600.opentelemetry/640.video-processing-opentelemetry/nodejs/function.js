const fs = require('fs');
const path = require('path');
const storage = require('./storage');
const { execFile } = require('child_process');
const { promisify } = require('util');
const execFileAsync = promisify(execFile);

const storage_handler = new storage.storage();

const { NodeTracerProvider } = require('@opentelemetry/node');
const { SimpleSpanProcessor } = require('@opentelemetry/tracing');
const { CollectorTraceExporter } = require('@opentelemetry/exporter-collector-grpc');
const { trace } = require('@opentelemetry/api');
const { Resource } = require('@opentelemetry/resources');

const provider = new NodeTracerProvider({
  resource: new Resource({
    'service.name': '640.video-processing-opentelemetry-nodejs',
  }),
});
const exporter = new CollectorTraceExporter({
  url: 'http://192.168.1.101:4317',
});
provider.addSpanProcessor(new SimpleSpanProcessor(exporter));
provider.register();

const tracer = trace.getTracer('function');
const SCRIPT_DIR = path.resolve(__dirname);

async function callFfmpeg(args) {
  return tracer.startActiveSpan('call_ffmpeg', { attributes: { 'ffmpeg_args': args } }, async (span) => {
    try {
      const ffmpegPath = path.join(SCRIPT_DIR, 'ffmpeg', 'ffmpeg');
      const { stdout, stderr } = await execFileAsync(ffmpegPath, ['-y', ...args], { stdio: ['ignore', 'pipe', 'pipe'] });
      span.end();
    } catch (error) {
      span.setAttribute('ffmpeg_error', error.message);
      span.end();
      throw new Error(`Invocation of ffmpeg failed! ${error.message}`);
    }
  });
}

async function toGif(video, duration) {
  return tracer.startActiveSpan('to_gif', { attributes: { 'video': video, 'duration': duration } }, async (span) => {
    const output = `/tmp/processed-${path.basename(video)}.gif`;
    await callFfmpeg(['-i', video, '-t', `${duration}`, '-vf', 'fps=10,scale=320:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse', '-loop', '0', output]);
    span.end();
    return output;
  });
}

async function watermark(video, duration) {
  return tracer.startActiveSpan('watermark', { attributes: { 'video': video, 'duration': duration } }, async (span) => {
    const output = `/tmp/processed-${path.basename(video)}`;
    const watermarkFile = path.join(SCRIPT_DIR, 'resources', 'watermark.png');
    await callFfmpeg(['-i', video, '-i', watermarkFile, '-t', `${duration}`, '-filter_complex', 'overlay=main_w/2-overlay_w/2:main_h/2-overlay_h/2', output]);
    span.end();
    return output;
  });
}

async function transcodeMp3(video, duration) {
  return tracer.startActiveSpan('transcode_mp3', { attributes: { 'video': video, 'duration': duration } }, async (span) => {
    span.end();
  });
}

const operations = { 'transcode': transcodeMp3, 'extract-gif': toGif, 'watermark': watermark };

exports.handler = async function(event) {
  return tracer.startActiveSpan('handler', { attributes: { 'event.bucket': event.bucket.bucket, 'event.key': event.object.key } }, async (span) => {
    try {
      const bucket = event.bucket.bucket;
      const input_prefix = event.bucket.input;
      const output_prefix = event.bucket.output;
      const key = event.object.key;
      const duration = event.object.duration;
      const op = event.object.op;
      const download_path = `/tmp/${key}`;

      span.setAttributes({
        'bucket': bucket,
        'input_prefix': input_prefix,
        'output_prefix': output_prefix,
        'key': key,
        'duration': duration,
        'operation': op
      });

      const ffmpegBinary = path.join(SCRIPT_DIR, 'ffmpeg', 'ffmpeg');
      try {
        fs.chmodSync(ffmpegBinary, '755');
      } catch (error) {
        span.setAttribute('chmod_error', error.message);
      }

      const downloadBegin = Date.now();
      await storage_handler.download(bucket, path.join(input_prefix, key), download_path);
      const downloadSize = fs.statSync(download_path).size;
      const downloadStop = Date.now();

      const processBegin = Date.now();
      const upload_path = await operations[op](download_path, duration);
      const processEnd = Date.now();

      const uploadBegin = Date.now();
      const filename = path.basename(upload_path);
      const uploadSize = fs.statSync(upload_path).size;
      const uploadKey = await storage_handler.upload(bucket, path.join(output_prefix, filename), upload_path);
      const uploadStop = Date.now();

      const downloadTime = (downloadStop - downloadBegin) / 1000;
      const uploadTime = (uploadStop - uploadBegin) / 1000;
      const processTime = (processEnd - processBegin) / 1000;

      span.setAttributes({
        'download_time': downloadTime,
        'download_size': downloadSize,
        'upload_time': uploadTime,
        'upload_size': uploadSize,
        'process_time': processTime
      });

      span.end();
      return {
        result: {
          bucket: bucket,
          key: uploadKey
        },
        measurement: {
          download_time: downloadTime,
          download_size: downloadSize,
          upload_time: uploadTime,
          upload_size: uploadSize,
          compute_time: processTime
        }
      };
    } catch (err) {
      span.recordException(err);
      span.setStatus({ code: 2, message: 'Handler error' });
      span.end();
      throw err;
    }
  });
};
