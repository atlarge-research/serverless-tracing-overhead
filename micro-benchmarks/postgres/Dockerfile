FROM postgres:latest

# Set environment variables
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres

EXPOSE 5432

# Copy initialization scripts
COPY ./init-scripts/ /docker-entrypoint-initdb.d/
