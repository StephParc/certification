# ingest_ticketmaster.py
"""
Batch Event Ingestion Service for Ticketmaster.

This module extends the basic harvesting capabilities by providing 
orchestration for large-scale data extractions. It allows the system 
to query multiple time windows or geographical zones in a single 
execution, ensuring the Data Lake is populated with comprehensive 
future event data.

Key Features:
1. Targeted Windowing: Precision filtering using start/end date-times.
2. Automated Batching: Orchestrates multiple daily extractions (e.g., 15-day outlook).
3. Persistent Metadata: Attaches detailed provenance data to every S3 object.
"""
import os
import json
import requests
import time
from datetime import datetime, timedelta, timezone

from config.config import TICKETMASTER_CONSUMER_KEY
from utils.S3_utils import upload_file
from utils.logger_config import setup_logger, trace_action

logger_name = "E5 - API Ticketmaster"
logger = setup_logger(logger_name)

@trace_action(logger_name)
def fetch_and_upload(country_code, start_date, end_date, label, extraction_date):
    """
    Core extraction function for targeted API windows.

    Queries the Ticketmaster API for a specific time range and country, 
    collects all paginated results, and delivers the final JSON payload 
    to the 'zone-brutes' bucket on S3.

    Args:
        country_code (str): ISO code for the target country.
        start_date (datetime): Beginning of the search window (UTC).
        end_date (datetime): End of the search window (UTC).
        label (str): Human-readable label for logging purposes.
        extraction_date (datetime): The reference date for S3 folder partitioning.
    """
    api_key = TICKETMASTER_CONSUMER_KEY
    url = "https://app.ticketmaster.com/discovery/v2/events.json"

    start_str = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_str = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")

    all_events = []
    page = 0
    total_pages = 1

    while page < total_pages:
        params = {
            "apikey": api_key,
            "countryCode": country_code,
            "segmentName": "Music",
            "size": 200,
            "page": page,
            "startDateTime": start_str,
            "endDateTime": end_str,
            "sort": "date,asc"
        }

        # Appel
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
        logger.warning(f"Aucun événement trouvé pour {label}")
        return

    # Sauvegarde du gros fichier consolidé
    date_folder = extraction_date.strftime("%Y-%m-%d")
    file_date = start_date.strftime("%Y-%m-%d")
    filename = f"ticketmaster_{country_code}_{file_date}.json"
    local_path = f"/tmp/{filename}"

    with open(local_path, "w", encoding="utf-8") as f:
        json.dump({"events": all_events, "metadata": {
                    "total": len(all_events), 
                    "country": country_code,
                    "extract_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "window_start": start_str,
                    "window_end": end_str}
                    }, f, ensure_ascii=False, indent=4)

    # Upload vers Garage S3
    s3_dest_path = f"E5/ticketmaster/{date_folder}/{filename}"
    if upload_file(
        local_path=local_path, 
        bucket="zone-brutes", 
        s3_path=s3_dest_path, 
        metadata={
            "source": "Ticketmaster_API",
            "step": "bronze",
            "destination": "ticketmaster.raw.ticketmaster_events"
        }):
        logger.info(f"Ingestion terminée{label} : {len(all_events)} événements dans s3://zone-brutes/{s3_dest_path}")
        os.remove(local_path)

@trace_action(logger_name)
def ingest_all_ticketmaster():
    """
    Orchestrator for multi-day batch ingestion.

    Specifically configured here to fetch 15 consecutive days of musical 
    events for the US market, simulating a 'catch-up' or 'bulk load' 
    scenario.
    """
    extraction_date = datetime.now()

    # --- 1. ÉTATS-UNIS (US) : Un fichier par jour pour les 15 prochains jours ---
    logger.info("Lancement extraction USA (Journalière)")
    base_date_us = datetime.now(timezone.utc) + timedelta(days=223)
    for i in range(15):
        # On définit les heures pour couvrir la journée complète
        start_us = (base_date_us + timedelta(days=i)).replace(hour=0, minute=0, second=0)
        end_us = start_us.replace(hour=23, minute=59, second=59)       
        fetch_and_upload("US", start_us, end_us, f"USA Jour {i}", extraction_date)

    # --- 2. ALLEMAGNE (DE) : Dans 6 mois ---
    # logger.info("Lancement extraction Allemagne (Future +6m)")
    # start_de = datetime.now(timezone.utc) + timedelta(days=181)
    # end_de = start_de + timedelta(days=365)
    # fetch_and_upload("DE", start_de, end_de, "Allemagne", extraction_date)

    # # --- 3. FRANCE (FR) : On prend ce qu'on peut sur un an ---
    # logger.info("🚀 Lancement extraction France")
    # start_fr = datetime.now(timezone.utc) + timedelta(days=365)
    # end_fr = start_fr + timedelta(days=365)
    # fetch_and_upload("FR", start_fr, end_fr, "France Standard", extraction_date)

if __name__ == "__main__":
    ingest_all_ticketmaster()