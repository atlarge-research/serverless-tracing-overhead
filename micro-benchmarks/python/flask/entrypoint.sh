#!/bin/sh

# Check if OpenTelemetry instrumentation is enabled
if [ "$OPENTELEMETRY" = "true" ]; then
  # Run the application with OpenTelemetry instrumentation
  exec opentelemetry-instrument flask run
else
  # Run the application without OpenTelemetry instrumentation
  exec flask run
fi
