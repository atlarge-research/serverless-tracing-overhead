import datetime
import io
import os
import sys
import uuid
from urllib.parse import unquote_plus
from PIL import Image

from . import storage
client = storage.storage.get_instance()

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.resources import Resource

resource = Resource(attributes={
    "service.name": "630.thumbnailer-opentelemetry"
})

trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer("function")

otlp_exporter = OTLPSpanExporter(
    endpoint="http://<REPLACE_ME>:4317",
    insecure=True
)

span_processor = SimpleSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

def resize_image(image_bytes, w, h, ctx):
    with tracer.start_as_current_span("resize_image", ctx) as span:
        span.set_attribute("width", w)
        span.set_attribute("height", h)
        
        with Image.open(io.BytesIO(image_bytes)) as image:
            image.thumbnail((w, h))
            out = io.BytesIO()
            image.save(out, format='jpeg')
            out.seek(0)
            resized_size = out.getbuffer().nbytes
            span.set_attribute("resized_size", resized_size)
            return out

def handler(event):
    span = tracer.start_span("handler")
    ctx = trace.set_span_in_context(span)

    bucket = event.get('bucket').get('bucket')
    input_prefix = event.get('bucket').get('input')
    output_prefix = event.get('bucket').get('output')
    key = unquote_plus(event.get('object').get('key'))
    width = event.get('object').get('width')
    height = event.get('object').get('height')

    span.set_attribute("bucket", bucket)
    span.set_attribute("input_prefix", input_prefix)
    span.set_attribute("output_prefix", output_prefix)
    span.set_attribute("key", key)
    span.set_attribute("width", width)
    span.set_attribute("height", height)

    download_span = tracer.start_span("download", context=ctx)
    img = client.download_stream(bucket, os.path.join(input_prefix, key))
    download_span.end()

    resize_span = tracer.start_span("resize", context=ctx)
    resized = resize_image(img, width, height, ctx)
    resized_size = resized.getbuffer().nbytes
    resize_span.end()

    upload_span = tracer.start_span("upload", context=ctx)
    key_name = client.upload_stream(bucket, os.path.join(output_prefix, key), resized)
    upload_span.end()

    span.set_attribute("download_size", len(img))
    span.set_attribute("upload_size", resized_size)
    span.end()

    return {
        'result': {
            'bucket': bucket,
            'key': key_name
        }
    }
