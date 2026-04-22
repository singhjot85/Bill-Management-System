FROM postgres:13.2 as postgres

COPY compose/local/pg/create_database.sh /usr/local/bin/postgres_scripts/
RUN chmod +x /usr/local/bin/postgres_scripts/create_database.sh
RUN rm -rf /usr/local/bin/postgres_scripts