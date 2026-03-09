# ingest_rates_to_postgres.py
"""
Musicshop Exchange Rate Ingestion Service (S3 to PostgreSQL).

This module automates the daily retrieval of currency exchange rates from 
the S3 Data Lake and their ingestion into the analytical staging area.

Key Technical Features:
1. Automated Key Resolution: Dynamically constructs the S3 path based on 
   the current execution date.
2. Memory-to-DB Streaming: Uses 'io.StringIO' to pipe CSV data from S3 
   directly into the database, bypassing local file storage.
3. Native Bulk Ingestion: Leverages 'cur.copy_expert' for high-performance 
   loading into the 'raw.exchange_rates' table.
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

logger_name = "E6 - Chargement taux"
logger = setup_logger(logger_name)

@trace_action(logger_name)
def ingest_rates():
    """
    Synchronizes today's exchange rates from S3 to PostgreSQL.

    The function targets the 'exchange_rates' staging table and performs 
    a bulk copy operation. It is designed to be idempotent when called 
    within a daily orchestration window.
    """
    today = datetime.now().strftime('%Y-%m-%d')
    s3 = get_s3_client()
    bucket_name = "zone-brutes"
    key = f"E6/musicshop/exchange_rates/{today}.csv"

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

        copy_sql = """
            COPY raw.exchange_rates (
                date_key,
                currency_code,
                exchange_rate
            ) FROM STDIN WITH (FORMAT CSV, HEADER, DELIMITER ',');
        """

        cur.copy_expert(sql=copy_sql, file=f)

        conn.commit()
        logger.info(f"Ingestion réussie: {cur.rowcount} taux de change chargés")

        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"Erreur lors de l'ingestion: {e}")
        raise

if __name__ == "__main__":
    ingest_rates()

