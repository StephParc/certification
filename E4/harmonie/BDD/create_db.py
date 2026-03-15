# create_db.py
"""
HBM Database Management and Data Ingestion CLI.

This utility serves as the primary interface for database lifecycle 
management. It provides a command-line interface (CLI) to:
1. Initialize the relational database schema (SQLAlchemy Base).
2. Perform bulk ingestion of source data (Users, Events, Instruments).
3. Execute the Scrapy ETL process, including author enrichment via 
   external APIs and robust error/rejection handling.

Usage:
    python3 -m E4.harmonie.BDD.create_db [action] --file [path]
"""
import csv
import os
import sys
import argparse
from datetime import date, datetime
from pathlib import Path

from E4.harmonie.BDD.database import get_session_sql, sql_connect, get_engine
from E4.harmonie.BDD.crud import (
    create_event, create_part, create_auteur, 
    create_asso_auteur_partition, create_user_admin, create_instrument
)
from E4.harmonie.BDD.api_externe import get_api_externe
from E4.harmonie.BDD.models import Base
from config.config import REJET_IMPORT_PATH, REJET_AUTEURS_PATH
from utils.logger_config import setup_logger, trace_action
from utils.S3_utils import handle_path, upload_file
from utils.utils_functions import write_rejection_log

logger_name = "E4 - Insertion BDD"
logger = setup_logger(logger_name)

@trace_action(logger_name)
def main():
    """
    Main entry point for the Database CLI.
    Parses arguments and routes execution to the appropriate ingestion 
    or initialization logic.
    """
    parser = argparse.ArgumentParser(description="HBM Database CLI Manager")
    parser.add_argument(
        "action", 
        choices=["init", "import_users", "import_events", "import_instruments", "import_scrapy"],
        help="Action to execute on the database"
    )
    parser.add_argument(
        "--file", 
        type=str,
        help="Relative path or S3 URI of the file to import"
    )

    args = parser.parse_args()

    try:
        if args.action == "init":
            logger.info("--- Initializing SQL Schema ---")
            init_db()
            
        elif args.action == "import_users":
            if not args.file: raise ValueError()
            insert_users_to_db(args.file)
            
        elif args.action == "import_events":
            if not args.file: raise ValueError("--file flag is required for this action.")
            processed_path = handle_path(args.file)
            insert_event_to_db(processed_path)
            
        elif args.action == "import_instruments":
            if not args.file: raise ValueError("--file flag is required for this action.")
            insert_instruments_to_db(args.file)
            
        elif args.action == "import_scrapy":
            if not args.file: raise ValueError("--file flag is required for this action.")
            processed_path = handle_path(args.file)
            insert_scrapy_to_db(processed_path)

        logger.info(f"Success: Action '{args.action}' completed.")

    except Exception as e:
        logger.error(f"Execution error for '{args.action}': {e}", file=sys.stderr)
        sys.exit(1)

@trace_action(logger_name)
def init_db():
    try:
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")

@trace_action(logger_name)
def insert_event_to_db(file_path):
    """
    Insert musical events from a CSV file into the database.

    Args:
        file_path (str): Path to the processed event CSV.
    
    Notes:
        Expects date format '%d-%m-%Y' in the source file.
    """
    SessionLocal= sql_connect()
    session = SessionLocal()
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                date_evenement = datetime.strptime(row.get('date_event'), "%d-%m-%Y").date()
                nom_evenement = row.get('nom_event')
                lieu = row.get('lieu')
                type_evenement = row.get('type_event')
                affiche = row.get('affiche')
                create_event(
                    session, 
                    date_evenement=date_evenement, 
                    nom_evenement=nom_evenement, 
                    lieu=lieu, 
                    type_evenement=type_evenement, 
                    affiche=affiche
                )    
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Event import error: {e}")
    finally:
        session.close()

@trace_action(logger_name)
def insert_scrapy_to_db(file_path):
    """
    Complex ETL process for scraped musical works.

    Performs data cleaning, creates partition records, and automatically 
    manages authorship relationships (composers, artists, arrangers). 
    Implements a rejection strategy where failed records are logged 
    locally and then synchronized back to S3 for governance.

    Args:
        file_path (str): Local path to the scraped data CSV.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    current_rejet_file = REJET_IMPORT_PATH.with_name(f"{timestamp}_{REJET_IMPORT_PATH.name}")
    current_rejet_auteurs = REJET_AUTEURS_PATH.with_name(f"{REJET_AUTEURS_PATH.name}")

    SessionLocal= sql_connect()
    session = SessionLocal()
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            count_ok = 0
            count_err = 0

            for row in csv_reader:
                etape = "Initialization"
                try:
                    etape = "Data Parsing"
                    # Extraction logic (Title uppercase, level float conversion)
                    titre=row.get('titre').upper() if row.get('titre') else None
                    sous_titre=row.get('sous_titre')
                    edition=row.get('edition')
                    collection=row.get('collection')
                    instrumentation=row.get('instrumentation')
                    niveau=float(row['niveau']) if row.get('niveau') else None
                    genre=row.get('genre')
                    style=row.get('style')
                    annee_sortie=int(row['annee_sortie']) if row.get('annee_sortie') else None
                    ISMN=row.get('ISMN')
                    ref_editeur=row.get('ref_editeur')
                    duree=row.get('duree')
                    description=row.get('description')
                    url=row.get('url')

                    etape = "Creating Partition"
                    part = create_part(
                        session, titre=titre,sous_titre=sous_titre, 
                        edition=edition, collection=collection,
                        instrumentation=instrumentation, niveau=niveau,
                        genre=genre, style=style, 
                        annee_sortie=annee_sortie, ISMN=ISMN,
                        ref_editeur=ref_editeur, duree=duree, 
                        description=description, url=url)
                    part_id = part.partition_id

                    # Author Role Mapping & Association
                    mapping_auteurs = {
                        'compositeur': row.get('compositeur', '').split(","),
                        'artiste': row.get('artiste', '').split(","),
                        'arrangeur': row.get('arrangeur', '').split(",")
                    }

                    for role, noms in mapping_auteurs.items():
                        etape = f"Traitement {role}"
                        for nom_brut in noms:
                            nom_brut = nom_brut.strip()
                            if not nom_brut:
                                continue
                            
                            etape = f"Traitement {role}: {nom_brut}"
                            auteur = create_auteur(session, nom=nom_brut)
                            
                            # Association
                            etape = f"Association {role}: {nom_brut}"
                            create_asso_auteur_partition(session, part_id, auteur.auteur_id, role)
                    
                    session.commit()
                    count_ok += 1

                except Exception as e:
                    session.rollback()
                    count_err += 1
                    error_detail = f"[{etape}] - {str(e)}"

                    headers = list(row.keys()) + ["erreur_import"]
                    row_data = list(row.values()) + [error_detail]
                    write_rejection_log(str(current_rejet_file), headers, row_data)
                    logger.warning(f"Ligne rejetée vers {current_rejet_file.name}")
            
            if count_err > 0:
                logger.warning(f"Exportation du log de rejet vers S3")
                s3_rejet_path = f"rejets/E4/import_global/{current_rejet_file.name}"
                upload_file(str(current_rejet_file), "zone_maintenance", s3_rejet_path)
                logger.info(f"Rejects uploaded to S3: zone_maintenance/{s3_rejet_path}")

            if current_rejet_auteurs.exists():
                logger.warning(f"Exportation du log rejets auteurs vers S3")
                s3_rejet_auteurs = f"rejets/E4/musicbrainz/{current_rejet_auteurs.name}"
                upload_file(str(current_rejet_auteurs), "zone-maintenance", s3_rejet_auteurs)
                logger.info(f"Rejects uploaded to S3: zone_maintenance/{s3_rejet_auteurs}")
            logger.info(f"Import finished. Success: {count_ok}, Errors: {count_err}")
    
    except Exception as e:
        logger.error(f"Error opening file: {e}")
    finally:
        session.close()  
    
@trace_action(logger_name)
def insert_users_to_db(file_path):
    """Insert seed users into the relational database."""
    SessionLocal= sql_connect()
    session = SessionLocal()
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                pseudo = row.get('pseudo')
                fullname = row.get('fullname')
                hashed_password = row.get('hashed_password')
                email = row.get('email')
                permissions = row.get('permissions')
                create_user_admin(
                    session, pseudo=pseudo, password=password,
                    fullname=fullname, email=email, permissions=permissions
                )    
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"User import error: {e}")
    finally:
        session.close()

@trace_action(logger_name)
def insert_instruments_to_db(file_path):
    """Populates the instrument SQL table from CSV."""
    SessionLocal = sql_connect()
    session = SessionLocal()
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                nom = row.get('nom').strip()
                famille = row.get('famille').strip()
                sous_famille = row.get('sous_famille').strip()
                create_instrument(session, nom=nom,famille=famille,sous_famille=sous_famille)
                    
        session.commit()
        logger.info(f"Instruments imported successfully (nom/famille/sous_famille)")
    except Exception as e:
        session.rollback()
        logger.error(f"Instrument import error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    main()
