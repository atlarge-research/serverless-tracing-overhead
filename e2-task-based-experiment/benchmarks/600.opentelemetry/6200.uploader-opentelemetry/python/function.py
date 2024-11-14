
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
    endpoint="http://<REPLACE_ME>:4317",
    insecure=True
)

# Setup the span processor with the exporter
span_processor = SimpleSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)


def handler(event):
    span = tracer.start_span("handler")
    ctx = trace.set_span_in_context(span)

    bucket = event.get('bucket').get('bucket')
    output_prefix = event.get('bucket').get('output')
    url = event.get('object').get('url')
    upload_key = os.path.basename(url)
    download_path = '/tmp/{}'.format(upload_key)

    span.set_attribute("bucket", bucket)
    span.set_attribute("output_prefix", output_prefix)
    span.set_attribute("url", url)
    span.set_attribute("download_path", download_path)
    span.set_attribute("upload_key", upload_key)

    download_span = tracer.start_span("download", context=ctx)
    urllib.request.urlretrieve(url, filename=download_path)
    download_span.end()

    upload_span = tracer.start_span("upload", context=ctx)
    key_name = client.upload(bucket, os.path.join(output_prefix, upload_key), download_path)
    upload_span.end()

    span.end()

    return {
        'result': {
            'bucket': bucket,
            'url': url,
            'key': key_name
        }
    }
