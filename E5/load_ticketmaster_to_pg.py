# load_ticketmaster_to_pg
import boto3
import json
import psycopg2
import psycopg2.extras
from config.config import SQL_TICKETMASTER_URL, KEY_ID_DL_RW, SECRET_KEY_DL_RW, DL_ENDPOINT, DL_REGION
from utils.S3_utils import get_s3_client, get_json_from_s3
from utils.logger_config import setup_logger, trace_action

logger_name = "E5 - LOAD RAW"
logger = setup_logger(logger_name)
s3 = get_s3_client()

@trace_action(logger_name)
def bulk_load_from_s3(prefix="E5/ticketmaster/"):
    bucket_name = "zone-brutes"
    try:
        # 1. Lister tous les fichiers dans le dossier
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
        
        conn = psycopg2.connect(SQL_TICKETMASTER_URL)
        cur = conn.cursor()
        
        count_files = 0
        count_events = 0

        for page in pages:
            if 'Contents' not in page: continue
            
            for obj in page['Contents']:
                s3_key = obj['Key']
                if not s3_key.endswith('.json'): continue
                
                logger.info(f"Traitement de : {s3_key}")
                
                # 2. Lire le JSON
                data = get_json_from_s3(bucket_name, s3_key)
                if not data: continue
                
                events = data.get("events", [])
                
                # 3. Insertion par lots (Batch insert)
                query = "INSERT INTO raw.ticketmaster_events (file_name, payload) VALUES (%s, %s)"
                # On prépare les données pour l'insertion massive
                values = [(s3_key, json.dumps(ev)) for ev in events]
                
                psycopg2.extras.execute_batch(cur, query, values)
                
                count_files += 1
                count_events += len(events)
        
        conn.commit()
        logger.info(f"TERMINÉ : {count_files} fichiers traités, {count_events} événements insérés.")

    except Exception as e:
        logger.error(f"Erreur globale : {e}")
    finally:
        if conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    bulk_load_from_s3()