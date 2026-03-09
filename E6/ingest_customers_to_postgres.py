# ingest_customers_to_postgres.py
"""
Musicshop Customer Ingestion Service (S3 to PostgreSQL).

This module automates the bulk loading of synthetic customer data from the 
S3 Data Lake into the analytical PostgreSQL environment. 

Key Operational Features:
1. S3 Stream Processing: Fetches CSV data directly into memory via io.StringIO 
   to avoid local disk overhead.
2. High-Speed Ingestion: Utilizes the PostgreSQL 'COPY' command via 
   'copy_expert' for maximum throughput during bulk loads.
3. Fresh Load Strategy: Executes a 'TRUNCATE' command before ingestion to 
   ensure the staging table represents the latest source state.
"""
import boto3
import csv
import psycopg2
import psycopg2.extras
import io
from datetime import datetime
from config.config import SQL_MUSICSHOP_URL
from utils.S3_utils import get_s3_client
from utils.logger_config import setup_logger, trace_action

logger_name = "E6 - Chargement clients"
logger = setup_logger(logger_name)

@trace_action(logger_name)
def ingest_customers():
    """
    Orchestrates the transfer of customer data from S3 to the 'raw.customer' table.

    Steps:
    1. Retrieve the 'customers.csv' file from the 'zone-brutes' S3 bucket.
    2. Establish a connection to the Musicshop database.
    3. Truncate the existing 'raw.customer' table to prevent duplicates.
    4. Execute a bulk 'COPY' operation for high-performance data transfer.
    """
    s3 = get_s3_client()
    bucket_name = "zone-brutes"
    key = f"E6/musicshop/customers.csv"

    # Fetching the source file from S3
    try:
        response = s3.get_object(Bucket=bucket_name, Key=key)
        csv_content = response['Body'].read().decode('utf-8')
        f = io.StringIO(csv_content)
        logger.info(f"Fichier {key} récupéré avec succès depuis S3")
    except Exception as e:
        logger.error(f"Impossible de récupérer le fichier sur S3: {e}")
        return
    
    # Executing the Database Load
    try:
        conn = psycopg2.connect(SQL_MUSICSHOP_URL)
        cur = conn.cursor()

        cur.execute("TRUNCATE TABLE raw.customer;")

        copy_sql = """
            COPY raw.customer (
                customer_id,
                name,
                address,
                postal_code,
                email,
                country,
                city,
                profile,
                created_at
            ) FROM STDIN WITH (FORMAT CSV, HEADER, DELIMITER ',');
        """

        cur.copy_expert(sql=copy_sql, file=f)

        conn.commit()
        logger.info(f"Ingestion réussie: {cur.rowcount} clients chargés")

        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"Erreur lors de l'ingestion: {e}")

if __name__ == "__main__":
    ingest_customers()

