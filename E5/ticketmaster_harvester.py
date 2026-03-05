# ticketmaster_harvester.py
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
    url = "https://app.ticketmaster.com/discovery/v2/events.json"

    extraction_date = datetime.now()
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

        # Mise à jour du nombre total de pages (fourni par l'API)
            page_info = data.get("page", {})
            total_pages = min(page_info.get("totalPages", 1),5)
            
            # Récupération des événements de la page actuelle
            events = data.get("_embedded", {}).get("events", [])
            all_events.extend(events)

            logger.info(f"Page {page + 1}/{total_pages} récupérée ({len(events)} événements)")

            # Sécurité anti-spam (Rate Limiting)
            # Ticketmaster limite le nombre d'appels par seconde
            time.sleep(0.2) 
            
            page += 1

        # Limite technique de l'API gratuite (souvent limitée à 1000 items max)
            if len(all_events) >= 1000:
                logger.warning("Limite de 1000 événements atteinte (quota API Discovery).")
                break

        except Exception as e:
            logger.error(f"Erreur à la page {page}: {e}")
            break

    if not all_events:
        logger.warning(f"Aucun événement trouvé pour {country_code}")
        return
    
    # stockage dans s3
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
        logger.info(f"Ingestion terminée{country_code} : {len(all_events)} événements dans s3://zone-brutes/{s3_dest_path}")
        os.remove(local_path)

if __name__ == "__main__":
    run_daily_ingestion()

