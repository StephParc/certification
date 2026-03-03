-- setup_ticketmaster.sql

CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.ticketmaster_events (
    id SERIAL PRIMARY KEY, 
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    file_name TEXT, 
    payload JSONB
);

CREATE INDEX IF NOT EXISTS idx_ticketmaster_filename ON raw.ticketmaster_events (file_name);

DROP USER IF EXISTS :"user_ro";
CREATE USER :"user_ro" WITH PASSWORD :'pass_ro';

DROP ROLE IF EXISTS analyst_group;
CREATE ROLE analyst_group;
GRANT analyst_group TO :"user_ro";
GRANT USAGE ON SCHEMA raw TO analyst_group;
GRANT SELECT ON ALL TABLES IN SCHEMA raw TO analyst_group;