# ticketmaster_harvester.py
"""
Ticketmaster API Events Harvester.

This module automates the daily extraction of musical events from the 
Ticketmaster Discovery API. It handles:
1. Time-windowed filtering (current day).
2. Automated pagination and results aggregation.
3. API Rate Limiting to prevent IP blacklisting.
4. Automated landing in the S3 Data Lake (Bronze Zone).
"""
import os
import json
import requests
import time
from datetime import datetime, timedelta, timezone

from config.config import DL_ENDPOINT, KEY_ID_DL_RW, SECRET_KEY_DL_RW, DL_REGION, TICKETMASTER_CONSUMER_KEY, TICKETMASTER_CONSUMER_SECRET
from utils.S3_utils import upload_file
from utils.logger_config import setup_logger, trace_action

logger_name = "E5 - API Ticketmaster"
logger = setup_logger(logger_name)

@trace_action(logger_name)
def run_daily_ingestion(country_code="US"):
    """
    Executes the daily ingestion process for a specific country.

    Queries the Ticketmaster Discovery v2 API for music segments scheduled 
    for the current date. Results are aggregated, paginated, and saved as 
    a JSON document before being uploaded to the Garage S3 Data Lake.

    Args:
        country_code (str): Two-letter ISO country code (default: "US").
    """
    url = "https://app.ticketmaster.com/discovery/v2/events.json"

    extraction_date = datetime.now()
    # Define the 24h window for the current day in UTC
    start_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)
    end_date = start_date.replace(hour=23, minute=59, second=59)
    start_str = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_str = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")

    all_events = []
    page = 0
    total_pages = 1

    while page < total_pages:
        params = {
        "apikey": TICKETMASTER_CONSUMER_KEY,
        "countryCode": country_code,
        "segmentName": "Music",
        "startDateTime": start_str,
        "endDateTime": end_str,
        "size": 200,
        "page": page,
        "sort": "date,asc"
    }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # Update total pages from API response (limited to 5 for the demo)
            page_info = data.get("page", {})
            total_pages = min(page_info.get("totalPages", 1),5)
            
            events = data.get("_embedded", {}).get("events", [])
            all_events.extend(events)

            logger.info(f"Page {page + 1}/{total_pages} récupérée ({len(events)} événements)")

            # Defensive sleep to respect Ticketmaster's Rate Limiting (0.2s)
            time.sleep(0.2) 
            
            page += 1

            # Hard cap for the Discovery API's free tier
            if len(all_events) >= 1000:
                logger.warning("Reached 1000 events limit (Discovery API quota).")
                break

        except Exception as e:
            logger.error(f"Error at page {page}: {e}")
            break

    if not all_events:
        logger.warning(f"No events found for {country_code}")
        return
    
    # Storage in S3 organized by extraction date
    date_folder = extraction_date.strftime("%Y-%m-%d")
    filename = f"ticketmaster_{country_code}_{date_folder}.json"
    local_path = f"/tmp/{filename}"

    with open(local_path, "w", encoding="utf-8") as f:
        json.dump({"events": all_events, 
                   "metadata":{
                        "total": len(all_events), 
                        "country": country_code,
                        "extract_date": extraction_date.strftime("%Y-%m-%d %H:%M:%S")
                        }
                    }, f, ensure_ascii=False, indent=4)
        
    s3_dest_path = f"E5/ticketmaster/{date_folder}/{filename}"
    
    # Upload to S3 with governance metadata
    if upload_file(
        local_path=local_path, 
        bucket="zone-brutes", 
        s3_path=s3_dest_path, 
        metadata={
            "source": "Ticketmaster_API",
            "step": "bronze",
            "owner": "Harmonie",
            "dag": "daily_ticketmaster_update_dag.py",
            "destination": "ticketmaster.raw.ticketmaster_events"
        }):
        logger.info(f"Ingestion successful for {country_code} : {len(all_events)} events uploaded to S3.")
        os.remove(local_path)

if __name__ == "__main__":
    run_daily_ingestion()

