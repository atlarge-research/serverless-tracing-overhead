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
    endpoint="http://192.168.1.101:4317",
    insecure=True
)

# Setup the span processor with the exporter
span_processor = SimpleSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

def parse_directory(directory):
    with tracer.start_as_current_span("parse_directory") as span:
        size = 0
        for root, dirs, files in os.walk(directory):
            for file in files:
                size += os.path.getsize(os.path.join(root, file))
        span.set_attribute("directory_size", size)
        return size

def handler(event):
    with tracer.start_as_current_span("handler") as span:
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

        s3_download_begin = datetime.datetime.now()
        client.download_directory(bucket, os.path.join(input_prefix, key), download_path)
        s3_download_stop = datetime.datetime.now()
        download_time = (s3_download_stop - s3_download_begin) / datetime.timedelta(microseconds=1)
        span.add_event("S3 download completed", {"download_time": download_time})

        size = parse_directory(download_path)
        span.set_attribute("download_size", size)

        compress_begin = datetime.datetime.now()
        shutil.make_archive(os.path.join(download_path, key), 'zip', root_dir=download_path)
        compress_end = datetime.datetime.now()
        process_time = (compress_end - compress_begin) / datetime.timedelta(microseconds=1)
        span.add_event("Compression completed", {"process_time": process_time})

        s3_upload_begin = datetime.datetime.now()
        archive_name = '{}.zip'.format(key)
        archive_size = os.path.getsize(os.path.join(download_path, archive_name))
        key_name = client.upload(bucket, os.path.join(output_prefix, archive_name), os.path.join(download_path, archive_name))
        s3_upload_stop = datetime.datetime.now()
        upload_time = (s3_upload_stop - s3_upload_begin) / datetime.timedelta(microseconds=1)
        span.add_event("S3 upload completed", {"upload_time": upload_time})
        
        span.set_attribute("upload_size", archive_size)

        return {
            'result': {
                'bucket': bucket,
                'key': key_name
            },
            'measurement': {
                'download_time': download_time,
                'download_size': size,
                'upload_time': upload_time,
                'upload_size': archive_size,
                'compute_time': process_time
            }
        }