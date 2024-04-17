FROM python:3.9-slim

WORKDIR /app

COPY .. /app

ARG REQUIREMENTS_FILE=requirements.txt
RUN pip install --no-cache-dir -r $REQUIREMENTS_FILE

EXPOSE 8080

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ARG OPENTELEMETRY=False
ENV OPENTELEMETRY=$OPENTELEMETRY

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
