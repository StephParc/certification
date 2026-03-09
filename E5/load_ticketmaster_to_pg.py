# load_ticketmaster_to_pg
"""
Bulk Ticketmaster Data Loader (S3 to PostgreSQL).

This service performs high-volume data ingestion from the S3 Data Lake 
to the PostgreSQL staging schema. It is optimized for initial data 
seeding or full-history synchronization.

Key Features:
1. Recursive S3 Scanning: Uses S3 Paginators to handle buckets containing 
   thousands of objects.
2. High-Performance Batch Insertion: Implements 'psycopg2.extras.execute_batch' 
   to minimize network overhead and database transaction costs.
3. Raw JSON Storage: Persists the full event payload as a JSONB-ready 
   string for downstream dbt transformations.
"""
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
    """
    Orchestrates the bulk transfer of JSON events from S3 to PostgreSQL.

    Iterates through all objects under the specified S3 prefix, downloads 
    each JSON payload, and executes a batch insert into the 
    'raw.ticketmaster_events' table.

    Args:
        prefix (str): The root S3 directory to scan. Defaults to 'E5/ticketmaster/'.
    """
    bucket_name = "zone-brutes"
    try:
        # 1. Listing all files under the prefix using S3 Paginator
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
                
                # 2. Reading JSON content from S3
                data = get_json_from_s3(bucket_name, s3_key)
                if not data: continue
                
                events = data.get("events", [])
                
                # 3. Batch insert for optimized database writing
                query = "INSERT INTO raw.ticketmaster_events (file_name, payload) VALUES (%s, %s)"
                # Preparing tuples for mass insertion
                values = [(s3_key, json.dumps(ev)) for ev in events]
                
                psycopg2.extras.execute_batch(cur, query, values)
                
                count_files += 1
                count_events += len(events)
        
        conn.commit()
        logger.info(f"BULK LOAD COMPLETED: {count_files} files, {count_events} events inserted.")

    except Exception as e:
        logger.error(f"Global Loading Error: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    bulk_load_from_s3()