
import datetime
import os
import uuid

import urllib.request

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.resources import Resource


from . import storage
client = storage.storage.get_instance()

resource = Resource(attributes={
    "service.name": "620.uploader-opentelemetry"
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


def handler(event):
    with tracer.start_as_current_span("handler") as span:
        bucket = event.get('bucket').get('bucket')
        output_prefix = event.get('bucket').get('output')
        url = event.get('object').get('url')
        name = os.path.basename(url)
        download_path = '/tmp/{}'.format(name)

        span.set_attribute("bucket", bucket)
        span.set_attribute("output_prefix", output_prefix)
        span.set_attribute("url", url)
        span.set_attribute("download_path", download_path)
        span.set_attribute("name", name)

        process_begin = datetime.datetime.now()
        urllib.request.urlretrieve(url, filename=download_path)
        size = os.path.getsize(download_path)
        process_end = datetime.datetime.now()

        process_time = (process_end - process_begin) / datetime.timedelta(microseconds=1)
        span.add_event("Download completed", {
            "size": size,
            "process_time": process_time
        })

        upload_begin = datetime.datetime.now()
        key_name = client.upload(bucket, os.path.join(output_prefix, name), download_path)
        upload_end = datetime.datetime.now()

        upload_time = (upload_end - upload_begin) / datetime.timedelta(microseconds=1)

        span.add_event("Upload completed", {
            "key_name": key_name,
            "upload_time": upload_time
        })

        span.set_attribute("process_time", process_time)
        span.set_attribute("upload_time", upload_time)
        span.set_attribute("download_size", size)

        return {
                'result': {
                    'bucket': bucket,
                    'url': url,
                    'key': key_name
                },
                'measurement': {
                    'download_time': 0,
                    'download_size': 0,
                    'upload_time': upload_time,
                    'upload_size': size,
                    'compute_time': process_time
                }
        }
