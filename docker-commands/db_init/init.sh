#!/bin/bash
set -e

echo '>>> Create the roles and databases'
psql -v ON_ERROR_STOP=0 --username "$POSTGRES_USER" <<-EOSQL
    -- Extensions
    CREATE EXTENSION unaccent;

    -- Databases
    CREATE DATABASE db_video_hub;

    -- Users
    CREATE USER $DATABASE_USER WITH PASSWORD '$DATABASE_PASSWORD';
    ALTER USER $DATABASE_USER CREATEDB;

    GRANT ALL PRIVILEGES ON DATABASE db_video_hub TO $DATABASE_USER;
EOSQL