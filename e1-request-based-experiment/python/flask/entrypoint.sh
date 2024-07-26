#!/bin/sh

# Check if OpenTelemetry instrumentation is enabled
if [ "$OPENTELEMETRY" = "true" ]; then
  # Run the application with OpenTelemetry instrumentation
  exec opentelemetry-instrument gunicorn app:app -c gunicorn_conf.py
else
  # Run the application without OpenTelemetry instrumentation
  exec gunicorn app:app -c gunicorn_conf.py
fi
