FROM postgres:16.2

EXPOSE 5432

# Copy initialization scripts
COPY ./init-scripts/ /docker-entrypoint-initdb.d/

# Create a directory for custom configuration
RUN mkdir -p /etc/postgresql/conf.d
COPY ./postgresql.conf /etc/postgresql/conf.d/postgresql.conf

CMD ["postgres", "-c", "config_file=/etc/postgresql/conf.d/postgresql.conf"]
