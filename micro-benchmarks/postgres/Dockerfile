FROM postgres:latest

EXPOSE 5432

# Copy initialization scripts
COPY ./init-scripts/ /docker-entrypoint-initdb.d/
