-- setup_musicshop.sql
/*
 * Musicshop Analytics Infrastructure Setup.
 *
 * This script initializes the PostgreSQL environment for the Musicshop 
 * data warehouse. It implements a Medallion Architecture and a 
 * Role-Based Access Control (RBAC) security model.
 *
 * Components:
 * 1. RBAC: Definition of 'analyst_group' and 'editor_role'.
 * 2. User Provisioning: Stored procedure for secure editor creation.
 * 3. Schema Layering: Creation of 'raw', 'silver', and 'gold' zones.
 * 4. Staging Tables: Definitions for exchange rates, customers, and orders.
 */

-- Role-Based Access Control (RBAC) Initialization
-- Ensures that roles exist before granting permissions.

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'analyst_group') THEN
        CREATE ROLE analyst_group;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'editor_role') THEN
        CREATE ROLE editor_role;
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS public.editor_metadata (
    db_user TEXT PRIMARY KEY,
    editor_name TEXT NOT NULL
);

/*
 * FUNCTION: create_editor
 * -----------------------
 * Automates the creation of database users with restricted permissions.
 * Uses SECURITY DEFINER to allow execution by non-superusers while 
 * maintaining strict metadata tracking in 'public.editor_metadata'.
 */

CREATE OR REPLACE FUNCTION create_editor(username TEXT, password TEXT, e_name TEXT) 
RETURNS VOID AS $$
BEGIN
    EXECUTE format('CREATE USER %I WITH PASSWORD %L', username, password);
    EXECUTE format('GRANT editor_role TO %I', username);
    INSERT INTO public.editor_metadata (db_user, editor_name) 
    VALUES (username, e_name)
    ON CONFLICT (db_user) DO UPDATE SET editor_name = EXCLUDED.editor_name;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

GRANT USAGE ON SCHEMA gold TO analyst_group;
GRANT USAGE ON SCHEMA gold TO editor_role;

ALTER DEFAULT PRIVILEGES IN SCHEMA gold GRANT SELECT ON TABLES TO analyst_group;
ALTER DEFAULT PRIVILEGES IN SCHEMA gold GRANT SELECT ON TABLES TO editor_role;

CREATE TABLE IF NOT EXISTS raw.exchange_rates (
    date_key DATE,
    currency_code VARCHAR(3),
    exchange_rate DECIMAL(10,6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (date_key, currency_code)
);

CREATE TABLE IF NOT EXISTS raw.customer (
    customer_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255),
    address VARCHAR(255),
    postal_code VARCHAR(20),
    email VARCHAR(255),
    country VARCHAR(100),
    city VARCHAR(100),
    profile VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw.raw_orders(
    order_id VARCHAR(20),
    customer_id VARCHAR(50),
    system_source VARCHAR(20),
    name VARCHAR(255),
    address VARCHAR(255),
    postal_code VARCHAR(20),
    email VARCHAR(255),
    country VARCHAR(100),
    profile VARCHAR(50),
    order_date TIMESTAMP,
    partition_id INT,
    titre VARCHAR(255),
    ref_editeur VARCHAR(100),
    edition VARCHAR(255),
    quantity INT,
    local_price DECIMAL(15,2)
);
