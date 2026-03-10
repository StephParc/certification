# load_to_db.py
"""
Ticketmaster Raw Data Ingestion Service (S3 to SQL).

This module facilitates the transition of raw event data from the 
S3 Data Lake (Bronze zone) to a PostgreSQL staging environment. 

Key Operational Features:
1. Idempotency Check: Verifies if a file has already been processed by 
   checking the 'file_name' in the destination table.
2. Batch Insertion: Uses 'psycopg2.extras.execute_batch' to optimize 
   database write performance for large JSON payloads.
3. Automated Partition Scanning: Processes files based on a daily folder 
   structure (YYYY-MM-DD).
"""
import boto3
import json
import psycopg2
import psycopg2.extras
from datetime import datetime
from config.config import SQL_TICKETMASTER_URL, KEY_ID_DL_RW, SECRET_KEY_DL_RW, DL_ENDPOINT, DL_REGION
from utils.S3_utils import get_s3_client, get_json_from_s3
from utils.logger_config import setup_logger, trace_action

logger_name = "E5 - LOAD RAW"
logger = setup_logger(logger_name)
s3 = get_s3_client()

@trace_action(logger_name)
def load_ticketmaster_file_to_bd(folder_date=datetime.now().strftime("%Y-%m-%d")):
    """
    Synchronizes JSON event files from S3 to the PostgreSQL 'raw' schema.

    The function scans a specific folder on S3, reads each JSON document, 
    and inserts the individual event payloads into the 'ticketmaster_events' 
    table. It ensures database integrity by rolling back on failure.

    Args:
        folder_date (str): The S3 partition to scan (format: YYYY-MM-DD). 
                           Defaults to the current date.
    """
    bucket_name = "zone-brutes"
    prefix = f"E5/ticketmaster/{folder_date}/"
    try:
        # 1. Folder Scanning logic via S3 Paginator
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
                
                # 2. Idempotency logic: check if the file was already processed
                cur.execute("SELECT 1 FROM raw.ticketmaster_events WHERE file_name = %s LIMIT 1", (s3_key,))
                if cur.fetchone():
                    logger.info(f"File {s3_key} already exists in DB. Skipping.")
                    continue

                logger.info(f"Processing S3 object: {s3_key}")
                
                # 3. Reading and Parsing JSON from Data Lake
                data = get_json_from_s3(bucket_name, s3_key)
                if not data: continue
                
                events = data.get("events", [])
                
                # 4. High-Performance Batch Insertion
                query = "INSERT INTO raw.ticketmaster_events (file_name, payload) VALUES (%s, %s)"
                values = [(s3_key, json.dumps(ev)) for ev in events]
                
                psycopg2.extras.execute_batch(cur, query, values)
                
                count_files += 1
                count_events += len(events)
        
        conn.commit()
        logger.info(f"LOAD COMPLETED: {count_files} files processed, {count_events} events inserted.")

    except Exception as e:
        logger.error(f"Global Ingestion Error: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    load_ticketmaster_file_to_bd()