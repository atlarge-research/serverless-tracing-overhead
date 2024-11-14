#!/usr/bin/env python

import datetime
import os
import stat
import subprocess


from . import storage
client = storage.storage.get_instance()

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.resources import Resource

resource = Resource(attributes={
    "service.name": "640.video-processing-opentelemetry"
})

trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer("function")

# Setup the OTLP exporter to send traces to the collector using HTTP
otlp_exporter = OTLPSpanExporter(
    endpoint="http://192.168.1.109:4317",
    insecure=True
)

# Setup the span processor with the exporter
span_processor = SimpleSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))

def call_ffmpeg(args, ctx):
    with tracer.start_as_current_span("call_ffmpeg", ctx) as span:
        ret = subprocess.run([os.path.join(SCRIPT_DIR, 'ffmpeg', 'ffmpeg'), '-y'] + args,
                             stdin=subprocess.DEVNULL,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        span.set_attribute("ffmpeg_args", args)
        if ret.returncode != 0:
            error_message = ret.stdout.decode('utf-8')
            span.set_attribute("ffmpeg_error", error_message)
            print('Invocation of ffmpeg failed!')
            print('Out: ', error_message)
            raise RuntimeError()

def to_gif(video, duration, event, ctx):
    with tracer.start_as_current_span("to_gif", ctx) as span:
        output = '/tmp/processed-{}.gif'.format(os.path.basename(video))
        span.set_attribute("video", video)
        span.set_attribute("duration", duration)
        call_ffmpeg(["-i", video,
                     "-t", "{0}".format(duration),
                     "-vf", "fps=10,scale=320:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
                     "-loop", "0",
                     output], ctx)
        return output

def watermark(video, duration, event, ctx):
    with tracer.start_as_current_span("watermark", ctx) as span:
        output = '/tmp/processed-{}'.format(os.path.basename(video))
        watermark_file = os.path.dirname(os.path.realpath(__file__))
        span.set_attribute("video", video)
        span.set_attribute("duration", duration)
        call_ffmpeg([
            "-i", video,
            "-i", os.path.join(watermark_file, os.path.join('resources', 'watermark.png')),
            "-t", "{0}".format(duration),
            "-filter_complex", "overlay=main_w/2-overlay_w/2:main_h/2-overlay_h/2",
            output], ctx)
        return output

def transcode_mp3(video, duration, event, parent_span):
    with tracer.start_as_current_span("transcode_mp3", trace.set_span_in_context(parent_span)) as span:
        # Implementation of transcode_mp3 if it exists
        span.end()
        pass

operations = { 'transcode': transcode_mp3, 'extract-gif': to_gif, 'watermark': watermark }

def handler(event):
    span = tracer.start_span("handler")
    ctx = trace.set_span_in_context(span)

    bucket = event.get('bucket').get('bucket')
    input_prefix = event.get('bucket').get('input')
    output_prefix = event.get('bucket').get('output')
    key = event.get('object').get('key')
    duration = event.get('object').get('duration')
    op = event.get('object').get('op')
    download_path = '/tmp/{}'.format(key)

    span.set_attribute("bucket", bucket)
    span.set_attribute("input_prefix", input_prefix)
    span.set_attribute("output_prefix", output_prefix)
    span.set_attribute("key", key)
    span.set_attribute("duration", duration)
    span.set_attribute("operation", op)

    ffmpeg_binary = os.path.join(SCRIPT_DIR, 'ffmpeg', 'ffmpeg')
    try:
        st = os.stat(ffmpeg_binary)
        os.chmod(ffmpeg_binary, st.st_mode | stat.S_IEXEC)
    except OSError as e:
        span.set_attribute("chmod_error", str(e))

    download_span = tracer.start_span("download", context=ctx)
    client.download(bucket, os.path.join(input_prefix, key), download_path)
    download_span.end()
    download_size = os.path.getsize(download_path)
    span.set_attribute("download_size", download_size)

    process_span = tracer.start_span("process", context=ctx)
    upload_path = operations[op](download_path, duration, event, ctx)
    process_span.end()

    upload_span = tracer.start_span("upload", context=ctx)
    filename = os.path.basename(upload_path)
    upload_size = os.path.getsize(upload_path)
    upload_key = client.upload(bucket, os.path.join(output_prefix, filename), upload_path)
    upload_span.end()

    span.set_attribute("upload_size", upload_size)

    span.end()
    return {
        'result': {
            'bucket': bucket,
            'key': upload_key
        }
    }
