# clean_scrapy.py
"""
Scrapy Data Cleaning and Delta Processing Module.

This module automates the transition of scraped data from the S3 Landing Zone 
(zone-brutes) to the Cleaned Data Zone (zone-propres). It identifies new 
records by comparing the latest extraction against the cumulative history, 
manages archival backups, and prepares delta files for database ingestion.

Data Pipeline:
1. Extract: Reads the latest 'last' and historical 'all' files from S3.
2. Transform: Filters rows to isolate strictly new musical works.
3. Load: Updates the master historical file and creates a timestamped archive.
"""
import pandas as pd
from datetime import date
from utils.S3_utils import read_csv_from_datalake, upload_file
from utils.logger_config import setup_logger, trace_action

logger_name = "E4 - Nettoyage scrapy"
logger = setup_logger(logger_name)

@trace_action(logger_name)
def clean_scrapy_S3():
    """
    Main orchestration function for S3-based delta cleaning.

    Performs a tuple-based comparison between the latest scraping results 
    and the historical dataset. If new items are detected, it triggers 
    a multi-step archival and synchronization process on the Data Lake.

    Returns:
        bool: True if new records were processed, False otherwise.
    """
    # Current date for timestamping
    date_du_jour = date.today()
    date_str = date.today().strftime("%Y-%m-%d")

    # Configuration to prevent type inference issues (e.g., stripping leading zeros)
    DTYPE_CONFIG = {'ISMN': str, 'annee_sortie': str}

    # Reading files from S3 Data Lake
    df_last = read_csv_from_datalake("zone-brutes", "E4/musicshop_last.csv", dtype=DTYPE_CONFIG)
    if df_last is None:
        logger.critical("Critical Error: Unable to read source file from S3")
        return False
    
    df_all = read_csv_from_datalake("zone-propres", "E4/musicshop_all.csv", dtype=DTYPE_CONFIG)
    if df_all is None:
        logger.info("Historical file not found. Initializing new history")
        df_all =pd.DataFrame(columns=df_last.columns)

    # Delta logic: Filter rows in df_last that are NOT in df_all
    df_new = df_last[~df_last.apply(tuple, 1).isin(df_all.apply(tuple, 1))].copy()

    if not df_new.empty:
        # Temporary local paths for S3 upload operations
        tmp_new = "/tmp/musicshop_new.csv"
        tmp_all = "/tmp/musicshop_all.csv"
        tmp_archive = "/tmp/musicshop_archive.csv"
        tmp_old_all = "/tmp/musicshop_old_all.csv"

        # Step 1: Secure the previous version of 'all' in archives
        df_all.to_csv(tmp_old_all, index=False)
        upload_file(
            local_path=tmp_old_all, 
            bucket="zone-propres", 
            s3_path="E4/archives/musicshop_all.csv",
            metadata={
                "source": "Scraping musicshopeurope",
                "dag": "daily_musicshop_update_dag.py",
                "destination": "zone-propres/E4/archives/"
            })

        # Step 2: Save the new deltas (to be picked up by the SQL ingestion DAG)
        df_new.to_csv(tmp_new, index=False)
        upload_file(
            local_path=tmp_new, 
            bucket="zone-propres", 
            s3_path="E4/musicshop_new.csv",
            metadata={
                "source": "zone-brutes/E4/musicshop_last.csv et zone-propres/E4/musicshop_all.csv",
                "dag": "daily_musicshop_update_dag.py",
                "destination": "hbm.public.TB_[auteur, partition]"
            })

        # Step 3: Merge new records into the master history 
        df_combined = pd.concat([df_new, df_all], ignore_index=True)
        df_combined.to_csv(tmp_all, index=False)     
        upload_file(
            local_path=tmp_all, 
            bucket="zone-propres", 
            s3_path="E4/musicshop_all.csv",
            metadata={
                "source": "Scraping musicshopeurope",
                "dag": "daily_musicshop_update_dag.py",
                "destination": "zone-propres/E4/"
            })

        # Step 4: Create a timestamped audit archive for the specific day
        df_new["date_ajout"] = date_du_jour
        df_new.to_csv(tmp_archive, index=False)
        upload_file(
            local_path=tmp_archive, 
            bucket="zone-propres", 
            s3_path=f"E4/archives/musicshop_{date_str}.csv",
            metadata={
                "source": "zone-propres/E4/musicshop_new.csv",
                "dag": "daily_musicshop_update_dag.py",
                "destination": "zone-propres/E4/archives/"
            })

        logger.info(f"Processing complete: {len(df_new)} new records added.")
        return True
    
    logger.info("No new data detected. Skipping S3 updates.")
    return False

if __name__ == "__main__":
    clean_scrapy_S3()