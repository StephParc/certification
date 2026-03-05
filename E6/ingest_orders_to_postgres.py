# ingest_orders_to_postgres.py
import boto3
import csv
import psycopg2
import psycopg2.extras
import io
from datetime import datetime
from config.config import SQL_MUSICSHOP_URL
from utils.S3_utils import get_s3_client, move_s3_object
from utils.logger_config import setup_logger, trace_action

logger_name = "E6 - Ingestion commandes"
logger = setup_logger(logger_name)

@trace_action(logger_name)
def ingest_all_pending_orders():
    LANDING_PREFIX = "E6/musicshop/orders/"
    ARCHIVE_PREFIXE = "E6/musicshop/archives/orders/"
    BUCKET = "zone-brutes"

    s3 = get_s3_client()
    response = s3.list_objects_v2(Bucket=BUCKET, Prefix=LANDING_PREFIX)

    if 'Contents' not in response:
        logger.info("Rien à traîter")
        return
   
    try:
        conn = psycopg2.connect(SQL_MUSICSHOP_URL)
        cur = conn.cursor()

        
        for obj in response['Contents']:
            file_key = obj['Key']
            if file_key.endswith('/'): continue

            logger.info(f"Traitement du fichier: {file_key}")

            try:
                file_obj = s3.get_object(Bucket=BUCKET, Key=file_key)
                csv_content = file_obj['Body'].read().decode('utf-8')
                f = io.StringIO(csv_content)
            except Exception as e:
                logger.error(f"Erreur lecture S3 pour {file_key}: {e}")
                continue

            try:
                copy_sql = """
                    COPY raw.raw_orders (
                        order_id,
                        customer_id,
                        system_source,
                        name,
                        address,
                        postal_code,
                        email,
                        country,
                        profile,
                        order_date,
                        partition_id,
                        titre,
                        ref_editeur,
                        edition,
                        quantity,
                        local_price
                    ) FROM STDIN WITH (FORMAT CSV, HEADER, DELIMITER ',');
                """

                cur.copy_expert(sql=copy_sql, file=f)
                conn.commit()
                logger.info(f"Fichier {file_key} injecté avec succès ({cur.rowcount} lignes de commandes)")

                new_path = move_s3_object(BUCKET, file_key, LANDING_PREFIX, ARCHIVE_PREFIXE)
                logger.info(f"Fichier archivé vers: {new_path}")

            except Exception as e:
                conn.rollback()
                logger.error(f"Erreur lors de l'ingestion du fichier: {file_key}. {e}")

        cur.close()
        conn.close()   

    except Exception as e:
        logger.error(f"Erreur de connexion base de données: {e}")
        raise

if __name__ == "__main__":
    ingest_all_pending_orders()

