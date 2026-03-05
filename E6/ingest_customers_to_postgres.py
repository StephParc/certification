# ingest_customers_to_postgres.py
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
    s3 = get_s3_client()
    bucket_name = "zone-brutes"
    key = f"E6/musicshop/customers.csv"

    try:
        response = s3.get_object(Bucket=bucket_name, Key=key)
        csv_content = response['Body'].read().decode('utf-8')
        f = io.StringIO(csv_content)
        logger.info(f"Fichier {key} récupéré avec succès depuis S3")
    except Exception as e:
        logger.error(f"Impossible de récupérer le fichier sur S3: {e}")
        return
    
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

