FROM python:3.9-slim

WORKDIR /app

COPY .. /app

ARG REQUIREMENTS_FILE=requirements.txt
RUN pip install --no-cache-dir -r $REQUIREMENTS_FILE

EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
