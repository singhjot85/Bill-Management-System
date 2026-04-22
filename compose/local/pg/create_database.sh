#!/bin/bash

set -U

local database=$DB_USER
echo "Creating Database >>> '$database'"
echo "Postgres Password >>> '$DB_PASS'"
PGPASSWORD=$DB_PASS psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    DROP DATABASE IF EXISTS $database;
    DROP USER IF EXSISTS $database;
    CREATE USER $database;
    CREATE DATABASE $database;
    GRANT ALL PRIVILEGES ON DATABASE $database TO $database;
    CREATE EXTENSIONS if not exists btree_gist WITH SCHEMA pg_catalog;
    CREATE EXTENSIONS if not exists btree_gin WITH SCHEMA pg_catalog;
    CREATE EXTENSIONS if not exists pg_trgm WITH SCHEMA pg_catalog;
EOSQL