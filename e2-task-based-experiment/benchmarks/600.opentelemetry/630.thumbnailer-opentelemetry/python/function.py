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
    endpoint="http://192.168.1.109:4317",
    insecure=True
)

span_processor = SimpleSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

def resize_image(image_bytes, w, h):
    with tracer.start_as_current_span("resize_image") as span:
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
    with tracer.start_as_current_span("handler") as span:
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

        download_begin = datetime.datetime.now()
        img = client.download_stream(bucket, os.path.join(input_prefix, key))
        download_end = datetime.datetime.now()
        download_time = (download_end - download_begin) / datetime.timedelta(microseconds=1)

        span.add_event("Download completed", {
            "size": len(img),
            "download_time": download_time
        })

        process_begin = datetime.datetime.now()
        resized = resize_image(img, width, height)
        resized_size = resized.getbuffer().nbytes
        process_end = datetime.datetime.now()
        process_time = (process_end - process_begin) / datetime.timedelta(microseconds=1)

        span.add_event("Image resized", {
            "resized_size": resized_size,
            "process_time": process_time
        })

        upload_begin = datetime.datetime.now()
        key_name = client.upload_stream(bucket, os.path.join(output_prefix, key), resized)
        upload_end = datetime.datetime.now()
        upload_time = (upload_end - upload_begin) / datetime.timedelta(microseconds=1)

        span.add_event("Upload completed", {
            "key_name": key_name,
            "upload_time": upload_time
        })

        span.set_attribute("download_time", download_time)
        span.set_attribute("upload_time", upload_time)
        span.set_attribute("process_time", process_time)
        span.set_attribute("download_size", len(img))
        span.set_attribute("upload_size", resized_size)

        return {
            'result': {
                'bucket': bucket,
                'key': key_name
            },
            'measurement': {
                'download_time': download_time,
                'download_size': len(img),
                'upload_time': upload_time,
                'upload_size': resized_size,
                'compute_time': process_time
            }
        }
