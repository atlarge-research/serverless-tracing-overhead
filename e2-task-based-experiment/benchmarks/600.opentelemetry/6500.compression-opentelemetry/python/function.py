import datetime
import io
import os
import shutil
import uuid
import zlib

from . import storage
client = storage.storage.get_instance()

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.resources import Resource

resource = Resource(attributes={
    "service.name": "650.compression-opentelemetry"
})

trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer("function")

# Setup the OTLP exporter to send traces to the collector using HTTP
otlp_exporter = OTLPSpanExporter(
    endpoint="http://<REPLACE_ME>:4317",
    insecure=True
)

# Setup the span processor with the exporter
span_processor = SimpleSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

def parse_directory(directory, parent_span):
    with tracer.start_as_current_span("parse_directory", trace.set_span_in_context(parent_span)) as span:
        size = 0
        for root, dirs, files in os.walk(directory):
            for file in files:
                size += os.path.getsize(os.path.join(root, file))
        span.set_attribute("directory_size", size)
        return size

def handler(event):
    span = tracer.start_span("handler")
    ctx = trace.set_span_in_context(span)

    bucket = event.get('bucket').get('bucket')
    input_prefix = event.get('bucket').get('input')
    output_prefix = event.get('bucket').get('output')
    key = event.get('object').get('key')
    download_path = '/tmp/{}-{}'.format(key, uuid.uuid4())
    os.makedirs(download_path)

    span.set_attribute("bucket", bucket)
    span.set_attribute("input_prefix", input_prefix)
    span.set_attribute("output_prefix", output_prefix)
    span.set_attribute("key", key)
    span.set_attribute("download_path", download_path)

    download_span = tracer.start_span("download", context=ctx)
    client.download_directory(bucket, os.path.join(input_prefix, key), download_path)
    download_span.end()

    size = parse_directory(download_path, span)
    span.set_attribute("download_size", size)

    compress_span = tracer.start_span("compress", context=ctx)
    shutil.make_archive(os.path.join(download_path, key), 'zip', root_dir=download_path)
    compress_span.end()

    upload_span = tracer.start_span("upload", context=ctx)
    archive_name = '{}.zip'.format(key)
    archive_size = os.path.getsize(os.path.join(download_path, archive_name))
    key_name = client.upload(bucket, os.path.join(output_prefix, archive_name), os.path.join(download_path, archive_name))
    upload_span.end()

    span.set_attribute("upload_size", archive_size)
    span.set_attribute("key_name", key_name)

    span.end()
    return {
        'result': {
            'bucket': bucket,
            'key': key_name
        }
    }
