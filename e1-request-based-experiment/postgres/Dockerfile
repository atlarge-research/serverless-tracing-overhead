FROM postgres:16.2

EXPOSE 5432

# Copy initialization scripts
COPY ./init-scripts/ /docker-entrypoint-initdb.d/

# Ensure scripts are readable
RUN chmod -R a+r /docker-entrypoint-initdb.d/

# Create a directory for custom configuration
RUN mkdir -p /etc/postgresql/conf.d
COPY ./postgresql.conf /etc/postgresql/conf.d/postgresql.conf
COPY ./pg_hba.conf /etc/postgresql/conf.d/pg_hba.conf

CMD ["postgres", "-c", "config_file=/etc/postgresql/conf.d/postgresql.conf", "-c", "hba_file=/etc/postgresql/conf.d/pg_hba.conf"]
